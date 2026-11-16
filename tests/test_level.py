import json
from pathlib import Path

import pytest

from gg_core import Level, LevelError, load_level

ROOT = Path(__file__).resolve().parent.parent


def valid():
    return {
        "format": 1,
        "name": "box",
        "tile_size": 45,
        "kill_y": -300,
        "spawns": {"p1": [0, 50], "p2": [90, 50]},
        "tiles": [
            {"x": 0, "y": 0, "type": "grass", "variant": 1},
            {"x": 1, "y": 0, "type": "stone", "variant": 0},
            {"x": 2, "y": 0, "type": "decor", "variant": 0},
        ],
    }


def test_arena_loads_and_matches_the_v1_map():
    level = load_level(ROOT / "data/levels/arena.json")
    v1 = json.loads((ROOT / "map.json").read_text())["tilemap"]
    assert level.tile_size == 45
    assert level.spawns == {"p1": (80, 600), "p2": (900, 600)}
    assert {(t.x, t.y, t.type, t.variant) for t in level.tiles} == {
        (t["pos"][0], t["pos"][1], t["type"], t["variant"]) for t in v1.values()
    }


def test_round_trips_through_dict():
    level = Level.from_dict(valid())
    assert Level.from_dict(json.loads(json.dumps(level.to_dict()))) == level


def test_only_grass_and_stone_are_solid():
    level = Level.from_dict(valid())
    assert level.is_solid(0, 0) and level.is_solid(1, 0)
    assert not level.is_solid(2, 0)
    assert not level.is_solid(5, 5)


def test_solid_tiles_around_returns_pixel_corners_of_neighbours():
    level = Level.from_dict(valid())
    assert sorted(level.solid_tiles_around(50, 50)) == [(0, 0), (45, 0)]
    assert level.solid_tiles_around(500, 500) == []
    assert level.solid_tiles_around(-1, -1) == [(0, 0)]  # negative coordinates floor, not truncate


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda d: d.update(format=2), "unsupported level format"),
        (lambda d: d.pop("format"), "unsupported level format"),
        (lambda d: d.update(name=""), "'name'"),
        (lambda d: d.update(tile_size=0), "'tile_size'"),
        (lambda d: d.update(tile_size=45.5), "'tile_size'"),
        (lambda d: d.update(kill_y="low"), "'kill_y'"),
        (lambda d: d.update(spawns={"p1": [0, 0]}), "at least two"),
        (lambda d: d["spawns"].update(p2=[1]), "spawn 'p2'"),
        (lambda d: d["spawns"].update(p2=[0, -500]), "below kill_y"),
        (lambda d: d.update(tiles=[]), "'tiles'"),
        (lambda d: d["tiles"].append({"x": 0.5, "y": 0, "type": "grass"}), "integer 'x' and 'y'"),
        (lambda d: d["tiles"].append({"x": 9, "y": 0}), "'type'"),
        (
            lambda d: d["tiles"].append({"x": 9, "y": 0, "type": "grass", "variant": -1}),
            "'variant'",
        ),
        (lambda d: d["tiles"].append({"x": 0, "y": 0, "type": "stone"}), "duplicates"),
    ],
)
def test_invalid_levels_are_rejected(change, message):
    data = valid()
    change(data)
    with pytest.raises(LevelError, match=message):
        Level.from_dict(data)


def test_load_level_reports_bad_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json")
    with pytest.raises(LevelError, match="not valid JSON"):
        load_level(path)


@pytest.mark.parametrize("name", ["arena", "meadow", "cliffs", "towers"])
def test_shipped_levels_load_and_both_players_land_on_solid_ground(name):
    from gg_core import PHASE_PLAYING, World

    level = load_level(ROOT / "data" / "levels" / f"{name}.json")
    assert level.name == name
    world = World(level)
    for _ in range(200):
        world.step({})
    assert world.phase == PHASE_PLAYING
    for player in world.players.values():
        assert player.hit_down, f"{player.id} is not standing in {name}"
        spawn_x = level.spawns[player.id][0]
        assert abs(player.x - spawn_x) < level.tile_size, (
            f"{player.id} was pushed sideways in {name}"
        )
    xs = [p.x for p in world.players.values()]
    assert abs(xs[0] - xs[1]) >= 10 * level.tile_size
