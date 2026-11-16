"""Convert a v1 map file (the tutorial editor's format) to a gg_core level file.

    PYTHONPATH=. uv run python tools/convert_v1_map.py OLD_MAP.json \\
        data/levels/NAME.json --name NAME

v1 ignored the file's own tile_size (16) and hard-coded 45, and hard-coded the
spawn points in game.py; both are written into the level here. The "offgrid"
list is dropped: v1 multiplied those pixel positions by the tile size, which put
every offgrid tile far outside the playable area.
"""

import argparse
import json
from pathlib import Path

from gg_core.level import LEVEL_FORMAT, Level


def convert(data: dict, name: str) -> dict:
    tiles = [
        {"x": t["pos"][0], "y": t["pos"][1], "type": t["type"], "variant": t["variant"]}
        for t in data["tilemap"].values()
    ]
    tiles.sort(key=lambda t: (t["y"], t["x"]))
    return {
        "format": LEVEL_FORMAT,
        "name": name,
        "tile_size": 45,
        "kill_y": -300,
        "spawns": {"p1": [80, 600], "p2": [900, 600]},
        "tiles": tiles,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    level = convert(json.loads(args.source.read_text()), args.name)
    Level.from_dict(level)  # validate before writing
    lines = ",\n".join("    " + json.dumps(t) for t in level.pop("tiles"))
    head = json.dumps(level, indent=2)[:-2]
    args.target.write_text(f'{head},\n  "tiles": [\n{lines}\n  ]\n}}\n')
    print(f"wrote {args.target}")


if __name__ == "__main__":
    main()
