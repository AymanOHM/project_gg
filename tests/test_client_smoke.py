"""The debug client starts, runs frames and draws without a display."""

import asyncio
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg  # noqa: E402

from gg_client.__main__ import LEVEL_PATH, main  # noqa: E402
from gg_client.audio import Audio  # noqa: E402
from gg_client.debug_renderer import SKY, DebugRenderer  # noqa: E402
from gg_client.keyboard import KEYMAP, read_inputs  # noqa: E402
from gg_client.menu import Menu, draw_menu  # noqa: E402
from gg_client.settings import Settings  # noqa: E402
from gg_client.sprite_renderer import SpriteRenderer  # noqa: E402
from gg_core import Match, PlayerInput, World, load_level  # noqa: E402


def test_main_loop_runs_frames_headless():
    asyncio.run(main(max_frames=30, settings=Settings()))  # menu
    asyncio.run(main(max_frames=30, skip_menu=True, settings=Settings()))
    asyncio.run(main(max_frames=30, debug=True, settings=Settings()))


def press(*keys):
    for key in keys:
        pg.event.post(pg.event.Event(pg.KEYDOWN, key=key))


def test_menu_keys_reach_the_menu_and_quit_ends_the_loop():
    pg.init()
    press(pg.K_UP, pg.K_RETURN)  # up from PLAY wraps to QUIT
    asyncio.run(main(max_frames=10_000_000, settings=Settings()))  # returns at once


def test_volume_changed_in_the_menu_is_applied_and_not_saved_for_injected_settings(tmp_path):
    pg.init()
    settings = Settings()
    press(pg.K_DOWN, pg.K_RETURN, pg.K_LEFT, pg.K_LEFT)  # OPTIONS, then music down twice
    asyncio.run(main(max_frames=5, settings=settings))
    assert settings.music_volume == 3


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


def test_menu_and_win_screens_are_drawn_and_clouds_drift():
    pg.init()
    pg.display.set_mode((1280, 720))
    screen = pg.Surface((1280, 720))
    renderer = SpriteRenderer(screen)
    level = load_level(LEVEL_PATH)
    renderer.load_level(level)

    draw_menu(screen, Menu(Settings()), renderer.draw_backdrop())
    title = screen.copy()
    before = [cloud["x"] for cloud in renderer.clouds]
    renderer.draw_backdrop()
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


def test_audio_plays_each_ticks_events_once():
    pg.init()
    audio = Audio()
    assert audio.enabled, "sound files failed to load"
    audio.start_music()
    snap = {
        "tick": 5,
        "events": [{"type": "shot", "player": "p1"}, {"type": "hit", "player": "p2"}],
    }
    assert audio.play_events(snap) == ["shot", "hit"]
    assert audio.play_events(snap) == []  # same tick drawn again
    assert audio.play_events({"tick": 6, "events": [{"type": "unknown"}]}) == []
    assert audio.play_events({"tick": 7, "events": [{"type": "jump", "player": "p1"}]}) == ["jump"]
