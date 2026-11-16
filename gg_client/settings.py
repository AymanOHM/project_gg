"""Player settings: volumes, fullscreen and key bindings, saved between runs."""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pygame as pg

from .keyboard import KEYMAP

SETTINGS_PATH = Path.home() / ".project_gg" / "settings.json"
VOLUME_STEPS = 10


def default_keymap() -> dict[str, dict[str, list[int]]]:
    return {
        pid: {button: list(keys) for button, keys in buttons.items()}
        for pid, buttons in KEYMAP.items()
    }


@dataclass
class Settings:
    music_volume: int = 5  # 0..VOLUME_STEPS
    effects_volume: int = 10
    fullscreen: bool = False
    keymap: dict[str, dict[str, list[int]]] = field(default_factory=default_keymap)

    def to_dict(self) -> dict:
        """JSON form. Keys are stored by name ("space", "left"), which survives pygame upgrades."""
        return {
            "music_volume": self.music_volume,
            "effects_volume": self.effects_volume,
            "fullscreen": self.fullscreen,
            "keymap": {
                pid: {button: [pg.key.name(k) for k in keys] for button, keys in buttons.items()}
                for pid, buttons in self.keymap.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        """Build from saved data. Anything missing or invalid falls back to the default."""
        settings = cls()
        for name in ("music_volume", "effects_volume"):
            value = data.get(name)
            if (
                isinstance(value, int)
                and not isinstance(value, bool)
                and 0 <= value <= VOLUME_STEPS
            ):
                setattr(settings, name, value)
        if isinstance(data.get("fullscreen"), bool):
            settings.fullscreen = data["fullscreen"]
        saved = data.get("keymap")
        if isinstance(saved, dict):
            for pid, buttons in settings.keymap.items():
                for button in buttons:
                    names = (
                        saved.get(pid, {}).get(button) if isinstance(saved.get(pid), dict) else None
                    )
                    keys = _keys_from_names(names)
                    if keys:
                        buttons[button] = keys
        return settings

    def save(self, path: Path = SETTINGS_PATH) -> None:
        if sys.platform == "emscripten":  # no lasting file system in the browser
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.to_dict(), indent=2))
        except OSError:
            pass  # settings are a convenience; never stop the game over them

    @classmethod
    def load(cls, path: Path = SETTINGS_PATH) -> "Settings":
        try:
            return cls.from_dict(json.loads(path.read_text()))
        except (OSError, ValueError):
            return cls()


def _keys_from_names(names) -> list[int]:
    if not isinstance(names, list):
        return []
    keys = []
    for name in names:
        try:
            keys.append(pg.key.key_code(name))
        except (ValueError, TypeError):
            continue
    return keys
