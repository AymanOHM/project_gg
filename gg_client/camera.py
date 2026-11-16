"""Camera and the world-to-screen conversion shared by every renderer."""

import pygame as pg

CAMERA_SMOOTHING = 30  # v1: the camera closes 1/30 of the gap each frame


class Camera:
    """Follows the midpoint between the players, easing towards it as v1 did.

    The world is Y-up with rectangles positioned at their bottom-left corner;
    pygame is Y-down with rectangles positioned at their top-left corner.
    """

    def __init__(self, screen_size: tuple[int, int]):
        self.width, self.height = screen_size
        self.scroll = [0.0, 0.0]

    def follow(self, players: list[dict]) -> None:
        mid_x = sum(p["x"] for p in players) / len(players)
        mid_y = sum(p["y"] for p in players) / len(players)
        self.scroll[0] += (mid_x - self.width / 2 - self.scroll[0]) / CAMERA_SMOOTHING
        self.scroll[1] += (mid_y - self.height / 2 - self.scroll[1]) / CAMERA_SMOOTHING

    def to_screen(self, x: float, y: float, w: float, h: float) -> pg.Rect:
        return pg.Rect(x - self.scroll[0], self.height - (y - self.scroll[1]) - h, w, h)
