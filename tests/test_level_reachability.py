"""Every shipped level can be crossed: each player can get to where the other starts.

This is a search, not a script. It tries button presses with the real `World`
physics, always extending the attempt that is closest to the goal, until one
arrives. A pass is a proof, because the route was actually walked. A failure
is only a warning: the search groups nearby positions together to stay fast,
so it can miss a route a person would find.
"""

import copy
import heapq
from pathlib import Path

import pytest

from gg_core import PHASE_PLAYING, Level, PlayerInput, World, load_level

LEVELS = Path(__file__).resolve().parent.parent / "data" / "levels"

HOLD_TICKS = 5  # each move is held this long; a jump or dash is pressed on its first tick
MOVES = [
    {},
    {"left": True},
    {"right": True},
    {"jump": True},
    {"left": True, "jump": True},
    {"right": True, "jump": True},
    {"left": True, "dash": True},
    {"right": True, "dash": True},
]
CELL = 15  # positions within the same 15 px square count as the same place


def can_reach(level, mover, use_dash, max_states):
    """True if `mover` can get within a tile of the other player's resting place."""
    world = World(level)
    for _ in range(200):  # both players settle on the ground
        world.step({})
    other = next(pid for pid in world.players if pid != mover)
    goal_x, goal_y = world.players[other].x, world.players[other].y

    def distance(p):
        return abs(p.x - goal_x) + abs(p.y - goal_y)

    def place(p, tick):
        rising = (p.vy > 0.5) - (p.vy < -0.5)
        return (p.x // CELL, p.y // CELL, rising, p.air_jump_ready, tick >= p.dash_ready_tick)

    start = copy.copy(world.players[mover])
    seen = {place(start, world.tick)}
    queue = [(distance(start), 0, start, world.tick)]  # closest to the goal first
    while queue and len(seen) < max_states:
        _, _, player, tick = heapq.heappop(queue)
        if abs(player.x - goal_x) < level.tile_size and abs(player.y - goal_y) < level.tile_size:
            return True
        for move in MOVES:
            if move.get("dash") and not use_dash:
                continue
            # Put the world back to the state being extended, then play the move.
            after = copy.copy(player)
            world.players[mover], world.tick, world.phase = after, tick, PHASE_PLAYING
            held = {k: v for k, v in move.items() if k in ("left", "right")}
            world.step({mover: PlayerInput(**move)})
            for _ in range(HOLD_TICKS - 1):
                world.step({mover: PlayerInput(**held)})
            if after.y < level.kill_y or place(after, world.tick) in seen:
                continue
            seen.add(place(after, world.tick))
            heapq.heappush(queue, (distance(after), len(seen), after, world.tick))
    return False


@pytest.mark.parametrize("mover", ["p1", "p2"])
@pytest.mark.parametrize("path", sorted(LEVELS.glob("*.json")), ids=lambda p: p.stem)
def test_each_player_can_reach_the_other(path, mover):
    level = load_level(path)
    # A short search with the dash finds most routes; the longer one without it
    # covers the levels where dashing first leads the search astray.
    assert can_reach(level, mover, use_dash=True, max_states=3_000) or can_reach(
        level, mover, use_dash=False, max_states=20_000
    ), f"no route found for {mover} on {level.name}"


def test_the_search_reports_a_level_that_cannot_be_crossed():
    """Two sealed rooms with a wall between them: the search must give up, not pass."""
    floor = [{"x": x, "y": 0, "type": "grass", "variant": 0} for x in range(21)]
    walls = [
        {"x": x, "y": y, "type": "stone", "variant": 0} for x in (-1, 10, 21) for y in range(1, 60)
    ]
    roof = [{"x": x, "y": 59, "type": "stone", "variant": 0} for x in range(21) if x != 10]
    level = Level.from_dict(
        {
            "format": 1,
            "name": "sealed",
            "tile_size": 45,
            "spawns": {"p1": [3 * 45, 45], "p2": [16 * 45, 45]},
            "tiles": floor + walls + roof,
        }
    )
    assert not can_reach(level, "p1", use_dash=True, max_states=3_000)
