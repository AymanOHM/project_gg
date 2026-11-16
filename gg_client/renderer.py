"""The contract between the game loop and whatever draws the game.

A renderer never sees a World. It gets the level once and then one snapshot dict
per frame, which is exactly what a network client receives from the server, so
the same renderer works for local play and online play. This module must not
import pygame: it is the interface, not an implementation.
"""

from typing import Protocol

from gg_core import Level


class Renderer(Protocol):
    def load_level(self, level: Level) -> None:
        """Prepare to draw `level`. Called once before the first `draw` of a round."""

    def draw(self, snapshot: dict, alpha: float = 0.0) -> None:
        """Draw one frame from a `World.snapshot()` dict.

        `alpha` (0..1) is how far the frame is between this tick and the next
        (`FixedStep.alpha`). A renderer may ignore it; one that interpolates keeps
        the previous snapshot itself. World coordinates are Y-up with positions at
        the bottom-left corner of each rectangle; converting to screen space is
        the renderer's job.
        """
