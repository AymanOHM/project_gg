# ADR-002: Core interfaces — step, inputs, snapshot, renderer

- **Status:** Accepted by Ayman on 2026-11-16. Still open for revision at the interface session with the second developer
- **Date:** 2026-11-16
- **Covers:** roadmap tasks 1.2, 1.3, 1.4, 1.5, 1.9, 2.1 (rules part) and the contract for 1.6

## Context

The rules must run in three places (desktop client, browser client, game server) and the renderer is built by a different person from the rules. Both need a small, stable contract. The matchmaker language is undecided, so nothing that crosses a process boundary may depend on Python.

## Decision

**1. One tick is one call.** `World.step(inputs)` advances the game by exactly 1/60 s. The world never reads a clock. Whoever owns the loop decides when to call it: the client uses `FixedStep` (an accumulator), the server uses a 60 Hz timer.

**2. Inputs are held buttons, not events.** `inputs` maps player id to `PlayerInput(left, right, jump, fire, fast_fall)`: the buttons held during that tick. The world derives events itself; a jump happens on the tick `jump` goes from released to held. A missing player holds nothing. On the wire an input is the same five booleans as a JSON object (`to_dict`), or five bits (`to_bits`).

**3. The snapshot is the only view of the world.** `World.snapshot()` returns plain dicts, lists, strings and numbers:

```json
{
  "v": 1, "tick": 512, "phase": "playing", "winner": null,
  "players": [{"id": "p1", "x": 80.0, "y": 720.0, "w": 35, "h": 55, "vx": 0.0, "vy": -0.2,
               "facing": 1, "action": "idle", "action_ticks": 14, "health": 100, "max_health": 100}],
  "bullets": [{"id": 7, "owner": "p1", "x": 126.0, "y": 740.0, "w": 35, "h": 15, "dir": 1}]
}
```

The snapshot also has `"events"`: what happened during that tick, as a list of `{"type": "jump" | "shot" | "hit", "player": id}`. They exist for sound and effects; a shot or a hit can begin and end inside one tick and never show up in `bullets`. A server that sends fewer snapshots than ticks must collect the events of the ticks in between.

`phase` is `playing` or `round_over`; `winner` is a player id, or `null` for a draw or an unfinished round. `action` is `idle`, `run`, `jump` or `wall_slide`, and `action_ticks` counts ticks since it changed, so a renderer picks the animation frame as `action_ticks // frame_duration % frame_count`. `v` goes up on any incompatible change.

**4. The renderer sees snapshots, never the world.** `Renderer.load_level(level)` once per round, then `Renderer.draw(snapshot, alpha)` once per frame (`gg_client/renderer.py`). Local play and online play feed it the same dicts, so the renderer can be built and tested against recorded snapshots with no rules code running.

**5. Coordinates stay as v1 had them.** Pixels, Y-up, position at the bottom-left corner of each rectangle. The renderer flips Y.

**6. Levels are a versioned JSON file** with tile size, spawn points and kill height inside it (`gg_core/level.py`), validated on load.

**7. The world is deterministic.** No wall-clock time, no unseeded randomness. The same level and inputs always give the same snapshots, which is what the v1 parity tests, replays and later client-side prediction rely on.

**8. A match wraps the world.** `Match(levels, rounds_to_win=2)` has the same `step(inputs)` and `snapshot()` and adds the flow around rounds: a 3 s countdown during which inputs are ignored, a 2 s pause after each round, the score, and level rotation. Its snapshot is the world's snapshot plus one object:

```json
"match": {"phase": "countdown", "tick": 0, "round": 1, "level": "arena", "scores": {"p1": 0, "p2": 0},
          "rounds_to_win": 2, "ticks_left": 180, "winner": null}
```

`match.phase` is `countdown`, `playing`, `round_over` or `match_over`. The top-level `phase` and `winner` still describe the current round. A drawn round scores for nobody. `World` is unchanged, so the v1 parity tests are unaffected.

## Alternatives considered

- **Input as events (`jump_pressed`).** Closer to v1's key callbacks, but a lost or duplicated network message changes the game. Held state can be resent every tick safely.
- **`step(inputs, dt)` with a variable timestep.** Simpler client loop; makes physics depend on frame rate (v1's problem) and breaks determinism.
- **Renderer reads `World` objects directly.** Less copying; ties the renderer to Python classes and gives the network client a second code path.
- **Snapshot as dataclasses, or as a binary format.** Dataclasses are not language-neutral. Binary is smaller, but two players and a few bullets are about 500 bytes of JSON, and JSON can be read in a browser console.
- **Y-down coordinates to match pygame.** Would change every v1 constant's sign and the map file, for no gain in the rules.

## Consequences

- The renderer needs no knowledge of physics, and the server needs no knowledge of drawing.
- `snapshot()` has no cosmetic state (clouds, particles, camera). Those belong to the renderer.
- Animation timing and sprite sizes live in the renderer. Collision sizes are in the snapshot (`w`, `h`).
- The snapshot is not a save file: it leaves out internal state (wall-jump flags, cooldowns), so a world cannot be rebuilt from it. Prediction or reconnects will need a fuller state export later.
- Player ids are `p1` (v1's WASD player, left spawn) and `p2` (v1's numpad player, right spawn).

## Settled on 2026-11-16

- A bullet may hit the player who fired it, as in v1. It almost never happens.
- Round end keeps v1's order: damage dealt by a player later in the order ends the round one tick later.

## Open for the interface session

- Whether `draw` should receive the previous snapshot too, instead of the renderer keeping it.
