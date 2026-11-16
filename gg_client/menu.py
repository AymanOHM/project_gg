"""Main menu, options and key bindings, drawn in the style of the welcome screen.

`Menu` holds only state and logic, so it can be tested without a window:
`handle_key` takes a pygame key code and returns what the game should do next.
`draw_menu` turns that state into pixels.
"""

import pygame as pg

from .settings import VOLUME_STEPS, Settings, default_keymap

PLAY, QUIT = "play", "quit"  # what handle_key can ask the game to do

BUTTON_LABELS = {
    "left": "LEFT",
    "right": "RIGHT",
    "jump": "JUMP",
    "fast_fall": "FAST FALL",
    "fire": "FIRE",
    "dash": "DASH",
}


class Menu:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.screen = "main"  # main | options | controls
        self.index = 0
        self.waiting_for_key = False  # True while a new key is being chosen for a binding
        self.changed = False  # set whenever a setting changes; the game applies and clears it

    # ------------------------------------------------------------------ items

    def items(self) -> list[tuple[str, str]]:
        """(id, text) for each line of the current screen."""
        s = self.settings
        if self.screen == "main":
            return [("play", "PLAY"), ("options", "OPTIONS"), ("quit", "QUIT")]
        if self.screen == "options":
            return [
                ("music", f"MUSIC  < {s.music_volume} >"),
                ("effects", f"EFFECTS  < {s.effects_volume} >"),
                ("fullscreen", f"FULLSCREEN  {'ON' if s.fullscreen else 'OFF'}"),
                ("controls", "CONTROLS"),
                ("back", "BACK"),
            ]
        lines = []
        for pid, buttons in s.keymap.items():
            for button, keys in buttons.items():
                names = " / ".join(pg.key.name(k).upper() for k in keys)
                lines.append(
                    (f"bind:{pid}:{button}", f"{pid.upper()} {BUTTON_LABELS[button]}  {names}")
                )
        return [*lines, ("reset", "RESET TO DEFAULTS"), ("back", "BACK")]

    def title(self) -> str:
        if self.waiting_for_key:
            return "PRESS A KEY"
        return {"main": "PROJECT GG", "options": "OPTIONS", "controls": "CONTROLS"}[self.screen]

    # ------------------------------------------------------------------ input

    def handle_key(self, key: int) -> str | None:
        """React to one key press. Returns PLAY, QUIT or None."""
        items = self.items()
        item = items[self.index][0]

        if self.waiting_for_key:
            if key != pg.K_ESCAPE:  # Esc cancels
                _, pid, button = item.split(":")
                self.settings.keymap[pid][button] = [key]
                self.changed = True
            self.waiting_for_key = False
            return None

        if key in (pg.K_UP, pg.K_w):
            self.index = (self.index - 1) % len(items)
        elif key in (pg.K_DOWN, pg.K_s):
            self.index = (self.index + 1) % len(items)
        elif key in (pg.K_LEFT, pg.K_a, pg.K_RIGHT, pg.K_d):
            self._adjust(item, -1 if key in (pg.K_LEFT, pg.K_a) else 1)
        elif key in (pg.K_RETURN, pg.K_SPACE):
            return self._select(item)
        elif key == pg.K_ESCAPE:
            if self.screen == "main":
                return QUIT
            self._go("options" if self.screen == "controls" else "main")
        return None

    def _adjust(self, item: str, step: int) -> None:
        s = self.settings
        if item == "music":
            s.music_volume = max(0, min(VOLUME_STEPS, s.music_volume + step))
        elif item == "effects":
            s.effects_volume = max(0, min(VOLUME_STEPS, s.effects_volume + step))
        elif item == "fullscreen":
            s.fullscreen = not s.fullscreen
        else:
            return
        self.changed = True

    def _select(self, item: str) -> str | None:
        if item == "play":
            return PLAY
        if item == "quit":
            return QUIT
        if item in ("options", "controls"):
            self._go(item)
        elif item == "back":
            self._go("options" if self.screen == "controls" else "main")
        elif item == "fullscreen":
            self._adjust(item, 1)
        elif item == "reset":
            self.settings.keymap = default_keymap()
            self.changed = True
        elif item.startswith("bind:"):
            self.waiting_for_key = True
        return None

    def _go(self, screen: str) -> None:
        self.screen = screen
        self.index = 0


# ---------------------------------------------------------------------- drawing

SHADOW = (24, 20, 37)
WHITE = (255, 255, 255)
_text_cache: dict[tuple[str, int], pg.Surface] = {}


def pixel_text(text: str, scale: int) -> pg.Surface:
    """White block lettering with a dark drop shadow, like the welcome screen's.

    The text is rendered small without smoothing and then enlarged with
    nearest-neighbour scaling, which keeps the pixels square.
    """
    key = (text, scale)
    if key not in _text_cache:
        font = pg.font.Font(None, 20)
        small = font.render(text, False, WHITE)
        shadow = font.render(text, False, SHADOW)
        w, h = small.get_size()
        image = pg.Surface((w + 1, h + 1), pg.SRCALPHA)
        image.blit(shadow, (1, 1))
        image.blit(small, (0, 0))
        _text_cache[key] = pg.transform.scale(image, ((w + 1) * scale, (h + 1) * scale))
        if len(_text_cache) > 400:  # volume and key names create new strings; keep it bounded
            _text_cache.clear()
    return _text_cache[key]


def draw_menu(screen: pg.Surface, menu: Menu, bob: float = 0.0) -> None:
    """Draw the menu over whatever is already on the screen (sky and clouds)."""
    width, height = screen.get_size()
    title = pixel_text(menu.title(), 9)
    screen.blit(title, title.get_rect(center=(width // 2, height * 0.2 + bob)))

    items = menu.items()
    long_list = len(items) > 6  # the controls screen
    scale = 3 if long_list else 4
    line = 32 if long_list else 62
    top = height * (0.3 if long_list else 0.42)
    for i, (_id, text) in enumerate(items):
        selected = i == menu.index
        image = pixel_text(f"> {text} <" if selected else text, scale)
        if not selected:
            image = image.copy()
            image.set_alpha(170)
        screen.blit(image, image.get_rect(center=(width // 2, top + i * line + bob)))

    hint = "ARROWS MOVE   ENTER SELECT   ESC BACK"
    if menu.waiting_for_key:
        hint = "ESC CANCELS"
    image = pixel_text(hint, 2)
    screen.blit(image, image.get_rect(center=(width // 2, height - 30)))
