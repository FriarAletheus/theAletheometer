import os, json, random
from typing import Any, Dict, List

ICHING_JSON = os.environ.get("ICHING_JSON", "iching.json")

ICHING = None

def load_iching() -> Dict[int, Dict[str, Any]]:
    """Load iching.json and index by hexagram ID."""
    with open(ICHING_JSON, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Support the current file shape: {"hexagrams": [{...}, {...}]}
    if isinstance(raw, dict) and "hexagrams" in raw and isinstance(raw["hexagrams"], list):
        return {h["id"]: h for h in raw["hexagrams"] if "id" in h}

    # Fallback: already-indexed dict
    if isinstance(raw, dict):
        out = {}
        for k, v in raw.items():
            try:
                out[int(k)] = v
            except Exception:
                pass
        return out

    raise ValueError("Unsupported iching.json format")

def ensure_loaded():
    global ICHING
    if ICHING is None:
        ICHING = load_iching()

# Line mapping: traditional 50-stalk method
LINE_SIGNATURE_TO_ID = {
    "111111": 1,   "000000": 2,   "100010": 3,   "010001": 4,
    "111010": 5,   "010111": 6,   "010000": 7,   "000010": 8,
    "111011": 9,   "110111": 10,  "111000": 11,  "000111": 12,
    "101111": 13,  "111101": 14,  "001000": 15,  "000100": 16,
    "100110": 17,  "011001": 18,  "110000": 19,  "000011": 20,
    "100101": 21,  "101001": 22,  "000001": 23,  "100000": 24,
    "100111": 25,  "111001": 26,  "100001": 27,  "011110": 28,
    "010010": 29,  "101101": 30,  "001110": 31,  "011100": 32,
    "001111": 33,  "111100": 34,  "000101": 35,  "101000": 36,
    "101011": 37,  "110101": 38,  "001010": 39,  "010100": 40,
    "110001": 41,  "100011": 42,  "111110": 43,  "011111": 44,
    "000110": 45,  "011000": 46,  "010110": 47,  "011010": 48,
    "110010": 49,  "101001": 50,  "101011": 51,  "001101": 52,
    "101110": 53,  "011101": 54,  "010101": 55,  "101010": 56,
    "011011": 57,  "110110": 58,  "010011": 59,  "110010": 60,
    "110011": 61,  "001100": 62,  "110001": 63,  "001110": 64
}

def _yarrow_stalk_cast() -> int:
    """Simulate a single line cast using the 50-stalk yarrow method."""
    n = 49  # 50th stalk set aside

    for _ in range(3):
        # Randomly split into left and right
        left = random.randint(1, n - 1)
        right = n - left

        # Remove one from right (heaven)
        right -= 1

        # Calculate remainders (treat 0 as 4)
        r_left = left % 4 if left % 4 != 0 else 4
        r_right = right % 4 if right % 4 != 0 else 4

        # Remove r_left + r_right + 1 from n
        n -= (r_left + r_right + 1)

    # n must be one of {24, 28, 32, 36}
    if n == 36:
        return 6   # old yin (changing)
    if n == 32:
        return 7   # young yang (stable)
    if n == 28:
        return 8   # young yin (stable)
    if n == 24:
        return 9   # old yang (changing)

    # Defensive fallback (should never occur)
    return 8

def _lines_to_signature_primary(lines: List[int]) -> str:
    """Convert line values to primary signature (yin/yang before change)."""
    sig = ""
    for v in reversed(lines):  # ← REVERSE to read bottom-to-top
        if v in (7, 9):  # yang lines
            sig += "1"
        else:  # yin lines (6, 8)
            sig += "0"
    return sig

def _lines_to_signature_relating(lines: List[int]) -> str:
    """Convert line values to relating signature (yin/yang after change)."""
    sig = ""
    for v in reversed(lines):  # ← REVERSE to read bottom-to-top
        if v == 6:      # old yin → changes to yang
            sig += "1"
        elif v == 9:    # old yang → changes to yin
            sig += "0"
        elif v == 7:    # young yang → stays yang
            sig += "1"
        else:           # v == 8, young yin → stays yin
            sig += "0"
    return sig

def get_hex_name(hex_id: int) -> str:
    """Retrieve hexagram name by ID."""
    ensure_loaded()
    data = ICHING.get(hex_id, {})
    return data.get("name", f"Hexagram {hex_id}")

def iching_lookup(hexagram: int) -> Dict[str, Any]:
    """
    Lookup semantic data for a specific hexagram by ID (1–64).
    """
    ensure_loaded()
    data = ICHING.get(hexagram) or {}
    return {"hexagram": hexagram, "data": data}

def iching_cast() -> Dict[str, Any]:
    """
    Perform a cast using the traditional 50-stalk yarrow method.

    Returns a machine-actionable "flight plan":
      - cast_raw: [6–9] bottom→top
      - primary:  {id, name, lookup_required}
      - relating: {id, name, lookup_required}
      - changing_lines: [{position, value, label}]
      - signatures: {primary, relating} (for trace/debug)
      - method: string
    """
    # 1) Cast six lines using the yarrow method
    lines: List[int] = [_yarrow_stalk_cast() for _ in range(6)]

    # 2) Compute signatures bottom→top
    primary_sig = _lines_to_signature_primary(lines)
    relating_sig = _lines_to_signature_relating(lines)

    primary_id = LINE_SIGNATURE_TO_ID.get(primary_sig)
    relating_id = LINE_SIGNATURE_TO_ID.get(relating_sig)

    if primary_id is None or relating_id is None:
        return {
            "error": "Invalid line signature (signature map mismatch or bit-order mismatch)",
            "debug": {
                "cast_raw": lines,
                "primary_signature": primary_sig,
                "relating_signature": relating_sig,
            },
        }

    # 3) Changing lines: only 6 and 9 move
    changing_lines: List[Dict[str, Any]] = []
    for idx, v in enumerate(lines):
        if v in (6, 9):
            changing_lines.append(
                {
                    "position": idx + 1,           # 1 = bottom, 6 = top
                    "value": v,                    # 6 or 9
                    "label": "six" if v == 6 else "nine",
                }
            )

    # 4) Flight plan
    return {
        "cast_raw": lines,
        "primary": {
            "id": primary_id,
            "name": get_hex_name(primary_id),
            "lookup_required": True,
        },
        "relating": {
            "id": relating_id,
            "name": get_hex_name(relating_id),
            "lookup_required": True,
        },
        "changing_lines": changing_lines,
        "signatures": {
            "primary": primary_sig,
            "relating": relating_sig,
        },
        "method": "50 Stalk Yarrow (Classical)",
    }
