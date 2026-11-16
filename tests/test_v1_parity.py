"""gg_core must reproduce the traces recorded from the v1 game code, tick for tick.

The traces come from tools/record_v1_traces.py. A failure here means behaviour
drifted from the original game.
"""

import gzip
import json
from pathlib import Path

import pytest

from gg_core import PHASE_ROUND_OVER, PlayerInput, World, load_level

ROOT = Path(__file__).resolve().parent.parent
TRACES = json.loads(gzip.decompress((ROOT / "tests/golden/v1_traces.json.gz").read_bytes()))[
    "traces"
]
ARENA = load_level(ROOT / "data/levels/arena.json")


def player_state(world, pid):
    p = world.players[pid]
    bullets = [[b.x, b.y, b.direction] for b in world.bullets if b.owner == pid]
    return [
        p.x, p.y, p.vy, p.move_x, int(p.facing < 0), p.action, p.health,
        int(p.hit_left), int(p.hit_right), int(p.hit_up), int(p.hit_down), bullets,
    ]  # fmt: skip


@pytest.mark.parametrize("name", sorted(TRACES))
def test_matches_v1_trace(name):
    trace = TRACES[name]
    world = World(ARENA)
    for tick, (masks, expected) in enumerate(zip(trace["inputs"], trace["frames"], strict=True), 1):
        world.step({"p1": PlayerInput.from_bits(masks[0]), "p2": PlayerInput.from_bits(masks[1])})
        assert player_state(world, "p1") == expected[0], f"p1 diverged at tick {tick}"
        assert player_state(world, "p2") == expected[1], f"p2 diverged at tick {tick}"


def test_traces_cover_the_mechanics():
    """Guard against a re-recording that silently stops exercising something."""
    frames = [f for t in TRACES.values() for f in t["frames"]]
    states = [s for f in frames for s in f]
    assert {s[5] for s in states} == {"idle", "run", "jump", "wall_slide"}
    assert any(s[9] for s in states), "no head bump recorded"
    assert any(s[6] < 100 for s in states), "no bullet damage recorded"
    assert any(s[6] <= 0 for s in states), "no death by bullets recorded"
    assert any(s[1] < -300 for s in states), "no fall off the map recorded"
    assert sum(len(t["frames"]) for t in TRACES.values()) > 5000


@pytest.mark.parametrize(
    ("name", "winner"),
    [("firefight_p1_wins", "p1"), ("firefight_p2_wins", "p2"), ("walk_off_the_map_left", "p2")],
)
def test_round_ends_with_the_survivor_as_winner(name, winner):
    world = World(ARENA)
    for masks in TRACES[name]["inputs"]:
        world.step({"p1": PlayerInput.from_bits(masks[0]), "p2": PlayerInput.from_bits(masks[1])})
    assert world.phase == PHASE_ROUND_OVER
    assert world.winner == winner
