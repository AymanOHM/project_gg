"""A plain renderer: coloured rectangles, no sprites.

It exists so the rules can be played and checked by eye before the real renderer
(roadmap task 1.6) is built, and as a small worked example of the Renderer
protocol. It is not the base for 1.6.
"""

import pygame as pg

from gg_core import Level

SKY = (72, 160, 211)
TILE_COLOURS = {"grass": (70, 140, 60), "stone": (90, 90, 110)}
PLAYER_COLOURS = {"p1": (230, 230, 240), "p2": (40, 40, 50)}
BULLET_COLOUR = (250, 220, 60)
CAMERA_SMOOTHING = 30  # v1: the camera closes 1/30 of the gap each frame


class DebugRenderer:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.font = pg.font.Font(None, 28)
        self.level: Level | None = None
        self.scroll = [0.0, 0.0]

    def load_level(self, level: Level) -> None:
        self.level = level

    def draw(self, snapshot: dict, alpha: float = 0.0) -> None:
        screen, level = self.screen, self.level
        width, height = screen.get_size()
        players = snapshot["players"]

        # v1's camera: ease towards the midpoint between the players.
        mid_x = sum(p["x"] for p in players) / len(players)
        mid_y = sum(p["y"] for p in players) / len(players)
        self.scroll[0] += (mid_x - width / 2 - self.scroll[0]) / CAMERA_SMOOTHING
        self.scroll[1] += (mid_y - height / 2 - self.scroll[1]) / CAMERA_SMOOTHING

        def to_screen(x, y, w, h):
            """World rectangle (Y-up, bottom-left origin) to a pygame Rect (Y-down, top-left)."""
            return pg.Rect(x - self.scroll[0], height - (y - self.scroll[1]) - h, w, h)

        screen.fill(SKY)
        size = level.tile_size
        for tile in level.tiles:
            rect = to_screen(tile.x * size, tile.y * size, size, size)
            if rect.colliderect(screen.get_rect()):
                pg.draw.rect(screen, TILE_COLOURS.get(tile.type, (120, 100, 80)), rect)

        for p in players:
            body = to_screen(p["x"], p["y"], p["w"], p["h"])
            pg.draw.rect(screen, PLAYER_COLOURS.get(p["id"], (200, 0, 200)), body)
            eye_x = body.right - 10 if p["facing"] > 0 else body.left + 4
            pg.draw.rect(screen, (220, 60, 60), (eye_x, body.top + 10, 6, 6))
            bar = to_screen(p["x"] - 8, p["y"] + 60, 50 * max(0, p["health"]) / p["max_health"], 5)
            pg.draw.rect(screen, (200, 40, 40), bar)

        for b in snapshot["bullets"]:
            pg.draw.rect(screen, BULLET_COLOUR, to_screen(b["x"], b["y"], b["w"], b["h"]))

        lines = [f"tick {snapshot['tick']}"]
        lines += [f"{p['id']}  {p['action']:<10} hp {p['health']}" for p in players]
        match = snapshot.get("match")  # absent when drawing a bare World
        if match:
            score = "  ".join(f"{pid} {won}" for pid, won in match["scores"].items())
            lines.append(f"round {match['round']}   {score}   first to {match['rounds_to_win']}")
            if match["phase"] == "countdown":
                lines.append(f"Starts in {match['ticks_left'] // 60 + 1}")
            elif match["phase"] == "round_over":
                lines.append(f"Round to {snapshot['winner'] or 'nobody (draw)'}")
            elif match["phase"] == "match_over":
                lines.append(f"{match['winner']} wins the match. Enter = new match, Esc = quit")
        elif snapshot["phase"] == "round_over":
            lines.append(f"Round over: {snapshot['winner'] or 'draw'}")
        for i, line in enumerate(lines):
            screen.blit(self.font.render(line, True, (0, 0, 0)), (10, 10 + 24 * i))
