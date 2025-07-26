import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_FILE = Path(__file__).resolve().parent.parent / 'svg' / 'epistemicHypershere.svg'
OUTPUT_JSON = Path(__file__).resolve().parent.parent / 'mnt' / 'data' / 'svg_colors.json'

NS = {
    'svg': 'http://www.w3.org/2000/svg',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
}

FILL_RE = re.compile(r'fill:(#[0-9a-fA-F]{3,6})')


def extract_colors(svg_path: Path) -> dict:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    color_map = {}
    for elem in root.iter():
        label = elem.attrib.get('{%s}label' % NS['inkscape'])
        if not label:
            continue
        if elem.tag.rsplit('}', 1)[-1] not in {'circle', 'ellipse', 'path'}:
            continue
        style = elem.attrib.get('style', '')
        m = FILL_RE.search(style)
        if m:
            color_map[label] = m.group(1)
    return color_map


def main():
    color_map = extract_colors(SVG_FILE)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(color_map, f, indent=2)
    print(f"Wrote {len(color_map)} colors to {OUTPUT_JSON}")


if __name__ == '__main__':
    main()
