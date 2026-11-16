"""Player input commands.

An input is the set of buttons a player holds during one tick. The world turns
held buttons into actions itself (for example, a jump happens on the tick the
jump button goes from released to held), so clients only ever report key state.
"""

from dataclasses import asdict, dataclass

_FIELDS = ("left", "right", "jump", "fire", "fast_fall")


@dataclass(frozen=True, slots=True)
class PlayerInput:
    left: bool = False
    right: bool = False
    jump: bool = False
    fire: bool = False
    fast_fall: bool = False

    @property
    def direction(self) -> int:
        """-1 for left, 1 for right, 0 for neither or both."""
        return int(self.right) - int(self.left)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerInput":
        """Build from a decoded JSON object. Missing buttons are released; extras are ignored."""
        return cls(**{name: bool(data.get(name, False)) for name in _FIELDS})

    def to_bits(self) -> int:
        """Compact form: bit 0 left, 1 right, 2 jump, 3 fire, 4 fast_fall."""
        return sum(1 << i for i, name in enumerate(_FIELDS) if getattr(self, name))

    @classmethod
    def from_bits(cls, bits: int) -> "PlayerInput":
        return cls(**{name: bool(bits >> i & 1) for i, name in enumerate(_FIELDS)})


NO_INPUT = PlayerInput()
