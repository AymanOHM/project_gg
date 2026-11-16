"""Record tick-by-tick traces from the original v1 game code, without a window.

The v1 classes in scripts/ call OpenGL directly, so this script installs stub
OpenGL modules, drives `player.move()` with scripted inputs at one frame per
tick, and writes the resulting state to tests/golden/v1_traces.json.gz.
gg_core must reproduce these traces exactly (tests/test_v1_parity.py).

Two deliberate differences from v1 as shipped:
- The bullet list is iterated over a copy, which fixes the skipped-bullet bug
  (roadmap task 1.7). gg_core has the same fix.
- The fire cooldown clock advances 17 ms per frame, so "more than 250 ms"
  means 15 frames.

Run from the repo root:  uv run python tools/record_v1_traces.py
Only needed again if the scenarios change; scripts/ itself is frozen.
"""

import gzip
import json
import random
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "golden" / "v1_traces.json.gz"
sys.path.insert(0, str(ROOT))

FRAME_MS = 17
clock = {"frame": 0}


def _install_opengl_stubs():
    def noop(*args, **kwargs):
        return None

    names = [
        "glGenTextures", "glBindTexture", "glTexParameterf", "glTexImage2D", "glBegin", "glEnd",
        "glTexCoord2f", "glVertex2f", "GL_TEXTURE_2D", "GL_TEXTURE_WRAP_S", "GL_TEXTURE_WRAP_T",
        "GL_REPEAT", "GL_TEXTURE_MIN_FILTER", "GL_TEXTURE_MAG_FILTER", "GL_NEAREST", "GL_RGBA",
        "GL_UNSIGNED_BYTE", "GL_QUADS",
    ]  # fmt: skip
    gl = types.ModuleType("OpenGL.GL")
    for name in names:
        setattr(gl, name, noop if name.startswith("gl") else 0)
    glut = types.ModuleType("OpenGL.GLUT")
    glut.GLUT_ELAPSED_TIME = 0
    glut.glutGet = lambda _what: clock["frame"] * FRAME_MS
    glu = types.ModuleType("OpenGL.GLU")
    pkg = types.ModuleType("OpenGL")
    pkg.GL, pkg.GLUT, pkg.GLU = gl, glut, glu
    sys.modules.update({"OpenGL": pkg, "OpenGL.GL": gl, "OpenGL.GLUT": glut, "OpenGL.GLU": glu})


_install_opengl_stubs()

from scripts import classes  # noqa: E402
from scripts.helper_func import Animation  # noqa: E402
from scripts.tilemap import Tilemap  # noqa: E402


def _fixed_bullets_update(self):
    for bullet in list(self.bullets):
        if abs(bullet.pos[0] - bullet.s_pos[0]) > 500:
            self.bullets.remove(bullet)
        else:
            bullet.update()


classes.Bullets.update = _fixed_bullets_update

LEFT, RIGHT, JUMP, FIRE, FAST_FALL = 1, 2, 4, 8, 16


class V1Game:
    """The parts of v1's Game object that the entity classes reach into."""

    def __init__(self):
        img = [b"", 1, 1]
        self.environment = {"gravity": 0.2}
        self.assets = {"gun": img, "bullet": img, "health_bar": img}
        for who in ("player", "enemy"):
            self.assets[who] = img
            for action, dur in (
                ("idle", 6),
                ("run", 4),
                ("jump", 5),
                ("slide", 5),
                ("wall_slide", 5),
            ):
                self.assets[f"{who}/{action}"] = Animation([img], img_dur=dur)
        self.stage = 1
        self.is_alive = True
        self.tilemap = Tilemap(game=self, tile_size=45)
        self.tilemap.load(str(ROOT / "map.json"))
        clock["frame"] = 0
        # v1 names: `enemy` is the WASD player (p1, left spawn), `player` the numpad one (p2).
        self.player = classes.player(self, "player", (900, 600), (35, 55))
        self.enemy = classes.player(self, "enemy", (80, 600), (35, 55))


def _state(p):
    return [
        p.pos[0], p.pos[1], p.velocity[1], p.mov_amount[0], int(p.flip), p.action, p.health,
        int(p.collisions["left"]), int(p.collisions["right"]),
        int(p.collisions["up"]), int(p.collisions["down"]),
        [[b.pos[0], b.pos[1], 1 if b.flip else -1] for b in p.gun.bullets.bullets],
    ]  # fmt: skip


def run(inputs):
    """inputs: list of (p1_mask, p2_mask) per frame. Returns the recorded frames."""
    game = V1Game()
    p1, p2 = game.enemy, game.player
    prev = (0, 0)
    frames = []
    for masks in inputs:
        clock["frame"] += 1
        for p, mask, before in ((p1, masks[0], prev[0]), (p2, masks[1], prev[1])):
            if mask & JUMP and not before & JUMP:
                p.jump()
            p.flags["fast_fall"] = bool(mask & FAST_FALL)
            p.fire = bool(mask & FIRE)
        prev = masks
        for p, mask in ((p1, masks[0]), (p2, masks[1])):
            p.move(game.tilemap, [bool(mask & RIGHT) - bool(mask & LEFT), 0])
        frames.append([_state(p1), _state(p2)])
        if game.stage == 2:
            break
    return frames


def hold(mask, n):
    return [mask] * n


def both(a, b):
    n = max(len(a), len(b))
    a, b = a + [0] * (n - len(a)), b + [0] * (n - len(b))
    return list(zip(a, b, strict=True))


