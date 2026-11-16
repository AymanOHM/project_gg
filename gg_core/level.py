"""Level format (version 1) and loader.

A level is a JSON object:

    {
      "format": 1,
      "name": "arena",
      "tile_size": 45,
      "kill_y": -300,
      "spawns": {"p1": [80, 600], "p2": [900, 600]},
      "tiles": [{"x": 7, "y": 12, "type": "grass", "variant": 1}, ...]
    }

Tile x/y are grid coordinates; the tile covers tile_size pixels from
(x * tile_size, y * tile_size). The world is Y-up. Spawns and kill_y are pixels.
Tiles whose type is in SOLID_TILE_TYPES block movement; others are decoration.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from .constants import DEFAULT_KILL_Y, SOLID_TILE_TYPES

LEVEL_FORMAT = 1

# Order matters: collisions are resolved tile by tile in this order, as in v1.
_NEIGHBOR_OFFSETS = ((-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1))


class LevelError(ValueError):
    """The level data is not a valid level."""


@dataclass(frozen=True, slots=True)
class Tile:
    x: int
    y: int
    type: str
    variant: int

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "type": self.type, "variant": self.variant}


@dataclass(frozen=True)
class Level:
    name: str
    tile_size: int
    spawns: dict[str, tuple[float, float]]
    tiles: tuple[Tile, ...]
    kill_y: float = DEFAULT_KILL_Y
    _solid: frozenset = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        solid = frozenset((t.x, t.y) for t in self.tiles if t.type in SOLID_TILE_TYPES)
        object.__setattr__(self, "_solid", solid)

    def is_solid(self, tile_x: int, tile_y: int) -> bool:
        return (tile_x, tile_y) in self._solid

    def solid_tiles_around(self, x: float, y: float) -> list[tuple[int, int]]:
        """Pixel positions (left, bottom) of the solid tiles in the 3x3 block around a point."""
        size = self.tile_size
        cx, cy = int(x // size), int(y // size)
        return [
            ((cx + dx) * size, (cy + dy) * size)
            for dx, dy in _NEIGHBOR_OFFSETS
            if (cx + dx, cy + dy) in self._solid
        ]

    def to_dict(self) -> dict:
        return {
            "format": LEVEL_FORMAT,
            "name": self.name,
            "tile_size": self.tile_size,
            "kill_y": self.kill_y,
            "spawns": {pid: list(pos) for pid, pos in self.spawns.items()},
            "tiles": [t.to_dict() for t in self.tiles],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Level":
        """Validate a decoded JSON object and build a Level. Raises LevelError."""
        if not isinstance(data, dict):
            raise LevelError("level must be a JSON object")
        if data.get("format") != LEVEL_FORMAT:
            raise LevelError(
                f"unsupported level format {data.get('format')!r}; expected {LEVEL_FORMAT}"
            )
        name = data.get("name")
        if not isinstance(name, str) or not name:
            raise LevelError("'name' must be a non-empty string")
        tile_size = data.get("tile_size")
        if not _is_int(tile_size) or tile_size <= 0:
            raise LevelError("'tile_size' must be a positive integer")
        kill_y = data.get("kill_y", DEFAULT_KILL_Y)
        if not _is_number(kill_y):
            raise LevelError("'kill_y' must be a number")

        spawns_in = data.get("spawns")
        if not isinstance(spawns_in, dict) or len(spawns_in) < 2:
            raise LevelError("'spawns' must map at least two player ids to [x, y]")
        spawns = {}
        for pid, pos in spawns_in.items():
            if not (isinstance(pos, list) and len(pos) == 2 and all(_is_number(v) for v in pos)):
                raise LevelError(f"spawn {pid!r} must be [x, y] numbers")
            if pos[1] < kill_y:
                raise LevelError(f"spawn {pid!r} is below kill_y")
            spawns[pid] = (pos[0], pos[1])

        tiles_in = data.get("tiles")
        if not isinstance(tiles_in, list) or not tiles_in:
            raise LevelError("'tiles' must be a non-empty list")
        tiles, seen = [], set()
        for i, t in enumerate(tiles_in):
            if not isinstance(t, dict):
                raise LevelError(f"tiles[{i}] must be an object")
            x, y, kind, variant = t.get("x"), t.get("y"), t.get("type"), t.get("variant", 0)
            if not (_is_int(x) and _is_int(y)):
                raise LevelError(f"tiles[{i}] needs integer 'x' and 'y'")
            if not isinstance(kind, str) or not kind:
                raise LevelError(f"tiles[{i}] needs a 'type' string")
            if not _is_int(variant) or variant < 0:
                raise LevelError(f"tiles[{i}] 'variant' must be a non-negative integer")
            if (x, y) in seen:
                raise LevelError(f"tiles[{i}] duplicates the tile at ({x}, {y})")
            seen.add((x, y))
            tiles.append(Tile(x, y, kind, variant))
        return cls(name=name, tile_size=tile_size, spawns=spawns, tiles=tuple(tiles), kill_y=kill_y)


def load_level(path: str | Path) -> Level:
    """Read and validate a level file."""
    try:
        data = json.loads(Path(path).read_text())
    except json.JSONDecodeError as e:
        raise LevelError(f"{path}: not valid JSON ({e})") from e
    return Level.from_dict(data)


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
