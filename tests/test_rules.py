"""The rules stated in plain numbers, on a small level built here.

tests/test_v1_parity.py proves the port matches v1; these tests say what the
rules are. Expected values are computed from gg_core.constants.
"""

import pytest

from gg_core import PHASE_ROUND_OVER, Level, PlayerInput, World
from gg_core import constants as c

TILE = 45
FLOOR_TOP = TILE  # the floor is the row of tiles at y = 0
HOLD_NOTHING = PlayerInput()
JUMP = PlayerInput(jump=True)


def make_world(wall_at=None, p1_x=100, p2_x=700):
    """A flat floor, optionally with a tall wall at tile column `wall_at`."""
    tiles = [{"x": x, "y": 0, "type": "grass", "variant": 0} for x in range(-5, 40)]
    if wall_at is not None:
        tiles += [{"x": wall_at, "y": y, "type": "stone", "variant": 0} for y in range(1, 12)]
    level = Level.from_dict(
        {
            "format": 1,
            "name": "test",
            "tile_size": TILE,
            "spawns": {"p1": [p1_x, FLOOR_TOP], "p2": [p2_x, FLOOR_TOP]},
            "tiles": tiles,
        }
    )
    world = World(level)
    steps(world, 3)  # one tick of falling registers the floor contact
    assert world.players["p1"].hit_down and world.players["p2"].hit_down
    return world


def steps(world, n, p1=HOLD_NOTHING, p2=HOLD_NOTHING):
    for _ in range(n):
        world.step({"p1": p1, "p2": p2})


def tap(world, p1):
    """Press for one tick, then release for one tick."""
    steps(world, 1, p1)
    steps(world, 1)


def test_running_covers_run_speed_pixels_per_tick_and_stops_at_once():
    world = make_world()
    p = world.players["p1"]
    x = p.x
    steps(world, 10, PlayerInput(right=True))
    assert p.x == x + 10 * c.RUN_SPEED and p.action == "run" and p.facing == 1
    steps(world, 1)
    assert p.x == x + 10 * c.RUN_SPEED and p.action == "idle"


def test_ground_jump_peak_is_the_sum_of_the_rising_speeds():
    world = make_world()
    p = world.players["p1"]
    rising_ticks = round(c.JUMP_SPEED / c.GRAVITY)
    expected_peak = sum(c.JUMP_SPEED - i * c.GRAVITY for i in range(rising_ticks))
    steps(world, 1, JUMP)
    peak = p.y
    while not p.hit_down:
        steps(world, 1)
        peak = max(peak, p.y)
    assert peak - FLOOR_TOP == pytest.approx(expected_peak)
    assert p.y == FLOOR_TOP


def test_one_extra_jump_in_the_air_and_no_more():
    world = make_world()
    p = world.players["p1"]
    tap(world, JUMP)
    steps(world, 10)
    steps(world, 1, JUMP)  # second jump: allowed
    assert p.vy == pytest.approx(c.JUMP_SPEED - c.GRAVITY)
    steps(world, 10)
    vy_before = p.vy
    steps(world, 1, JUMP)  # third jump: ignored, gravity carries on
    assert p.vy == pytest.approx(vy_before - c.GRAVITY)


def test_holding_jump_does_not_jump_again_on_landing():
    world = make_world()
    p = world.players["p1"]
    steps(world, 200, JUMP)
    assert p.hit_down and p.y == FLOOR_TOP


def test_wall_jump_pushes_away_from_the_wall_and_restores_the_air_jump():
    world = make_world(wall_at=4)  # wall face at x = 180
    p = world.players["p1"]
    tap(world, JUMP)
    steps(world, 12, PlayerInput(right=True))  # drift into the wall while airborne
    while not p.hit_right:
        steps(world, 1, PlayerInput(right=True))
    assert p.x == 4 * TILE - c.PLAYER_WIDTH and not p.hit_down
    steps(world, 1, PlayerInput(right=True))  # release jump before pressing again
    x = p.x
    steps(world, 1, JUMP)
    assert p.x == x - c.RUN_SPEED
    assert p.vy == pytest.approx(c.JUMP_SPEED - c.GRAVITY)
    assert p.air_jump_ready


