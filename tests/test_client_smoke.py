"""The debug client starts, runs frames and draws without a display."""

import asyncio
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg  # noqa: E402

from gg_client.__main__ import LEVEL_PATH, main  # noqa: E402
from gg_client.debug_renderer import SKY, DebugRenderer  # noqa: E402
from gg_client.keyboard import KEYMAP, read_inputs  # noqa: E402
from gg_core import Match, PlayerInput, World, load_level  # noqa: E402


def test_main_loop_runs_frames_headless():
    asyncio.run(main(max_frames=30))


def test_debug_renderer_draws_a_snapshot():
    pg.init()
    screen = pg.Surface((1280, 720))
    level = load_level(LEVEL_PATH)
    world = World(level)
    for _ in range(100):
        world.step({"p1": PlayerInput(fire=True)})
    renderer = DebugRenderer(screen)
    renderer.load_level(level)
    for _ in range(200):  # let the camera settle on the players
        renderer.draw(world.snapshot())
    colours = {
        tuple(screen.get_at((x, y)))[:3] for x in range(0, 1280, 8) for y in range(0, 720, 8)
    }
    assert SKY in colours and len(colours) >= 4  # sky, tiles and both players are visible


def test_keyboard_maps_keys_to_player_inputs():
    pressed = {key: False for keys in KEYMAP.values() for group in keys.values() for key in group}
    pressed[pg.K_a] = pressed[pg.K_SPACE] = pressed[pg.K_UP] = True
    inputs = read_inputs(pressed)
    assert inputs["p1"] == PlayerInput(left=True, fire=True)
    assert inputs["p2"] == PlayerInput(jump=True)


def test_debug_renderer_draws_every_match_phase():
    pg.init()
    renderer = DebugRenderer(pg.Surface((1280, 720)))
    level = load_level(LEVEL_PATH)
    renderer.load_level(level)
    match = Match([level], rounds_to_win=1, countdown_ticks=2, round_over_ticks=2)
    seen = set()
    for tick in range(2000):
        seen.add(match.phase)
        renderer.draw(match.snapshot())
        match.step({"p1": PlayerInput(left=tick > 100)})
    assert seen == {"countdown", "playing", "round_over", "match_over"}
