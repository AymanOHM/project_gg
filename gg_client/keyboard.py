"""Keyboard layout: which keys each local player holds for each button."""

import pygame as pg

from gg_core import PlayerInput

# p1 keeps v1's WASD + space. p2 keeps v1's numpad and also gets the arrow keys,
# because laptops have no numpad. Dash is new in the rewrite.
KEYMAP = {
    "p1": {
        "left": (pg.K_a,),
        "right": (pg.K_d,),
        "jump": (pg.K_w,),
        "fast_fall": (pg.K_s,),
        "fire": (pg.K_SPACE,),
        "dash": (pg.K_LSHIFT,),
    },
    "p2": {
        "left": (pg.K_LEFT, pg.K_KP4),
        "right": (pg.K_RIGHT, pg.K_KP6),
        "jump": (pg.K_UP, pg.K_KP8),
        "fast_fall": (pg.K_DOWN, pg.K_KP5),
        "fire": (pg.K_RSHIFT, pg.K_SLASH, pg.K_KP0),
        "dash": (pg.K_PERIOD, pg.K_KP_PERIOD),
    },
}


def read_inputs(pressed, keymap=KEYMAP) -> dict[str, PlayerInput]:
    """Turn `pygame.key.get_pressed()` into one PlayerInput per local player."""
    return {
        pid: PlayerInput(
            **{button: any(pressed[k] for k in keys) for button, keys in buttons.items()}
        )
        for pid, buttons in keymap.items()
    }
