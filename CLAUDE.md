# Project GG

**Read `docs/ROADMAP.md` and `docs/HANDOFF.md` before doing anything.** The roadmap is the plan; the handoff says where the work stands and lists the exact next steps.

## Goal

Turn a 2024 PyOpenGL course game (a 2D two-player platform shooter, preserved at tag `v1`) into a DevOps portfolio project:

- `gg_core`: headless rules package. Pure Python, standard library only.
- `gg_client`: pygame-ce client for desktop and, through pygbag, the browser.
- `gg_server`: authoritative WebSocket game server (asyncio), later on Kubernetes with Agones.

The server is authoritative: clients send inputs only. Interfaces between components stay language-neutral (versioned JSON), because the matchmaker may be written in Node or Python.

## Layout

| Path | What it is |
|---|---|
| `data/` | Art, audio, maps |
| `gg_core/` | Headless rules: `World` (one round), `Match` (rounds, countdown, score), inputs, level loader, fixed-step clock, bots |
| `gg_client/` | `Renderer` protocol, `SpriteRenderer` (the game's renderer), `DebugRenderer` (collision boxes, `--debug`), camera, keyboard map, `python -m gg_client` |
| `data/levels/` | Levels in the `gg_core` format. `arena.json` is the original game's map |
| `tests/` | pytest. `tests/golden/v1_traces.json.gz` holds traces recorded from v1 |
| `web/` | Browser build: `main.py` (pygbag entry point) and `build.sh`. Output goes to `build/web-app/` (ignored) |
| `tools/` | `convert_v1_map.py` (v1 map format to level format) |
| `spikes/` | Throwaway experiments. Do not build on them |
| `docs/ROADMAP.md` | Phases, tasks, gates, backlog. Source of truth. |
| `docs/HANDOFF.md` | Current status and ordered next steps |
| `docs/adr/` | Architecture decision records, one page each |
| `docs/spikes/` | Spike write-ups |
| `docs/issues/` | Ready-to-paste GitHub issue bodies |

## Commands

```bash
uv sync                      # install Python 3.12 + dependencies
uv run pytest -q             # tests
uv run ruff check .          # lint
uv run ruff format .         # format
uv run python -m gg_client   # the rewrite: local best of three (Esc quits; --debug for collision boxes)
./web/build.sh --serve       # browser build on http://localhost:8000 (plain static servers do not work locally)
```

CI (`.github/workflows/ci.yml`) runs ruff, pytest and the web build on every PR. Keep it green. `deploy-web.yml` publishes the web build to GitHub Pages on a version tag.

## Rules for `gg_core`

- No imports of pygame, OpenGL or any third-party package. It must run in CPython and in pygbag's WebAssembly Python.
- Deterministic: no wall-clock time, no unseeded randomness, no global state. Time is counted in ticks (60 per second).
- World coordinates are Y-up, in pixels, with a rectangle's position at its bottom-left corner (as in v1). Renderers convert to screen space.
- Behaviour must match v1 unless a roadmap task says otherwise. `tests/test_v1_parity.py` compares `World` with traces recorded from the v1 code on every tick. The v1 code and the recorder are gone from `main` (they are at tag `v1` and in the history), so the traces cannot be re-recorded casually. If a task changes behaviour on purpose, say so in the PR and delete only the scenarios it invalidates, replacing them with tests in `tests/test_rules.py`. Never edit the trace file by hand and never loosen the comparison to make a test pass.
- Do not edit `data/levels/arena.json`: the traces depend on it. Add new levels as new files.
- The interfaces are described in `docs/adr/002-core-interfaces.md`. Renderers and network code use `World.snapshot()` dicts only, never `World` objects.

## Git rules (non-negotiable)

- Commits are authored and committed as Ayman (`git config user.name` → `AymanOHM`). If the identity is different, stop and ask.
- **No AI attribution anywhere**: no `Co-Authored-By` trailer, no "Generated with" line, no session links, in commits, PR titles, PR bodies or release notes. After committing, check with `git log -1 --format=full`.
- Short-lived branches off `main`: `chore/…`, `feat/…`, `refactor/…`, `spike/…`, `docs/…`. Conventional commits, small steps.
- Push branches and open PRs. **Never merge, never push to `main`, never force-push a shared branch, never rewrite history.**
- Every PR description has: what changed, why, how to test, risks, roadmap task IDs.
- Do not @-mention people in PRs, issues or releases unless Ayman asks.

## Working rules

- Roadmap changes (phases, gates, scope, tasks, owners, locked decisions) are proposed to Ayman, then applied to `docs/ROADMAP.md` only after he approves.
- Reversible implementation details: decide, and note them in the PR description.
- Open decisions that are not yours to make: matchmaker language (Node vs Python) and hosting direction (see `docs/HANDOFF.md`).
- Update `docs/HANDOFF.md` after every PR or decision.
- Quality bar: working code with tests, ruff-clean, behaviour preserved. No speculative abstraction.
