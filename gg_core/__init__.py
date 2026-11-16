"""Headless rules for Project GG. Standard library only: no pygame, no OpenGL."""

from .clock import FixedStep
from .inputs import NO_INPUT, PlayerInput
from .level import Level, LevelError, load_level
from .match import MATCH_COUNTDOWN, MATCH_OVER, MATCH_PLAYING, MATCH_ROUND_OVER, Match
from .world import PHASE_PLAYING, PHASE_ROUND_OVER, SNAPSHOT_VERSION, World

__all__ = [
    "MATCH_COUNTDOWN",
    "MATCH_OVER",
    "MATCH_PLAYING",
    "MATCH_ROUND_OVER",
    "NO_INPUT",
    "PHASE_PLAYING",
    "PHASE_ROUND_OVER",
    "SNAPSHOT_VERSION",
    "FixedStep",
    "Level",
    "LevelError",
    "Match",
    "PlayerInput",
    "World",
    "load_level",
]
