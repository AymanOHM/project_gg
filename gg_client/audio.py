"""Music and sound effects.

Sounds are triggered by the "events" list in each snapshot, so the same code
works for local play and for snapshots that arrive from a server. If the audio
device cannot be opened, everything here does nothing.
"""

from pathlib import Path

import pygame as pg

DATA = Path(__file__).resolve().parent.parent / "data"

# Snapshot event type -> (sound file, volume).
EVENT_SOUNDS = {
    "jump": ("jump.ogg", 0.7),
    "shot": ("shoot.ogg", 0.4),
    "hit": ("hit.ogg", 0.8),
}
MUSIC_VOLUME = 0.5
AMBIENCE_VOLUME = 0.2


class Audio:
    def __init__(self):
        self.enabled = True
        self.sounds: dict[str, pg.mixer.Sound] = {}
        try:
            if not pg.mixer.get_init():
                pg.mixer.init()
            for event, (file, volume) in EVENT_SOUNDS.items():
                sound = pg.mixer.Sound(DATA / "sfx" / file)
                sound.set_volume(volume)
                self.sounds[event] = sound
            self.ambience = pg.mixer.Sound(DATA / "sfx" / "ambience.ogg")
            self.ambience.set_volume(AMBIENCE_VOLUME)
        except (pg.error, FileNotFoundError):
            self.enabled = False
        self._last_tick = None

    def start_music(self) -> None:
        if not self.enabled:
            return
        pg.mixer.music.load(DATA / "music.ogg")
        pg.mixer.music.set_volume(MUSIC_VOLUME)
        pg.mixer.music.play(-1)
        self.ambience.play(-1)

    def play_events(self, snapshot: dict) -> list[str]:
        """Play the sounds for a snapshot's events, once per tick. Returns what was played."""
        key = (snapshot.get("match", {}).get("round"), snapshot["tick"])
        if key == self._last_tick:  # the same tick drawn twice
            return []
        self._last_tick = key
        played = [e["type"] for e in snapshot["events"] if e["type"] in EVENT_SOUNDS]
        if self.enabled:
            for event in played:
                self.sounds[event].play()
        return played
