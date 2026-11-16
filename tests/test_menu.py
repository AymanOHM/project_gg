import json
import os
from collections import defaultdict

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg  # noqa: E402

from gg_client.keyboard import KEYMAP, read_inputs  # noqa: E402
from gg_client.menu import LEAVE, PLAY, QUIT, RESUME, Menu, draw_menu  # noqa: E402
from gg_client.settings import Settings  # noqa: E402
from gg_core import PlayerInput  # noqa: E402

pg.init()


def press(menu, *keys):
    result = None
    for key in keys:
        result = menu.handle_key(key)
    return result


def test_main_menu_plays_and_quits():
    assert press(Menu(Settings()), pg.K_RETURN) == PLAY
    assert press(Menu(Settings()), pg.K_DOWN, pg.K_DOWN, pg.K_RETURN) == QUIT
    assert press(Menu(Settings()), pg.K_ESCAPE) == QUIT


def test_selection_wraps_around():
    menu = Menu(Settings())
    press(menu, pg.K_UP)
    assert menu.items()[menu.index][0] == "quit"
    press(menu, pg.K_DOWN)
    assert menu.items()[menu.index][0] == "play"


def test_options_change_volume_within_limits_and_toggle_fullscreen():
    settings = Settings(music_volume=1)
    menu = Menu(settings)
    press(menu, pg.K_DOWN, pg.K_RETURN)  # OPTIONS
    assert menu.screen == "options"
    press(menu, pg.K_LEFT, pg.K_LEFT, pg.K_LEFT)
    assert settings.music_volume == 0 and menu.changed
    press(menu, pg.K_DOWN, pg.K_RIGHT)
    assert settings.effects_volume == 10  # already at the top
    press(menu, pg.K_DOWN, pg.K_RETURN)
    assert settings.fullscreen is True
    assert press(menu, pg.K_ESCAPE) is None and menu.screen == "main"


def test_rebinding_a_key_changes_what_the_game_reads():
    settings = Settings()
    menu = Menu(settings)
    press(menu, pg.K_DOWN, pg.K_RETURN, pg.K_DOWN, pg.K_DOWN, pg.K_DOWN, pg.K_RETURN)  # CONTROLS
    assert menu.screen == "controls"
    press(menu, pg.K_DOWN, pg.K_DOWN)  # P1 JUMP
    assert menu.items()[menu.index][0] == "bind:p1:jump"
    press(menu, pg.K_RETURN)
    assert menu.waiting_for_key and menu.title() == "PRESS A KEY"
    press(menu, pg.K_k)  # any key, including ones that normally move the cursor
    assert not menu.waiting_for_key
    assert settings.keymap["p1"]["jump"] == [pg.K_k]

    pressed = defaultdict(bool, {pg.K_k: True, pg.K_w: True})  # W is no longer jump
    assert read_inputs(pressed, settings.keymap)["p1"] == PlayerInput(jump=True)


def test_escape_cancels_a_rebind_and_reset_restores_defaults():
    settings = Settings()
    menu = Menu(settings)
    press(menu, pg.K_DOWN, pg.K_RETURN, pg.K_DOWN, pg.K_DOWN, pg.K_DOWN, pg.K_RETURN)
    press(menu, pg.K_RETURN, pg.K_ESCAPE)
    assert settings.keymap["p1"]["left"] == list(KEYMAP["p1"]["left"])
    press(menu, pg.K_RETURN, pg.K_j)
    assert settings.keymap["p1"]["left"] == [pg.K_j]
    press(menu, pg.K_UP, pg.K_UP, pg.K_RETURN)  # up from the first line: BACK, then RESET
    assert settings.keymap["p1"]["left"] == list(KEYMAP["p1"]["left"])


def test_settings_survive_a_save_and_load(tmp_path):
    path = tmp_path / "nested" / "settings.json"
    settings = Settings(music_volume=2, effects_volume=7, fullscreen=True)
    settings.keymap["p2"]["fire"] = [pg.K_m]
    settings.save(path)
    assert json.loads(path.read_text())["keymap"]["p2"]["fire"] == ["m"]
    assert Settings.load(path) == settings


def test_bad_or_missing_settings_fall_back_to_defaults(tmp_path):
    assert Settings.load(tmp_path / "missing.json") == Settings()
    broken = tmp_path / "broken.json"
    broken.write_text("{nope")
    assert Settings.load(broken) == Settings()
    odd = {
        "music_volume": 99,
        "effects_volume": "loud",
        "fullscreen": 1,
        "keymap": {"p1": {"jump": ["no such key"]}},
    }
    assert Settings.from_dict(odd) == Settings()


def test_every_menu_screen_draws():
    screen = pg.Surface((1280, 720))
    menu = Menu(Settings())
    for keys in (
        [],
        [pg.K_DOWN, pg.K_RETURN],
        [pg.K_DOWN, pg.K_DOWN, pg.K_DOWN, pg.K_RETURN],
        [pg.K_RETURN],
        "pause",
    ):
        if keys == "pause":
            menu.open("pause")
        else:
            press(menu, *keys)
        screen.fill((72, 160, 211))
        draw_menu(screen, menu)
        white = sum(
            tuple(screen.get_at((x, y)))[:3] == (255, 255, 255)
            for x in range(0, 1280, 3)
            for y in range(0, 720, 3)
        )
        assert white > 300


def test_pause_menu_resumes_leaves_and_returns_from_options():
    menu = Menu(Settings())
    menu.open("pause")
    assert menu.title() == "PAUSED"
    assert press(menu, pg.K_RETURN) == RESUME
    assert press(menu, pg.K_ESCAPE) == RESUME

    press(menu, pg.K_DOWN, pg.K_RETURN)  # OPTIONS
    assert menu.screen == "options"
    press(menu, pg.K_ESCAPE)
    assert menu.screen == "pause"  # back to the pause menu, not the main menu

    assert press(menu, pg.K_DOWN, pg.K_DOWN, pg.K_RETURN) == LEAVE
    assert menu.screen == "main" and menu.index == 0
    press(menu, pg.K_DOWN, pg.K_RETURN, pg.K_ESCAPE)  # options and back, now from the main menu
    assert menu.screen == "main"
