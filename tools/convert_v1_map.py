"""Convert an old map file (the tutorial editor's format) to a gg_core level file.

    PYTHONPATH=. uv run python tools/convert_v1_map.py OLD_MAP.json \\
        data/levels/NAME.json --name NAME [--y-down]

Two kinds of old map exist:

- The v1 game's own map (Y-up). v1 ignored the file's tile_size (16), hard-coded
  45 and hard-coded the spawn points in game.py; both are written into the level.
  Its "offgrid" list is dropped: v1 drew those tiles far outside the playable area.
- The tutorial's maps in data/maps (Y-down, positions in 16 px units). Pass
  --y-down: tile rows are mirrored so the map is the right way up in a Y-up
  world, and the spawn points come from the map's "spawners" markers (the
  player marker for p1, the enemy marker farthest from it for p2). Offgrid
  decoration is dropped because the level format only has grid tiles.
"""

import argparse
import json
from pathlib import Path

from gg_core.level import LEVEL_FORMAT, Level

TILE_SIZE = 45
OLD_UNIT = 16  # pixels per tile in the tutorial's maps
SPAWN_LIFT = 10  # start slightly above the marker so nobody spawns inside the floor
KILL_MARGIN = 300  # how far below the lowest tile a player has to fall to be out


def convert(data: dict, name: str, y_down: bool = False) -> dict:
    sign = -1 if y_down else 1
    tiles = [
        {"x": t["pos"][0], "y": sign * t["pos"][1], "type": t["type"], "variant": t["variant"]}
        for t in data["tilemap"].values()
    ]
    tiles.sort(key=lambda t: (t["y"], t["x"]))
    if y_down:
        spawns = _spawns_from_markers(data["offgrid"])
        kill_y = min(t["y"] for t in tiles) * TILE_SIZE - KILL_MARGIN
    else:
        spawns, kill_y = {"p1": [80, 600], "p2": [900, 600]}, -300
    return {
        "format": LEVEL_FORMAT,
        "name": name,
        "tile_size": TILE_SIZE,
        "kill_y": kill_y,
        "spawns": spawns,
        "tiles": tiles,
    }


def _spawns_from_markers(offgrid: list[dict]) -> dict[str, list[int]]:
    markers = [t for t in offgrid if t["type"] == "spawners"]
    player = next(t["pos"] for t in markers if t["variant"] == 0)
    others = [t["pos"] for t in markers if t["variant"] != 0]
    far = max(others, key=lambda pos: abs(pos[0] - player[0]))
    left, right = sorted((player, far), key=lambda pos: pos[0])

    def to_world(pos):
        scale = TILE_SIZE / OLD_UNIT
        return [round(pos[0] * scale), round(-(pos[1] + OLD_UNIT) * scale) + SPAWN_LIFT]

    return {"p1": to_world(left), "p2": to_world(right)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--y-down", action="store_true", help="the source is a tutorial map")
    args = parser.parse_args()
    level = convert(json.loads(args.source.read_text()), args.name, args.y_down)
    Level.from_dict(level)  # validate before writing
    lines = ",\n".join("    " + json.dumps(t) for t in level.pop("tiles"))
    head = json.dumps(level, indent=2)[:-2]
    args.target.write_text(f'{head},\n  "tiles": [\n{lines}\n  ]\n}}\n')
    print(f"wrote {args.target}: spawns {level['spawns']}, kill_y {level['kill_y']}")


if __name__ == "__main__":
    main()
