"""A match: several rounds on one or more levels, first to `rounds_to_win` wins.

Match owns the flow around the rounds (countdown, pause after a round, score,
level rotation) and leaves the rules to World. It has the same two calls as
World, `step(inputs)` and `snapshot()`, so loops, renderers and the server can
treat it the same way.
"""

from collections.abc import Mapping, Sequence

from .constants import TICK_RATE
from .inputs import PlayerInput
from .level import Level
from .world import PHASE_ROUND_OVER, World

MATCH_COUNTDOWN = "countdown"
MATCH_PLAYING = "playing"
MATCH_ROUND_OVER = "round_over"
MATCH_OVER = "match_over"

_NO_INPUTS: Mapping[str, PlayerInput] = {}


class Match:
    def __init__(
        self,
        levels: Sequence[Level],
        rounds_to_win: int = 2,  # best of 3
        countdown_ticks: int = 3 * TICK_RATE,
        round_over_ticks: int = 2 * TICK_RATE,
        player_ids: tuple[str, ...] = ("p1", "p2"),
    ):
        if not levels:
            raise ValueError("a match needs at least one level")
        if rounds_to_win < 1:
            raise ValueError("rounds_to_win must be at least 1")
        self.levels = tuple(levels)
        self.rounds_to_win = rounds_to_win
        self.countdown_ticks = countdown_ticks
        self.round_over_ticks = round_over_ticks
        self.player_ids = player_ids
        self.scores = dict.fromkeys(player_ids, 0)
        self.round = 0  # 1 for the first round
        self.winner: str | None = None  # the match winner, once phase is match_over
        self.tick = 0
        self._start_round()

    @property
    def level(self) -> Level:
        """The level of the current round. Levels rotate in the order given."""
        return self.levels[(self.round - 1) % len(self.levels)]

    def step(self, inputs: Mapping[str, PlayerInput]) -> None:
        """Advance the match by one tick. Does nothing once the match is over."""
        if self.phase == MATCH_OVER:
            return
        self.tick += 1

        if self.phase == MATCH_COUNTDOWN:
            # The world runs with nothing held, so players drop onto the level
            # and stand still until the countdown ends.
            self.world.step(_NO_INPUTS)
            self._timer -= 1
            if self._timer <= 0:
                self.phase = MATCH_PLAYING

        elif self.phase == MATCH_PLAYING:
            self.world.step(inputs)
            if self.world.phase == PHASE_ROUND_OVER:
                if self.world.winner is not None:  # a draw scores for nobody
                    self.scores[self.world.winner] += 1
                self.phase = MATCH_ROUND_OVER
                self._timer = self.round_over_ticks

        elif self.phase == MATCH_ROUND_OVER:
            self._timer -= 1
            if self._timer <= 0:
                leader = max(self.scores, key=self.scores.get)
                if self.scores[leader] >= self.rounds_to_win:
                    self.winner = leader
                    self.phase = MATCH_OVER
                else:
                    self._start_round()

    def snapshot(self) -> dict:
        """The world's snapshot plus a "match" object. See docs/adr/002-core-interfaces.md."""
        snap = self.world.snapshot()
        snap["match"] = {
            "phase": self.phase,
            "tick": self.tick,
            "round": self.round,
            "level": self.level.name,
            "scores": dict(self.scores),
            "rounds_to_win": self.rounds_to_win,
            "ticks_left": self._timer if self.phase in (MATCH_COUNTDOWN, MATCH_ROUND_OVER) else 0,
            "winner": self.winner,
        }
        return snap

    def _start_round(self) -> None:
        self.round += 1
        self.world = World(self.level, self.player_ids)
        self.phase = MATCH_COUNTDOWN
        self._timer = self.countdown_ticks
        if self._timer <= 0:
            self.phase = MATCH_PLAYING
