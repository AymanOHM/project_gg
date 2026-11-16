"""Camera and the world-to-screen conversion shared by every renderer."""

import pygame as pg

CAMERA_SMOOTHING = 30  # v1: the camera closes 1/30 of the gap each frame
# Zooming out: the view grows until both players are this far inside its edges.
MARGIN_X = 250
MARGIN_Y = 200


class Camera:
    """Follows the midpoint between the players, easing towards it as v1 did.

    The world is Y-up with rectangles positioned at their bottom-left corner;
    pygame is Y-down with rectangles positioned at their top-left corner.

    `scale` is how many world pixels one screen pixel covers. It is 1 unless
    `max_scale` allows more, in which case the view widens when the players are
    far apart. `to_screen` then returns positions in the widened view
    (`view_size`), and the renderer shrinks that picture to fit the screen.
    """

    def __init__(self, screen_size: tuple[int, int], max_scale: float = 1.0):
        self.width, self.height = screen_size
        self.max_scale = max_scale
        self.scale = 1.0
        self.scroll = [0.0, 0.0]

    @property
    def view_size(self) -> tuple[int, int]:
        return round(self.width * self.scale), round(self.height * self.scale)

    def follow(self, players: list[dict]) -> None:
        xs = [p["x"] for p in players]
        ys = [p["y"] for p in players]
        wanted = max(
            1.0,
            (max(xs) - min(xs) + 2 * MARGIN_X) / self.width,
            (max(ys) - min(ys) + 2 * MARGIN_Y) / self.height,
        )
        self.scale += (min(wanted, self.max_scale) - self.scale) / CAMERA_SMOOTHING
        if self.scale < 1.001:  # close enough: draw straight to the screen again
            self.scale = 1.0

        view_w, view_h = self.view_size
        mid_x = sum(xs) / len(xs)
        mid_y = sum(ys) / len(ys)
        self.scroll[0] += (mid_x - view_w / 2 - self.scroll[0]) / CAMERA_SMOOTHING
        self.scroll[1] += (mid_y - view_h / 2 - self.scroll[1]) / CAMERA_SMOOTHING

    def to_screen(self, x: float, y: float, w: float, h: float) -> pg.Rect:
        view_h = self.view_size[1]
        return pg.Rect(x - self.scroll[0], view_h - (y - self.scroll[1]) - h, w, h)
