"""World behaviour beyond the v1 traces: the Phase 1 gate and the public contract."""

import json
import subprocess
import sys
from pathlib import Path

from gg_core import (
    PHASE_PLAYING,
    PHASE_ROUND_OVER,
    SNAPSHOT_VERSION,
    PlayerInput,
    World,
    load_level,
)
from gg_core import constants as c
from gg_core.bots import RandomBot

ROOT = Path(__file__).resolve().parent.parent
ARENA = load_level(ROOT / "data/levels/arena.json")


def run_bots(seed, ticks):
    """Play `ticks` ticks with two random bots, starting a new round whenever one ends."""
    bots = {"p1": RandomBot(seed), "p2": RandomBot(seed + 1000)}
    world, rounds, snapshots = World(ARENA), 0, []
    for _ in range(ticks):
        world.step({pid: bot.next_input() for pid, bot in bots.items()})
        snapshots.append(world.snapshot())
        if world.phase == PHASE_ROUND_OVER:
            world, rounds = World(ARENA), rounds + 1
    return snapshots, rounds


def test_ten_thousand_headless_ticks():
    snapshots, rounds = run_bots(seed=7, ticks=10_000)
    assert len(snapshots) == 10_000
    assert rounds > 5
    for snap in snapshots:
        for p in snap["players"]:
            assert p["health"] <= c.MAX_HEALTH
            assert -c.MAX_FALL_SPEED <= p["vy"] <= c.JUMP_SPEED
            assert abs(p["vx"]) <= c.DASH_SPEED
            assert p["action"] in {"idle", "run", "jump", "wall_slide", "dash"}
        assert len(snap["bullets"]) <= 8
    assert any(e["type"] == "dash" for snap in snapshots for e in snap["events"])


def test_same_inputs_give_the_same_game():
    assert run_bots(seed=3, ticks=2_000) == run_bots(seed=3, ticks=2_000)
    assert run_bots(seed=3, ticks=2_000) != run_bots(seed=4, ticks=2_000)


def test_snapshot_is_versioned_plain_json():
    world = World(ARENA)
    for _ in range(120):
        world.step({"p1": PlayerInput(fire=True), "p2": PlayerInput(jump=True)})
    snap = world.snapshot()
    assert json.loads(json.dumps(snap)) == snap
    assert snap["v"] == SNAPSHOT_VERSION
    assert snap["tick"] == 120
    assert snap["phase"] == PHASE_PLAYING and snap["winner"] is None
    assert [p["id"] for p in snap["players"]] == ["p1", "p2"]
    assert isinstance(snap["events"], list)
    assert set(snap["players"][0]) == {
        "id", "x", "y", "w", "h", "vx", "vy", "facing",
        "action", "action_ticks", "health", "max_health",
    }  # fmt: skip
    assert snap["bullets"] and set(snap["bullets"][0]) == {"id", "owner", "x", "y", "w", "h", "dir"}
    assert snap["bullets"][0]["owner"] == "p1"


def test_missing_inputs_mean_nothing_is_held():
    a, b = World(ARENA), World(ARENA)
    for _ in range(100):
        a.step({})
        b.step({"p1": PlayerInput(), "p2": PlayerInput()})
    assert a.snapshot() == b.snapshot()


def test_step_does_nothing_after_the_round_is_over():
    world = World(ARENA)
    for tick in range(700):
        world.step({"p1": PlayerInput(left=tick > 90)})
    assert world.phase == PHASE_ROUND_OVER and world.winner == "p2"
    before = world.snapshot()
    world.step({"p2": PlayerInput(right=True, fire=True)})
    assert world.snapshot() == before


def test_both_players_out_on_the_same_tick_is_a_draw():
    level = load_level(ROOT / "data/levels/arena.json")
    world = World(level)
    for p in world.players.values():
        p.x, p.y = 5000, -290  # no ground anywhere near; both cross kill_y together
    while world.phase == PHASE_PLAYING:
        world.step({})
    assert world.winner is None


def test_two_bullets_from_one_player_both_advance_when_the_first_is_removed():
    """Task 1.7: v1 skipped the next bullet whenever one was removed mid-loop."""
    world = World(ARENA)
    for _ in range(90):
        world.step({})
    p1 = world.players["p1"]
    for _ in range(40):
        world.step({"p1": PlayerInput(fire=True)})
        mine = [b for b in world.bullets if b.owner == "p1"]
        if len(mine) == 2:
            break
    first, second = mine
    first.start_x = first.x - c.BULLET_RANGE - 1  # out of range: removed on the next tick
    x_before = second.x
    world.step({})
    assert [b.id for b in world.bullets if b.owner == p1.id] == [second.id]
    assert second.x == x_before + c.BULLET_SPEED * second.direction


def test_gg_core_imports_no_pygame_or_opengl():
    code = (
        "import sys, gg_core, gg_core.bots, gg_core.world\n"
        "bad = [m for m in sys.modules if m.split('.')[0] in ('pygame', 'OpenGL')]\n"
        "assert not bad, bad\n"
    )
    subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)


def test_snapshot_events_report_jumps_shots_and_hits_for_one_tick_each():
    world = World(ARENA)
    for _ in range(90):
        world.step({})
    assert world.snapshot()["events"] == []

    world.step({"p1": PlayerInput(jump=True)})
    assert world.snapshot()["events"] == [{"type": "jump", "player": "p1"}]
    world.step({"p1": PlayerInput(jump=True)})  # still held: no second jump
    assert world.snapshot()["events"] == []

    seen = []
    for _ in range(c.FIRE_COOLDOWN_TICKS - 1):
        world.step({"p2": PlayerInput(fire=True)})
        seen += world.snapshot()["events"]
    assert seen == [{"type": "shot", "player": "p2"}]


def test_a_hit_is_an_event_even_when_the_bullet_never_appears_in_a_snapshot():
    world = World(ARENA)
    p1, p2 = world.players["p1"], world.players["p2"]
    for _ in range(90):
        world.step({})
    p1.x, p1.y = p2.x - 60, p2.y  # point blank, facing right
    world.step({})  # the gun catches up with the new position
    events, bullets_seen = [], 0
    for _ in range(3):
        world.step({"p1": PlayerInput(fire=True)})
        events += world.snapshot()["events"]
        bullets_seen += len(world.snapshot()["bullets"])
    assert {"type": "shot", "player": "p1"} in events
    assert {"type": "hit", "player": "p2"} in events
    assert p2.health == c.MAX_HEALTH - c.BULLET_DAMAGE
    assert bullets_seen == 0
