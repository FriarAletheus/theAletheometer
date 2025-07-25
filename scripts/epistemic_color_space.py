import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "mnt" / "data" / "svg_colors.json"


def load_colors(path: Path = DATA_PATH) -> dict:
    """Load label-to-color mappings extracted from the SVG."""
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    colors = load_colors()
    for label, hex_color in colors.items():
        print(f"{label}: {hex_color}")
