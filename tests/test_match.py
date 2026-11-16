import json
from pathlib import Path

import pytest

from gg_core import (
    MATCH_COUNTDOWN,
    MATCH_OVER,
    MATCH_PLAYING,
    MATCH_ROUND_OVER,
    Level,
    Match,
    PlayerInput,
    load_level,
)
from gg_core.bots import RandomBot

ARENA = load_level(Path(__file__).resolve().parent.parent / "data/levels/arena.json")
RIGHT = PlayerInput(right=True)


def pit(name):
    """A level where p1 stands on a floor and p2 has nothing under it."""
    return Level.from_dict(
        {
            "format": 1,
            "name": name,
            "tile_size": 45,
            "spawns": {"p1": [0, 45], "p2": [900, 45]},
            "tiles": [{"x": x, "y": 0, "type": "grass", "variant": 0} for x in range(-2, 3)],
        }
    )


def run_until(match, phase, inputs=None, limit=5000):
    for _ in range(limit):
        if match.phase == phase:
            return
        match.step(inputs or {})
    raise AssertionError(f"never reached {phase}; stuck in {match.phase}")


def test_inputs_are_ignored_during_the_countdown():
    match = Match([ARENA], countdown_ticks=180)
    for _ in range(180):
        assert match.phase == MATCH_COUNTDOWN
        match.step({"p1": PlayerInput(right=True, fire=True, jump=True)})
    assert match.phase == MATCH_PLAYING
    p1 = match.snapshot()["players"][0]
    assert (p1["x"], p1["y"]) == (80, 720)  # dropped onto the level, did not walk
    assert match.snapshot()["bullets"] == []
    match.step({"p1": RIGHT})
    assert match.snapshot()["players"][0]["x"] == 86


def test_countdown_reports_ticks_left():
    match = Match([ARENA], countdown_ticks=180)
    assert match.snapshot()["match"]["ticks_left"] == 180
    match.step({})
    assert match.snapshot()["match"]["ticks_left"] == 179


def test_best_of_three_is_won_by_the_first_to_two_rounds():
    match = Match([pit("a")], rounds_to_win=2, countdown_ticks=10, round_over_ticks=5)
    run_until(match, MATCH_ROUND_OVER)
    assert match.scores == {"p1": 1, "p2": 0} and match.round == 1 and match.winner is None
    run_until(match, MATCH_COUNTDOWN)
    assert match.round == 2
    run_until(match, MATCH_OVER)
    assert match.scores == {"p1": 2, "p2": 0} and match.round == 2
    assert match.winner == "p1"


def test_a_draw_scores_for_nobody_and_the_match_goes_on():
    both_fall = Level.from_dict(
        {**pit("void").to_dict(), "spawns": {"p1": [900, 45], "p2": [950, 45]}}
    )
    match = Match([both_fall], rounds_to_win=1, countdown_ticks=0, round_over_ticks=1)
    run_until(match, MATCH_ROUND_OVER)
    assert match.scores == {"p1": 0, "p2": 0}
    run_until(match, MATCH_PLAYING)
    assert match.round == 2 and match.winner is None


def test_levels_rotate_each_round():
    match = Match([pit("a"), pit("b")], rounds_to_win=3, countdown_ticks=1, round_over_ticks=1)
    names = []
    while match.phase != MATCH_OVER:
        if not names or names[-1][0] != match.round:
            names.append((match.round, match.snapshot()["match"]["level"]))
        match.step({})
    assert names == [(1, "a"), (2, "b"), (3, "a")]


def test_step_does_nothing_after_the_match_is_over():
    match = Match([pit("a")], rounds_to_win=1, countdown_ticks=1, round_over_ticks=1)
    run_until(match, MATCH_OVER)
    before = match.snapshot()
    match.step({"p1": RIGHT})
    assert match.snapshot() == before


def test_snapshot_is_the_world_snapshot_plus_a_match_object():
    match = Match([ARENA])
    snap = match.snapshot()
    assert json.loads(json.dumps(snap)) == snap
    assert {k: v for k, v in snap.items() if k != "match"} == match.world.snapshot()
    assert snap["match"] == {
        "phase": "countdown",
        "tick": 0,
        "round": 1,
        "level": "arena",
        "scores": {"p1": 0, "p2": 0},
        "rounds_to_win": 2,
        "ticks_left": 180,
        "winner": None,
    }


def test_a_full_match_between_bots_finishes_and_is_repeatable():
    def play():
        bots = {"p1": RandomBot(1), "p2": RandomBot(2)}
        match = Match([ARENA])
        run = []
        for _ in range(60_000):
            if match.phase == MATCH_OVER:
                break
            match.step({pid: bot.next_input() for pid, bot in bots.items()})
            run.append(match.snapshot()["match"]["scores"])
        return match.phase, match.winner, run[-1], len(run)

    first = play()
    assert first[0] == MATCH_OVER and first[1] in {"p1", "p2"}
    assert first == play()


@pytest.mark.parametrize("kwargs", [{"levels": []}, {"levels": [ARENA], "rounds_to_win": 0}])
def test_invalid_matches_are_rejected(kwargs):
    with pytest.raises(ValueError):
        Match(**kwargs)
