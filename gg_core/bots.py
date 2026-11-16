"""Headless input generators, for tests now and for load tests later."""

import random

from .inputs import PlayerInput

_TOGGLE_CHANCE = {"left": 0.04, "right": 0.04, "jump": 0.15, "fire": 0.02, "fast_fall": 0.03}


class RandomBot:
    """Holds and releases buttons at random. Seeded, so a run can be repeated exactly."""

    def __init__(self, seed: int):
        self._rng = random.Random(seed)
        self._held = dict.fromkeys(_TOGGLE_CHANCE, False)

    def next_input(self) -> PlayerInput:
        for button, chance in _TOGGLE_CHANCE.items():
            if self._rng.random() < chance:
                self._held[button] = not self._held[button]
        return PlayerInput(**self._held)