def random_inputs(seed, n, p2_walks=True):
    rng = random.Random(seed)
    out, masks = [], [0, 0]
    chances = ((LEFT, 0.04), (RIGHT, 0.04), (JUMP, 0.15), (FIRE, 0.02), (FAST_FALL, 0.03))
    for _ in range(n):
        for i in (0, 1):
            for bit, chance in chances:
                if rng.random() < chance and (i == 0 or p2_walks or bit > RIGHT):
                    masks[i] ^= bit
        out.append((masks[0], masks[1]))
    return out


def tap(mask, base=0):
    """One frame with `mask` pressed on top of `base`, then one frame of `base` alone."""
    return [base | mask, base]


# Map geometry these scripts rely on (pixels, Y-up): p1 lands at (80, 720) in the left
# tunnel; p2 lands at (900, 450) on a platform spanning x 720..945. Running right and
# jumping once at the tunnel exit carries p1 over the middle structure onto p2's platform.
SETTLE = hold(0, 90)  # both players pop out of their spawn tiles and land
P1_TO_P2_PLATFORM = SETTLE + hold(RIGHT, 45) + tap(JUMP, RIGHT) + hold(RIGHT, 88)
P1_TO_MIDDLE_WALL = SETTLE + hold(RIGHT, 150)  # ends pressed against a wall at (325, 585)

SCENARIOS = {
    "idle": both(hold(0, 200), hold(0, 200)),
    "run_and_stop": both(
        SETTLE + hold(RIGHT, 6) + hold(0, 10) + hold(LEFT, 9) + hold(0, 30),
        SETTLE + hold(LEFT, 25) + hold(0, 10) + hold(RIGHT, 20) + hold(0, 30),
    ),
    "jump_and_double_jump": both(
        SETTLE + tap(JUMP) + hold(0, 20) + tap(JUMP) + hold(0, 20) + tap(JUMP) + hold(0, 120),
        SETTLE
        + tap(JUMP, LEFT)
        + hold(LEFT, 10)
        + tap(JUMP, RIGHT)
        + hold(RIGHT, 9)
        + hold(0, 150),
    ),
    "jump_held_does_not_repeat": both(SETTLE + hold(JUMP, 200), SETTLE + hold(JUMP | LEFT, 12)),
    "fast_fall": both(
        SETTLE + tap(JUMP) + hold(0, 15) + hold(FAST_FALL, 60),
        SETTLE + tap(JUMP) + hold(0, 5) + tap(JUMP) + hold(FAST_FALL, 120),
    ),
    "head_bump_in_tunnel": both(SETTLE + (tap(JUMP) + hold(0, 30)) * 3, SETTLE),
    "wall_jumps": both(
        P1_TO_MIDDLE_WALL
        + (tap(JUMP, RIGHT) + hold(RIGHT, 14)) * 4
        + (tap(JUMP, RIGHT) + hold(LEFT, 8) + hold(RIGHT, 20)) * 4
        + hold(0, 200),
        SETTLE,
    ),
    "walk_off_the_map_right": both(SETTLE, SETTLE + hold(RIGHT, 600)),
    "walk_off_the_map_left": both(SETTLE + hold(LEFT, 600), SETTLE),
    "cross_the_map": both(P1_TO_P2_PLATFORM + hold(0, 60), hold(0, 300)),
    "firefight_p1_wins": both(
        P1_TO_P2_PLATFORM + hold(FIRE, 400),
        hold(0, 232) + hold(LEFT, 1) + hold(FIRE, 400),
    ),
    "firefight_p2_wins": both(
        P1_TO_P2_PLATFORM + hold(0, 30) + hold(FIRE, 400),
        hold(0, 222) + hold(LEFT, 1) + hold(FIRE, 400),
    ),
    "fire_taps_respect_cooldown": both(
        P1_TO_P2_PLATFORM + (tap(FIRE) + hold(0, 4)) * 20,
        hold(0, 500),
    ),
    "fire_into_wall_and_out_of_range": both(
        P1_TO_MIDDLE_WALL + hold(FIRE, 60) + hold(LEFT, 1) + hold(FIRE, 120),
        SETTLE + hold(FIRE, 120),
    ),
    **{f"random_seed_{n}": random_inputs(n, 1500) for n in range(1, 9)},
    **{f"random_p2_stays_seed_{n}": random_inputs(n, 1500, p2_walks=False) for n in range(11, 17)},
}


def main():
    traces = {}
    for name, inputs in SCENARIOS.items():
        frames = run(inputs)
        traces[name] = {"inputs": [list(m) for m in inputs[: len(frames)]], "frames": frames}
        last = frames[-1]
        print(f"{name:34s} frames={len(frames):5d} p1=({last[0][0]:.0f},{last[0][1]:.0f}) hp={last[0][6]}"  # noqa: E501
              f" p2=({last[1][0]:.0f},{last[1][1]:.0f}) hp={last[1][6]}")  # fmt: skip
    doc = {
        "source": "scripts/ at tag v1, bullet-list fix applied, 1 frame = 1 tick",
        "player_fields": ["x", "y", "vy", "move_x", "flip", "action", "health",
                          "hit_left", "hit_right", "hit_up", "hit_down", "bullets[x, y, dir]"],
        "input_bits": {"left": LEFT, "right": RIGHT, "jump": JUMP, "fire": FIRE, "fast_fall": FAST_FALL},  # noqa: E501
        "traces": traces,
    }  # fmt: skip
    with gzip.GzipFile(OUT, "wb", mtime=0) as f:
        f.write(json.dumps(doc, separators=(",", ":")).encode())
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
