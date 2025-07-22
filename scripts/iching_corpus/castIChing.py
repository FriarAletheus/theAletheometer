import random
import json

# Load the hexagram data from iching.json
with open("/mnt/data/iching.json", "r", encoding="utf-8") as f:
    hexagrams = json.load(f)["hexagrams"]

# Define the IChingOracle class as in ichiRan.py
class IChingOracle:
    def __init__(self, hexagrams):
        self.hexagrams = hexagrams

    def fifty_stick_cast(self):
        def cast_line():
            choices = [6, 7, 8, 9]  # 6 = old yin, 7 = young yang, 8 = young yin, 9 = old yang
            weights = [1, 5, 7, 3]
            return random.choices(choices, weights=weights, k=1)[0]
        return [cast_line() for _ in range(6)]

    def lines_to_hexagram_number(self, lines):
        binary = ''.join(['1' if line % 2 == 1 else '0' for line in reversed(lines)])
        return int(binary, 2) + 1

    def cast(self):
        lines = self.fifty_stick_cast()
        hex_num = self.lines_to_hexagram_number(lines)
        hexagram = next((h for h in self.hexagrams if h["hexagram_number"] == hex_num), None)
        return {
            "cast_lines": lines,
            "hexagram_number": hex_num,
            "hexagram": hexagram
        }

# Create oracle instance and cast
oracle = IChingOracle(hexagrams)
result = oracle.cast()
result
