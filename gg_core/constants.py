"""Movement and combat constants, taken from scripts/classes.py at tag v1.

Distances are pixels, speeds are pixels per tick, times are ticks (60 per second).
v1 advanced its physics once per rendered frame; one v1 frame is one tick here.
"""

TICK_RATE = 60

# Movement
GRAVITY = 0.2
WALL_SLIDE_GRAVITY = GRAVITY / 2  # falling while pushing into a wall
FAST_FALL_ACCEL = 0.5  # extra downward speed per tick while fast_fall is held
MAX_FALL_SPEED = 10
RUN_SPEED = 6
JUMP_SPEED = 5
AIR_CONTROL_DIVISOR = 10  # in the air, each tick adds direction * RUN_SPEED / 10

# Dash (roadmap task 2.5; not in v1). A short burst in a straight line.
DASH_SPEED = 15  # must stay below the tile size, or a dash could pass through a wall
DASH_TICKS = 8  # 8 ticks at 15 px is 120 px, a little under three tiles
DASH_COOLDOWN_TICKS = 45  # from the start of one dash to the start of the next

# Players
PLAYER_WIDTH = 35
PLAYER_HEIGHT = 55
MAX_HEALTH = 100

# Guns and bullets. Offsets are from the player's bottom-left corner.
GUN_OFFSET_X_FACING_RIGHT = 21
GUN_OFFSET_X_FACING_LEFT = 0
GUN_OFFSET_Y = 15
BULLET_SPAWN_X_FACING_RIGHT = 25  # from the gun position
BULLET_SPAWN_X_FACING_LEFT = -45
BULLET_SPAWN_Y = 5
BULLET_WIDTH = 35
BULLET_HEIGHT = 15
BULLET_SPEED = 20
BULLET_RANGE = 500
BULLET_DAMAGE = 20
FIRE_COOLDOWN_TICKS = 15  # v1: 250 ms

# Levels
DEFAULT_KILL_Y = -300  # a player below this height has fallen off the map
SOLID_TILE_TYPES = frozenset({"grass", "stone"})
