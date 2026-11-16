import pytest

from gg_core import FixedStep, PlayerInput


def test_direction():
    assert PlayerInput(left=True).direction == -1
    assert PlayerInput(right=True).direction == 1
    assert PlayerInput(left=True, right=True).direction == 0
    assert PlayerInput().direction == 0


@pytest.mark.parametrize("bits", range(32))
def test_bits_and_dict_round_trip(bits):
    held = PlayerInput.from_bits(bits)
    assert held.to_bits() == bits
    assert PlayerInput.from_dict(held.to_dict()) == held


def test_from_dict_tolerates_missing_and_unknown_keys():
    assert PlayerInput.from_dict({"jump": 1, "dash": True}) == PlayerInput(jump=True)


def test_fixed_step_runs_one_tick_per_sixtieth_of_a_second():
    clock = FixedStep()
    assert [clock.advance(1 / 60) for _ in range(5)] == [1, 1, 1, 1, 1]


def test_fixed_step_carries_leftover_time():
    clock = FixedStep()
    assert clock.advance(0.025) == 1  # 1.5 ticks
    assert clock.alpha == pytest.approx(0.5)
    assert clock.advance(0.025) == 2  # 0.5 carried + 1.5
    assert clock.advance(1 / 240) == 0
    assert clock.alpha == pytest.approx(0.25)


def test_fixed_step_same_total_time_gives_same_tick_count_at_any_frame_rate():
    for fps in (30, 60, 144, 240):
        clock = FixedStep()
        assert sum(clock.advance(1 / fps) for _ in range(fps * 2)) == pytest.approx(120, abs=1)


def test_fixed_step_drops_time_after_a_long_stall():
    clock = FixedStep(max_steps=5)
    assert clock.advance(2.0) == 5
    assert clock.advance(1 / 60) == 1
