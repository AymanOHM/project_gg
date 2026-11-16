"""Local two-player game on one keyboard:  uv run python -m gg_client

p1: A/D move, W jump, S fast fall, Space fire.
p2: arrows move/jump/fast fall, Right Shift or / fire (numpad 4/6/8/5/0 also work).
Enter starts a new round once one is over. Esc quits.

The loop is async with one `await` per frame, which is what pygbag needs to run
the same file in a browser.
"""

import asyncio
import sys
from pathlib import Path

import pygame as pg

from gg_core import PHASE_ROUND_OVER, FixedStep, World, load_level

from .debug_renderer import DebugRenderer
from .keyboard import read_inputs

LEVEL_PATH = Path(__file__).resolve().parent.parent / "data" / "levels" / "arena.json"


async def main(max_frames: int | None = None) -> None:
    pg.init()
    screen = pg.display.set_mode((1280, 720))
    pg.display.set_caption("Project GG")
    frame_timer = pg.time.Clock()

    level = load_level(LEVEL_PATH)
    renderer = DebugRenderer(screen)
    renderer.load_level(level)
    world = World(level)
    fixed = FixedStep()

    frames = 0
    while max_frames is None or frames < max_frames:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                return
            if (
                event.type == pg.KEYDOWN
                and event.key == pg.K_RETURN
                and world.phase == PHASE_ROUND_OVER
            ):
                world = World(level)

        inputs = read_inputs(pg.key.get_pressed())
        for _ in range(fixed.advance(frame_timer.tick(60) / 1000)):
            world.step(inputs)

        renderer.draw(world.snapshot(), fixed.alpha)
        pg.display.flip()
        frames += 1
        await asyncio.sleep(0)
    pg.quit()


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else None))
