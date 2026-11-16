"""The debug client starts, runs frames and draws without a display."""

import asyncio
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg  # noqa: E402

from gg_client.__main__ import LEVEL_PATH, main  # noqa: E402
from gg_client.debug_renderer import SKY, DebugRenderer  # noqa: E402
from gg_client.keyboard import KEYMAP, read_inputs  # noqa: E402
from gg_client.sprite_renderer import SpriteRenderer  # noqa: E402
from gg_core import Match, PlayerInput, World, load_level  # noqa: E402


def test_main_loop_runs_frames_headless():
    asyncio.run(main(max_frames=30))  # welcome screen
    asyncio.run(main(max_frames=30, skip_title=True))
    asyncio.run(main(max_frames=30, debug=True))


def test_enter_starts_a_match_from_the_welcome_screen_and_q_quits():
    pg.init()
    pg.event.post(pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN))
    asyncio.run(main(max_frames=5))
    pg.init()
    pg.event.post(pg.event.Event(pg.KEYDOWN, key=pg.K_q))
    asyncio.run(main(max_frames=10_000_000))  # returns at once instead of running forever


def played_match(ticks=243):
    """p1 crosses the arena to p2's platform and opens fire; one bullet is in the air."""
    level = load_level(LEVEL_PATH)
    match = Match([level], countdown_ticks=100)
    for t in range(ticks):
        p1 = PlayerInput(right=t < 236, jump=t == 146, fire=t > 240)
        p2 = PlayerInput(left=t == 250, fire=t > 250)
        match.step({"p1": p1, "p2": p2})
    return level, match


def test_sprite_renderer_draws_players_tiles_and_bullets():
    pg.init()
    pg.display.set_mode((1280, 720))
    screen = pg.Surface((1280, 720))
    level, match = played_match()
    renderer = SpriteRenderer(screen)
    renderer.load_level(level)
    snap = match.snapshot()
    assert snap["bullets"]
    for _ in range(300):  # let the camera settle
        renderer.draw(snap)
    for thing in [*snap["players"], *snap["bullets"]]:
        rect = renderer.camera.to_screen(thing["x"], thing["y"], thing["w"], thing["h"])
        box = screen.subsurface(rect.clip(screen.get_rect()))
        colours = {
            tuple(box.get_at((x, y)))[:3]
            for x in range(box.get_width())
            for y in range(box.get_height())
        }
        assert len(colours) > 2, f"nothing drawn for {thing['id']}"


def test_sprite_renderer_loads_no_images_once_warm(monkeypatch):
    pg.init()
    pg.display.set_mode((1280, 720))
    level, match = played_match()
    renderer = SpriteRenderer(pg.Surface((1280, 720)))
    renderer.load_level(level)
    renderer.draw(match.snapshot())

    def fail(*args, **kwargs):
        raise AssertionError("image loaded or scaled during draw")

    monkeypatch.setattr(pg.image, "load", fail)
    monkeypatch.setattr(pg.transform, "scale", fail)
    for _ in range(50):
        renderer.draw(match.snapshot())


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


def test_title_and_win_screens_cover_the_view_and_clouds_drift():
    pg.init()
    pg.display.set_mode((1280, 720))
    screen = pg.Surface((1280, 720))
    renderer = SpriteRenderer(screen)
    level = load_level(LEVEL_PATH)
    renderer.load_level(level)

    renderer.draw_title()
    title = screen.copy()
    before = [cloud["x"] for cloud in renderer.clouds]
    renderer.draw_title()
    assert all(cloud["x"] > x for cloud, x in zip(renderer.clouds, before, strict=True))

    match = Match([level], rounds_to_win=1, countdown_ticks=1, round_over_ticks=1)
    for tick in range(2000):  # p1 walks off the map, so p2 wins
        match.step({"p1": PlayerInput(left=tick > 100)})
    assert match.snapshot()["match"]["winner"] == "p2"
    renderer.draw(match.snapshot())
    white = [
        (x, y)
        for x in range(0, 1280, 4)
        for y in range(0, 720, 4)
        if tuple(screen.get_at((x, y)))[:3] == (255, 255, 255)
    ]
    assert len(white) > 200, "the win screen's lettering is missing"
    assert pg.image.tobytes(screen, "RGB") != pg.image.tobytes(title, "RGB")
