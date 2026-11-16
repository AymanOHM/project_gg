"""Local two-player game on one keyboard:  uv run python -m gg_client

Options:
  --debug        draw plain rectangles (collision boxes) instead of sprites; no menu
  --skip-menu    start a match at once

Default keys (change them under Options > Controls):
  p1: A/D move, W jump, S fast fall, Space fire.
  p2: arrows move/jump/fast fall, Right Shift or / fire (numpad 4/6/8/5/0 also work).
A match is best of three. Esc leaves a match for the menu; Esc on the menu quits.

The loop is async with one `await` per frame, which is what pygbag needs to run
the same file in a browser.
"""

import asyncio
import sys
from pathlib import Path

import pygame as pg

from gg_core import MATCH_OVER, FixedStep, Match, load_level

from .audio import Audio
from .debug_renderer import DebugRenderer
from .keyboard import read_inputs
from .menu import PLAY, QUIT, Menu, draw_menu
from .settings import VOLUME_STEPS, Settings
from .sprite_renderer import SpriteRenderer

LEVELS_DIR = Path(__file__).resolve().parent.parent / "data" / "levels"
LEVEL_PATH = LEVELS_DIR / "arena.json"
LEVEL_ORDER = ("arena", "meadow", "cliffs", "towers")  # one per round, in this order
WINDOW_SIZE = (1280, 720)


def apply_settings(settings: Settings, audio: Audio) -> None:
    audio.set_volumes(settings.music_volume / VOLUME_STEPS, settings.effects_volume / VOLUME_STEPS)
    if settings.fullscreen != pg.display.is_fullscreen():
        try:
            pg.display.toggle_fullscreen()
        except pg.error:
            settings.fullscreen = pg.display.is_fullscreen()  # not possible here (e.g. no display)


async def main(
    max_frames: int | None = None,
    debug: bool = False,
    skip_menu: bool = False,
    settings: Settings | None = None,
) -> None:
    pg.init()
    # SCALED keeps the game at 1280x720 and lets SDL stretch it to the window or screen.
    screen = pg.display.set_mode(WINDOW_SIZE, pg.SCALED)
    pg.display.set_caption("Project GG")
    frame_timer = pg.time.Clock()

    levels = [load_level(LEVELS_DIR / f"{name}.json") for name in LEVEL_ORDER]
    by_name = {level.name: level for level in levels}
    renderer = DebugRenderer(screen) if debug else SpriteRenderer(screen)
    shown_level = None  # the level the renderer currently has loaded
    save = settings is None  # settings passed in (tests) are never written to disk
    settings = settings or Settings.load()
    menu = Menu(settings)
    audio = Audio()
    audio.start_music()
    apply_settings(settings, audio)
    # No match means the menu is showing. The debug renderer has no menu.
    match = Match(levels) if debug or skip_menu else None
    fixed = FixedStep()

    frames = 0
    running = True
    while running and (max_frames is None or frames < max_frames):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type != pg.KEYDOWN:
                continue
            elif match is None:
                action = menu.handle_key(event.key)
                if action == PLAY:
                    match = Match(levels)
                elif action == QUIT:
                    running = False
                if menu.changed:
                    apply_settings(settings, audio)
                    if save:
                        settings.save()
                    menu.changed = False
            elif event.key == pg.K_ESCAPE:
                match = None if not debug else match
                running = running and not debug
            elif event.key == pg.K_RETURN and match.phase == MATCH_OVER:
                match = Match(levels)

        steps = fixed.advance(frame_timer.tick(60) / 1000)
        if match is None:
            draw_menu(screen, menu, renderer.draw_backdrop())
        else:
            inputs = read_inputs(pg.key.get_pressed(), settings.keymap)
            for _ in range(steps):
                match.step(inputs)
                audio.play_events(match.snapshot())
            snapshot = match.snapshot()
            if snapshot["match"]["level"] != shown_level:  # a new round on another level
                shown_level = snapshot["match"]["level"]
                renderer.load_level(by_name[shown_level])
            renderer.draw(snapshot, fixed.alpha)
        pg.display.flip()
        frames += 1
        await asyncio.sleep(0)
    pg.quit()


if __name__ == "__main__":
    args = sys.argv[1:]
    frame_limit = next((int(a) for a in args if a.isdigit()), None)
    asyncio.run(main(frame_limit, debug="--debug" in args, skip_menu="--skip-menu" in args))
