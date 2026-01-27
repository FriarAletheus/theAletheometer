from fastmcp import FastMCP
import os, json
from typing import Any, Dict

mcp = FastMCP("IChing")

ICHING_JSON = os.environ.get("ICHING_JSON", "/app/iching.json")

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

@mcp.tool()
def iching_lookup(hexagram: int) -> Dict[str, Any]:
    """
    Lookup semantic data for a specific hexagram by ID (1–64).
    """
    ensure_loaded()
    data = ICHING.get(hexagram) or {}
    return {"hexagram": hexagram, "data": data}

@mcp.tool()
def iching_cast() -> Dict[str, Any]:
    """
    Adapter wrapper around ichiRan.cast_impl().

    Returns a machine-actionable "flight plan" with:
      - cast_raw: [6–9] bottom→top
      - primary:  {id, name, lookup_required}
      - relating: {id, name, lookup_required}
      - changing_lines: [{position, value, label}]
      - signatures: {primary, relating}
      - method: string
    """
    import ichiRan
    return ichiRan.iching_cast()

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=3000,
        path="/mcp",
    )