def test_sliding_down_a_wall_falls_at_half_gravity():
    world = make_world(wall_at=4)
    p = world.players["p1"]
    tap(world, JUMP)
    steps(world, 40, PlayerInput(right=True))  # past the top of the jump, pressed on the wall
    assert p.hit_right and p.vy < 0 and p.action == "wall_slide"
    vy = p.vy
    steps(world, 1, PlayerInput(right=True))
    assert p.vy == pytest.approx(vy - c.WALL_SLIDE_GRAVITY)


def ticks_to_land(fast_fall):
    world = make_world()
    p = world.players["p1"]
    steps(world, 1, JUMP)
    ticks = 0
    while not p.hit_down:
        steps(world, 1, PlayerInput(fast_fall=fast_fall))
        ticks += 1
    return ticks


def test_fast_fall_lands_sooner():
    assert ticks_to_land(fast_fall=True) < ticks_to_land(fast_fall=False)


def test_fall_speed_is_capped():
    world = make_world()
    p = world.players["p1"]
    p.x, p.y = 5000, 3000  # far from any floor
    steps(world, 200, PlayerInput(fast_fall=True))
    assert p.vy == -c.MAX_FALL_SPEED


def test_holding_fire_shoots_once_per_cooldown():
    world = make_world(p2_x=1500)  # p2 out of range
    start = world.tick
    shots = 0
    seen = set()
    for _ in range(4 * c.FIRE_COOLDOWN_TICKS):
        steps(world, 1, PlayerInput(fire=True))
        new = {b.id for b in world.bullets} - seen
        if new:
            shots += len(new)
            seen |= new
            assert (world.tick - start + 3) % c.FIRE_COOLDOWN_TICKS == 0
    assert shots == 4


def test_bullet_flies_at_bullet_speed_and_disappears_past_its_range():
    world = make_world(p2_x=1500)
    steps(world, c.FIRE_COOLDOWN_TICKS, PlayerInput(fire=True))
    (bullet,) = world.bullets
    x = bullet.x
    steps(world, 1)
    assert bullet.x == x + c.BULLET_SPEED
    travelled = 0
    while world.bullets:
        travelled = bullet.x - bullet.start_x
        steps(world, 1)
    assert c.BULLET_RANGE < travelled <= c.BULLET_RANGE + c.BULLET_SPEED


def test_bullet_is_stopped_by_a_wall():
    world = make_world(wall_at=8, p2_x=600)  # wall between the players
    steps(world, 60, PlayerInput(fire=True))
    assert world.players["p2"].health == c.MAX_HEALTH
    assert all(b.x < 8 * TILE for b in world.bullets)


def test_each_hit_takes_bullet_damage_and_enough_hits_end_the_round():
    world = make_world(p1_x=100, p2_x=400)
    p2 = world.players["p2"]
    hits_to_kill = c.MAX_HEALTH // c.BULLET_DAMAGE
    seen = []
    while world.phase != PHASE_ROUND_OVER:
        steps(world, 1, PlayerInput(fire=True))
        if not seen or seen[-1] != p2.health:
            seen.append(p2.health)
    assert seen == [c.MAX_HEALTH - i * c.BULLET_DAMAGE for i in range(hits_to_kill + 1)]
    assert world.winner == "p1"


def test_falling_below_kill_y_loses_the_round():
    world = make_world()
    world.players["p2"].x = 5000  # no floor there
    while world.phase != PHASE_ROUND_OVER:
        steps(world, 1)
    assert world.players["p2"].y < world.level.kill_y
    assert world.winner == "p1"


def test_players_do_not_block_each_other():
    world = make_world(p1_x=100, p2_x=160)
    p1 = world.players["p1"]
    steps(world, 30, PlayerInput(right=True))
    assert p1.x == 100 + 30 * c.RUN_SPEED
