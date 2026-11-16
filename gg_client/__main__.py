"""Local two-player game on one keyboard:  uv run python -m gg_client

Add --debug to draw plain rectangles (collision boxes) instead of sprites.

p1: A/D move, W jump, S fast fall, Space fire.
p2: arrows move/jump/fast fall, Right Shift or / fire (numpad 4/6/8/5/0 also work).
A match is best of three. Enter starts one from the welcome screen, and a new one
once a match is over. Esc or Q quits.

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
from .sprite_renderer import SpriteRenderer

LEVEL_PATH = Path(__file__).resolve().parent.parent / "data" / "levels" / "arena.json"


async def main(
    max_frames: int | None = None, debug: bool = False, skip_title: bool = False
) -> None:
    pg.init()
    screen = pg.display.set_mode((1280, 720))
    pg.display.set_caption("Project GG")
    frame_timer = pg.time.Clock()

    level = load_level(LEVEL_PATH)
    renderer = DebugRenderer(screen) if debug else SpriteRenderer(screen)
    renderer.load_level(level)
    # No match yet means the welcome screen is showing. The debug renderer has none.
    match = Match([level]) if debug or skip_title else None
    fixed = FixedStep()
    audio = Audio()
    audio.start_music()

    frames = 0
    while max_frames is None or frames < max_frames:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, pg.K_q):
                    pg.quit()
                    return
                if event.key == pg.K_RETURN and (match is None or match.phase == MATCH_OVER):
                    match = Match([level])

        steps = fixed.advance(frame_timer.tick(60) / 1000)
        if match is None:
            renderer.draw_title()
        else:
            inputs = read_inputs(pg.key.get_pressed())
            for _ in range(steps):
                match.step(inputs)
                audio.play_events(match.snapshot())
            renderer.draw(match.snapshot(), fixed.alpha)
        pg.display.flip()
        frames += 1
        await asyncio.sleep(0)
    pg.quit()


if __name__ == "__main__":
    args = sys.argv[1:]
    frames = next((int(a) for a in args if a.isdigit()), None)
    asyncio.run(main(frames, debug="--debug" in args, skip_title="--skip-title" in args))
