"""Fixed-timestep accumulator: turns variable frame times into whole ticks."""

from .constants import TICK_RATE


class FixedStep:
    """Call `advance(seconds_since_last_frame)` once per rendered frame and run
    `World.step` that many times. `alpha` is how far the display is between the
    last tick and the next one (0..1), for renderers that interpolate.
    """

    def __init__(self, rate: int = TICK_RATE, max_steps: int = 5):
        self.dt = 1.0 / rate
        self.max_steps = max_steps  # after a long stall, drop time instead of spiralling
        self._accumulated = 0.0

    def advance(self, elapsed: float) -> int:
        self._accumulated += max(0.0, elapsed)
        steps = int(self._accumulated / self.dt)
        if steps > self.max_steps:
            steps = self.max_steps
            self._accumulated = 0.0
        else:
            self._accumulated -= steps * self.dt
        return steps

    @property
    def alpha(self) -> float:
        return self._accumulated / self.dt
