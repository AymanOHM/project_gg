"""The game rules: one World per round, advanced one tick at a time.

`World.step` is a port of v1's `player.move`, `gun.fire` and `Bullet.update`
(scripts/classes.py at tag v1). The order of operations inside a tick follows v1
exactly, including the quirks noted below, because tests/test_v1_parity.py
compares every tick against traces recorded from the v1 code. Change behaviour
here only together with a roadmap task that says so, and re-record or retire the
affected traces in the same change.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from . import constants as c
from .geometry import overlaps
from .inputs import NO_INPUT, PlayerInput
from .level import Level

SNAPSHOT_VERSION = 1

PHASE_PLAYING = "playing"
PHASE_ROUND_OVER = "round_over"


@dataclass(slots=True)
class Player:
    id: str
    x: float
    y: float
    vy: float = 0.0
    move_x: float = 0.0  # horizontal distance covered in the last tick
    facing: int = 1  # 1 right, -1 left
    health: int = c.MAX_HEALTH
    action: str = "idle"  # idle | run | jump | wall_slide
    action_ticks: int = 0  # ticks since `action` last changed, for animation
    air_time: int = 0

    # Contacts found by the last tick's collision pass.
    hit_left: bool = False
    hit_right: bool = False
    hit_up: bool = False
    hit_down: bool = False

    air_jump_ready: bool = False  # granted on landing and by a wall jump
    wall_jumped_left: bool = False  # since last landing: keeps air control while touching walls
    wall_jumped_right: bool = False
    jump_was_held: bool = False
    last_fire_tick: int = 0

    # The gun trails the player by one tick, as in v1: a shot uses the position
    # and facing from the end of the previous tick.
    gun_x: float = 0.0
    gun_y: float = 0.0
    gun_facing: int = 1

    @property
    def touching(self) -> bool:
        return self.hit_left or self.hit_right or self.hit_up or self.hit_down


@dataclass(slots=True)
class Bullet:
    id: int
    owner: str
    x: float
    y: float
    start_x: float
    direction: int  # 1 right, -1 left


class World:
    """Authoritative state of one round. Deterministic: same level + same inputs = same result."""

    def __init__(self, level: Level, player_ids: tuple[str, ...] = ("p1", "p2")):
        missing = [pid for pid in player_ids if pid not in level.spawns]
        if missing:
            raise ValueError(f"level {level.name!r} has no spawn for {missing}")
        self.level = level
        self.tick = 0
        self.phase = PHASE_PLAYING
        self.winner: str | None = None  # set when the round ends; None then means a draw
        self.players: dict[str, Player] = {}
        self.bullets: list[Bullet] = []
        self._next_bullet_id = 1
        for pid in player_ids:
            x, y = level.spawns[pid]
            self.players[pid] = Player(
                id=pid, x=x, y=y,
                gun_x=x + c.PLAYER_WIDTH / 2, gun_y=y + c.PLAYER_HEIGHT / 2,
            )  # fmt: skip

    # ------------------------------------------------------------------ public

    def step(self, inputs: Mapping[str, PlayerInput]) -> None:
        """Advance the world by one tick (1/60 s).

        `inputs` maps player id to the buttons held during this tick. A player
        with no entry holds nothing. Once the round is over, step does nothing.
        """
        if self.phase != PHASE_PLAYING:
            return
        self.tick += 1

        for player in self.players.values():
            held = inputs.get(player.id, NO_INPUT)
            if held.jump and not player.jump_was_held:
                self._jump(player)
            player.jump_was_held = held.jump

        round_over = False
        for player in self.players.values():
            held = inputs.get(player.id, NO_INPUT)
            self._move(player, held.direction, held.fast_fall)
            if held.fire:
                self._fire(player)
            self._aim_gun(player)
            self._update_bullets(player.id)
            # v1 checks only the player whose turn it is, so damage dealt by a
            # player later in the order ends the round one tick later.
            if self._is_out(player):
                round_over = True

        if round_over:
            self.phase = PHASE_ROUND_OVER
            alive = [p.id for p in self.players.values() if not self._is_out(p)]
            self.winner = alive[0] if len(alive) == 1 else None

    def snapshot(self) -> dict:
        """Everything a renderer or a network client needs to draw this tick.

        Plain dicts, lists, strings and numbers only, so it serialises to JSON
        unchanged. The shape is documented in docs/adr/002-core-interfaces.md;
        bump SNAPSHOT_VERSION when it changes incompatibly.
        """
        return {
            "v": SNAPSHOT_VERSION,
            "tick": self.tick,
            "phase": self.phase,
            "winner": self.winner,
            "players": [
                {
                    "id": p.id,
                    "x": p.x,
                    "y": p.y,
                    "w": c.PLAYER_WIDTH,
                    "h": c.PLAYER_HEIGHT,
                    "vx": p.move_x,
                    "vy": p.vy,
                    "facing": p.facing,
                    "action": p.action,
                    "action_ticks": p.action_ticks,
                    "health": p.health,
                    "max_health": c.MAX_HEALTH,
                }
                for p in self.players.values()
            ],
            "bullets": [
                {
                    "id": b.id,
                    "owner": b.owner,
                    "x": b.x,
                    "y": b.y,
                    "w": c.BULLET_WIDTH,
                    "h": c.BULLET_HEIGHT,
                    "dir": b.direction,
                }
                for b in self.bullets
            ],
        }

    # ---------------------------------------------------------------- movement

    def _jump(self, p: Player) -> None:
        if not p.touching and p.air_jump_ready:  # double jump
            p.vy = c.JUMP_SPEED
            p.air_jump_ready = False
        elif p.hit_down:  # from the ground
            p.vy = c.JUMP_SPEED
        elif p.hit_right:  # wall jump, pushed away from the wall
            p.vy = c.JUMP_SPEED
            p.move_x = -c.RUN_SPEED
            p.wall_jumped_right, p.wall_jumped_left = True, False
            p.air_jump_ready = True
        elif p.hit_left:
            p.vy = c.JUMP_SPEED
            p.move_x = c.RUN_SPEED
            p.wall_jumped_left, p.wall_jumped_right = True, False
            p.air_jump_ready = True

    def _move(self, p: Player, direction: int, fast_fall: bool) -> None:
        w, h, size = c.PLAYER_WIDTH, c.PLAYER_HEIGHT, self.level.tile_size

        # Horizontal speed: instant on the ground, gradual in the air.
        if not p.touching or p.wall_jumped_left or p.wall_jumped_right:
            push = direction * c.RUN_SPEED / c.AIR_CONTROL_DIVISOR
            if p.move_x > 0:
                p.move_x = min(c.RUN_SPEED, p.move_x + push)
            else:
                p.move_x = max(-c.RUN_SPEED, p.move_x + push)
        else:
            p.move_x = direction * c.RUN_SPEED
        move_y = p.vy

        p.hit_left = p.hit_right = p.hit_up = p.hit_down = False
        against_wall = False

        p.x += p.move_x
        x = p.x
        for tile_x, tile_y in self.level.solid_tiles_around(p.x, p.y):
            if overlaps(x, p.y, w, h, tile_x, tile_y, size, size):
                if p.move_x > 0:
                    p.hit_right = against_wall = True
                    x = tile_x - w
                if p.move_x < 0:
                    p.hit_left = against_wall = True
                    x = tile_x + size
                p.x = x

        p.y += move_y
        y = p.y
        for tile_x, tile_y in self.level.solid_tiles_around(p.x, p.y):
            if overlaps(p.x, y, w, h, tile_x, tile_y, size, size):
                if move_y > 0:
                    p.vy = 0
                    p.hit_up = True
                    y = tile_y - h
                if move_y < 0:  # landed
                    p.vy = 0
                    p.hit_down = True
                    p.air_jump_ready = True
                    p.wall_jumped_left = p.wall_jumped_right = False
                    p.air_time = 0
                    y = tile_y + size
                p.y = y

        gravity = c.WALL_SLIDE_GRAVITY if p.vy < 0 and against_wall else c.GRAVITY
        if fast_fall:
            p.vy = p.vy - c.FAST_FALL_ACCEL
        p.vy = max(-c.MAX_FALL_SPEED, p.vy - gravity)

        if p.move_x > 0:
            p.facing = 1
        if p.move_x < 0:
            p.facing = -1

        p.action_ticks += 1
        p.air_time += 1
        if p.air_time > 1:
            action = "wall_slide" if p.hit_left or p.hit_right else "jump"
        elif direction != 0:
            action = "run"
        else:
            action = "idle"
        if action != p.action:
            p.action = action
            p.action_ticks = 0

    # ------------------------------------------------------------------ combat

    def _fire(self, p: Player) -> None:
        if self.tick - p.last_fire_tick < c.FIRE_COOLDOWN_TICKS:
            return
        p.last_fire_tick = self.tick
        if p.gun_facing > 0:
            x = p.gun_x + c.BULLET_SPAWN_X_FACING_RIGHT
        else:
            x = p.gun_x + c.BULLET_SPAWN_X_FACING_LEFT
        self.bullets.append(
            Bullet(
                id=self._next_bullet_id,
                owner=p.id,
                x=x,
                y=p.gun_y + c.BULLET_SPAWN_Y,
                start_x=x,
                direction=p.gun_facing,
            )
        )
        self._next_bullet_id += 1

    def _aim_gun(self, p: Player) -> None:
        p.gun_facing = p.facing
        offset = c.GUN_OFFSET_X_FACING_RIGHT if p.facing > 0 else c.GUN_OFFSET_X_FACING_LEFT
        p.gun_x = p.x + offset
        p.gun_y = p.y + c.GUN_OFFSET_Y

    def _update_bullets(self, owner: str) -> None:
        """Advance one player's bullets. Builds a new list instead of removing while
        iterating, which is the fix for v1's skipped-bullet bug (roadmap task 1.7)."""
        kept = []
        for b in self.bullets:
            if b.owner != owner or self._bullet_survives(b):
                kept.append(b)
        self.bullets = kept

    def _bullet_survives(self, b: Bullet) -> bool:
        w, h, size = c.BULLET_WIDTH, c.BULLET_HEIGHT, self.level.tile_size
        if abs(b.x - b.start_x) > c.BULLET_RANGE:
            return False
        # v1 tests players in reverse order and a bullet can hit its own shooter.
        for p in reversed(self.players.values()):
            if overlaps(b.x, b.y, w, h, p.x, p.y, c.PLAYER_WIDTH, c.PLAYER_HEIGHT):
                p.health -= c.BULLET_DAMAGE
                return False
        for tile_x, tile_y in self.level.solid_tiles_around(b.x, b.y):
            if overlaps(b.x, b.y, w, h, tile_x, tile_y, size, size):
                return False
        b.x += c.BULLET_SPEED * b.direction
        return True

    def _is_out(self, p: Player) -> bool:
        return p.health <= 0 or p.y < self.level.kill_y
