"""Headless rules for Project GG. Standard library only: no pygame, no OpenGL."""

from .clock import FixedStep
from .inputs import NO_INPUT, PlayerInput
from .level import Level, LevelError, load_level

__all__ = ["NO_INPUT", "FixedStep", "Level", "LevelError", "PlayerInput", "load_level"]
