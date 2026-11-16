"""The game's renderer: v1's sprites drawn with pygame-ce.

Every image is loaded, scaled and mirrored once, in `__init__`. `draw` only blits.
"""

from pathlib import Path

import pygame as pg

from gg_core import Level

from .camera import Camera

IMAGES = Path(__file__).resolve().parent.parent / "data" / "images"
SKY = (72, 160, 211)

# v1 drew the WASD player (now p1) with the "player2" sprites and the numpad
# player (now p2) with the "player" sprites.
PLAYER_SPRITES = {"p1": "player2", "p2": "player"}
# Ticks each animation frame is shown (v1's img_dur).
FRAME_TICKS = {"idle": 6, "run": 4, "jump": 5, "wall_slide": 5}

GUN_SIZE = (15, 13)
GUN_OFFSET_RIGHT = (21, 15)  # from the player's bottom-left corner, facing right
GUN_OFFSET_LEFT = (0, 15)
HEALTH_BAR = {"dx": -8, "dy": 60, "w": 50, "h": 5}


def _load(path: Path, size: tuple[int, int]) -> pg.Surface:
    return pg.transform.scale(pg.image.load(path).convert_alpha(), size)


def _load_frames(folder: Path, size: tuple[int, int]) -> list[pg.Surface]:
    files = sorted(folder.glob("*.png"), key=lambda f: int(f.stem))
    return [_load(f, size) for f in files]


def _both_ways(image: pg.Surface) -> dict[int, pg.Surface]:
    """The image as drawn (facing right, 1) and mirrored (facing left, -1)."""
    return {1: image, -1: pg.transform.flip(image, True, False)}


class SpriteRenderer:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.camera = Camera(screen.get_size())
        self.font = pg.font.Font(None, 36)
        self.big_font = pg.font.Font(None, 160)
        self.level: Level | None = None
        self.tiles: dict[tuple[str, int], pg.Surface] = {}
        self.players: dict[tuple[str, str], list[dict[int, pg.Surface]]] = {}
        self._player_size: tuple[int, int] | None = None
        self.gun = _both_ways(_load(IMAGES / "_gun.png", GUN_SIZE))
        self._bullet_file = IMAGES / "bullet3.png"
        self.bullets: dict[tuple[int, int], dict[int, pg.Surface]] = {}
        self.health_colour = pg.image.load(IMAGES / "health_simple.png").get_at((0, 0))

    def load_level(self, level: Level) -> None:
        self.level = level
        size = (level.tile_size, level.tile_size)
        for tile in level.tiles:
            key = (tile.type, tile.variant)
            if key not in self.tiles:
                self.tiles[key] = _load(IMAGES / "tiles" / tile.type / f"{tile.variant}.png", size)

    def draw(self, snapshot: dict, alpha: float = 0.0) -> None:
        screen, camera = self.screen, self.camera
        camera.follow(snapshot["players"])
        screen.fill(SKY)
        self._draw_tiles()
        for p in snapshot["players"]:
            self._draw_player(p)
        for b in snapshot["bullets"]:
            rect = camera.to_screen(b["x"], b["y"], b["w"], b["h"])
            # The bullet image points left, so it is mirrored when flying right.
            screen.blit(self._bullet_images(b["w"], b["h"])[-b["dir"]], rect)
        self._draw_hud(snapshot)

    def _draw_tiles(self) -> None:
        size = self.level.tile_size
        visible = self.screen.get_rect()
        for tile in self.level.tiles:
            rect = self.camera.to_screen(tile.x * size, tile.y * size, size, size)
            if rect.colliderect(visible):
                self.screen.blit(self.tiles[(tile.type, tile.variant)], rect)

    def _draw_player(self, p: dict) -> None:
        frames = self._player_frames(p)
        frame = frames[(p["action_ticks"] // FRAME_TICKS[p["action"]]) % len(frames)]
        self.screen.blit(frame[p["facing"]], self.camera.to_screen(p["x"], p["y"], p["w"], p["h"]))

        dx, dy = GUN_OFFSET_RIGHT if p["facing"] > 0 else GUN_OFFSET_LEFT
        gun_rect = self.camera.to_screen(p["x"] + dx, p["y"] + dy, *GUN_SIZE)
        self.screen.blit(self.gun[p["facing"]], gun_rect)

        health = max(0, p["health"]) / p["max_health"]
        bar = self.camera.to_screen(
            p["x"] + HEALTH_BAR["dx"],
            p["y"] + HEALTH_BAR["dy"],
            HEALTH_BAR["w"] * health,
            HEALTH_BAR["h"],
        )
        pg.draw.rect(self.screen, self.health_colour, bar)

    def _player_frames(self, p: dict) -> list[dict[int, pg.Surface]]:
        """Animation frames for this player's current action, loaded on first use."""
        size = (p["w"], p["h"])
        if size != self._player_size:  # sizes come from the snapshot; reload if they ever change
            self.players.clear()
            self._player_size = size
        sprites = PLAYER_SPRITES.get(p["id"], "player")
        key = (sprites, p["action"])
        if key not in self.players:
            folder = IMAGES / "entities" / sprites / p["action"]
            self.players[key] = [_both_ways(f) for f in _load_frames(folder, size)]
        return self.players[key]

    def _bullet_images(self, w: int, h: int) -> dict[int, pg.Surface]:
        if (w, h) not in self.bullets:
            self.bullets[(w, h)] = _both_ways(_load(self._bullet_file, (w, h)))
        return self.bullets[(w, h)]

    def _draw_hud(self, snapshot: dict) -> None:
        match = snapshot.get("match")  # absent when drawing a bare World
        if not match:
            return
        width, height = self.screen.get_size()
        score = "   ".join(f"{pid.upper()}  {won}" for pid, won in match["scores"].items())
        self._text(self.font, f"Round {match['round']}      {score}", (width // 2, 30))
        if match["phase"] == "countdown":
            self._text(self.big_font, str(match["ticks_left"] // 60 + 1), (width // 2, height // 3))
        elif match["phase"] == "round_over":
            winner = snapshot["winner"]
            text = f"{winner.upper()} takes the round" if winner else "Draw"
            self._text(self.font, text, (width // 2, height // 3))
        elif match["phase"] == "match_over":
            text = f"{match['winner'].upper()} wins the match. Enter to play again"
            self._text(self.font, text, (width // 2, height // 3))

    def _text(self, font: pg.font.Font, text: str, center: tuple[int, int]) -> None:
        shadow = font.render(text, True, (20, 30, 50))
        self.screen.blit(shadow, shadow.get_rect(center=(center[0] + 2, center[1] + 2)))
        image = font.render(text, True, (255, 255, 255))
        self.screen.blit(image, image.get_rect(center=center))
