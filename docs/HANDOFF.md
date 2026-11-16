# Handoff

Last updated: 2026-11-16 (end of the first working session)

## Status

Phase 0 is done except the board, branch protection and licence verification. Phase 1 is implemented except the sprite renderer (1.6): `gg_core` runs headless, imports no pygame or OpenGL, passes a 10,000-tick test and reproduces the original game's movement and combat bit for bit on about 8,000 recorded ticks. A plain rectangle client makes it playable (`uv run python -m gg_client`). The pygbag spike says the browser client is feasible. Six PRs are open and stacked; nothing is merged. Two decisions wait for Ayman: the hosting direction and the backlog proposals.

## Open PRs — merge in this order

Each PR is based on the one above it. After merging one, GitHub retargets the next to `main`. Use squash merge only if you merge strictly top to bottom; otherwise use a merge commit so the stack does not conflict.

| # | Branch | Tasks | Notes for the reviewer |
|---|---|---|---|
| [#26](https://github.com/AymanOHM/project_gg/pull/26) | `chore/repo-cleanup` | 0.3, 0.4, 0.5, 0.8 (part) | Deletes 45 MB. Roadmap amendments are in here |
| [#27](https://github.com/AymanOHM/project_gg/pull/27) | `spike/pygbag` | 1.10 | Based on #26, independent of #28–#31. Read `docs/spikes/pygbag.md` |
| [#28](https://github.com/AymanOHM/project_gg/pull/28) | `feat/core-interfaces` | 1.1, 1.2, 1.3, 1.9 | Based on #26. Read ADR-002 first |
| [#29](https://github.com/AymanOHM/project_gg/pull/29) | `feat/world-step` | 1.4, 1.5, 1.7, 1.11 | Based on #28. The core of the session |
| [#30](https://github.com/AymanOHM/project_gg/pull/30) | `feat/debug-client` | — | Based on #29. Playable client |
| [#31](https://github.com/AymanOHM/project_gg/pull/31) | `docs/handoff-and-backlog` | — | Based on #30. This file, proposals, issue bodies |
| [#32](https://github.com/AymanOHM/project_gg/pull/32) | `docs/asset-licences` | 0.8 (part) | Based on #31. `CREDITS.md` with what could be verified |
| [#33](https://github.com/AymanOHM/project_gg/pull/33) | `test/readable-rules` | 1.8 | Based on #32. Tests only; `gg_core` unchanged |
| [#34](https://github.com/AymanOHM/project_gg/pull/34) | `feat/match-rounds` | 2.1 (rules part) | Based on #33. `Match`: countdown, best of three, score, level rotation |
| [#35](https://github.com/AymanOHM/project_gg/pull/35) | `docs/adr-001-and-roadmap` | 0.1 | Based on #34. ADR-001 accepted; proposals B1–B14 applied to the roadmap |
| [#36](https://github.com/AymanOHM/project_gg/pull/36) | `feat/sprite-renderer` | 1.6a | Based on #35. `SpriteRenderer`; view a frame by running the client |
| [#37](https://github.com/AymanOHM/project_gg/pull/37) | `feat/clouds-and-screens` | 1.6b | Based on #36. Clouds, welcome screen, win screens |
| [#38](https://github.com/AymanOHM/project_gg/pull/38) | `chore/remove-v1-code` | 1.12 | Based on #37. Deletes `game.py`, `scripts/`, `map.json`, PyOpenGL. **Play v1 and the rewrite side by side before merging this one** (check out `feat/clouds-and-screens`) |
| #39 | `feat/web-build` | 2.6, 2.7 | Based on #38. `web/build.sh`, CI web build, deploy workflow. Live at https://aymanohm.github.io/project_gg/play/ |

#27 and #28 both follow #26 and both touch `pyproject.toml`/`uv.lock` (only #27 does); no conflict is expected.

## Done this session

| Task | What |
|---|---|
| 0.3 | `v1` tag and [release](https://github.com/AymanOHM/project_gg/releases/tag/v1) on `af4e694`; `libs/`, `.idea/`, `.rar`, `.psd`, `desktop.ini` removed |
| 0.4 | Python 3.12, `pyproject.toml`, `uv.lock` |
| 0.5 | ruff, pre-commit, GitHub Actions |
| 0.8 | `LICENSE`, `CREDITS.md` (licences not yet verified) |
| Gate 0 | The old game starts on the M3 Mac (`uv run python game.py`). Start-up only was checked |
| 1.10 | pygbag spike and write-up |
| 1.1, 1.2, 1.3, 1.9 | `gg_core` package, `FixedStep`, `PlayerInput`, level format and loader, `Renderer` protocol, ADR-002 (Proposed) |
| 1.4, 1.5, 1.7 | `World.step`, `World.snapshot`, bullet fix, `p1`/`p2` |
| 1.11 | `RandomBot` |
| 1.8 | `tests/test_rules.py` |
| 2.1 (rules part), 2.4 (rotation logic) | `gg_core.Match`; the debug client plays best of three. Menu and "back to menu" are client work, still open |
| — | v1 trace recorder and parity tests; debug client |

## Decisions

### Made by Ayman (2026-11-16)

- `v1` is `origin/main` at `af4e694`.
- Reference frame rate is 60 fps: one old frame is one tick. Parity need not be strict.
- Roadmap amendments approved and applied: relaxed Phase 0 gate, task 0.8, task 4.9.
- A separate roadmap task for golden-master traces was not approved. The traces exist as test tooling inside the refactor PR instead.

### Made by Ayman (2026-11-17)

- **Hosting: web multiplayer with the same client on desktop.** Written up as `docs/adr/001-architecture-direction.md` (Accepted).
- **Backlog proposals B1–B14: all accepted** and applied to `docs/ROADMAP.md`. `docs/proposals/2026-11-16-backlog.md` is kept as the record.
- **1.6 (sprite renderer) moves to Ayman's column**, because 2.2 waits on it.
- **Go-ahead to publish the pygbag spike to GitHub Pages** for the static-hosting check.

### Pending — Ayman

- **Matchmaker language** (Node or Python): Ayman asks his friend. Nothing built depends on it.
- **ADR-002** is Proposed. It has open questions for the interface session.
- **Licence of the tutorial resources** (see `CREDITS.md`).

### Decided without Ayman — please confirm

| Decision | Why | To undo |
|---|---|---|
| `ROADMAP.md` moved from the repo root to `docs/ROADMAP.md` | The brief names that path | `git mv` |
| The pre-session working tree is in `git stash` | It was CRLF noise on 3,104 files plus one blank line | `git stash drop` discards it; it is safe to drop |
| `LICENSE` is MIT, "Ayman Osama and the Project GG contributors" | The README already said MIT | Edit the file |
| PyOpenGL and Pillow are in a `legacy` dependency group | Only v1 needs them | `pyproject.toml` |
| ruff skips `game.py` and `scripts/` | Frozen reference code | `pyproject.toml` |
| `p1` = WASD player (left spawn), `p2` = numpad player | The README says so; v1's code and win screens disagreed | Rename in `gg_core` and re-record |
| Fire cooldown is 15 ticks | 250 ms at 60 Hz | `gg_core/constants.py` and re-record |
| Match flow: 3 s countdown with inputs ignored, 2 s pause after a round, first to 2, draws score for nobody | No v1 behaviour to copy; these are defaults on `Match(...)` | Constructor arguments |
| A held jump key jumps once | v1 re-jumped on OS key repeat, which differs per machine | `World.step` |
| v1's quirks are kept (self-hit possible, one-tick asymmetry at round end, gun one tick behind) | Bit-for-bit parity; listed in proposal B13 | `gg_core/world.py` and re-record |
| `map.json`'s `offgrid` tiles are dropped | v1 drew them far off-screen | `tools/convert_v1_map.py` |
| Player 2 also has arrow keys and Right Shift | The MacBook has no numpad | `gg_client/keyboard.py` |
| pygbag is in a `web` dependency group, not installed by default | Keeps CI and `uv sync` small | `pyproject.toml` |

## Tasks taken from the friend's column, and why

| Task | Why |
|---|---|
| 0.5 CI, ruff, pre-commit | The refactor needed green CI under it from the first PR |
| 1.10 pygbag spike | It gates the hosting decision, which gates ADR-001 |
| 1.11 headless bot | The 10,000-tick gate test needs an input generator; it is 20 lines |
| 1.8 | Characterization had to come before the refactor. The trace tests cover every mechanic; `tests/test_rules.py` then states the rules in plain numbers, which took minutes once the core existed |

Not taken: 0.2 (board), 0.6 (branch protection), 0.7 (dev container), 1.6 (renderer). The debug client is deliberately rectangles only, so 1.6 is still a whole task.

## Next steps

For the next model. Do them in order; each is one branch and one PR. Do not start a step whose precondition is not met; go to the next one.

1. **Nothing can merge until Ayman reviews.** If PRs #26–#31 are still open, do not rebase or force-push them. Fix review comments with new commits on the same branch.
2. **0.8 licence check: partly done** (branch `docs/asset-licences`). The health bar pack is CC BY 4.0. The tutorial resources have no licence on their download page; only Ayman can settle this, by checking the tutorial video's description or asking the author. Do not repeat the web search. The unused-asset deletion in `docs/issues/0.8-asset-licences.md` is still to do.
3. **1.8 readable rule tests: done** (`tests/test_rules.py`, branch `test/readable-rules`).
4. **2.10 audio to OGG.** Follow `docs/issues/2.10-audio-to-ogg.md`. Precondition: Ayman approved proposal B7.
5. **2.7 static-hosting check.** Follow `docs/issues/2.7-static-hosting-check.md`. Precondition: #27 merged. Publishing to GitHub Pages needs Ayman's explicit go-ahead.
6. **1.6a sprite renderer.** Follow `docs/issues/1.6a-sprite-renderer.md`. Precondition: Ayman confirms his friend is not doing it.
7. **ADR-001.** Precondition: Ayman has chosen the hosting option. One page in `docs/adr/001-architecture-direction.md`, same headings as ADR-002, status Accepted, using the option table and the spike numbers above.
8. **Apply approved backlog proposals** to `docs/ROADMAP.md`, one commit, listing the proposal IDs in the message. Apply only the IDs Ayman names.

After every step: update this file (Status, Done, Open PRs, Next steps), run `uv run ruff check . && uv run ruff format --check . && uv run pytest -q`, commit, push, open the PR.

## Known risks and traps

Raw material for the write-ups: what broke and how it was handled.

- **PR #25 was merged into `feature_testing`, not `main`.** Its only code change removed four commented lines. `main` and `v1` do not contain it, and lose nothing.
- **3,104 "modified" files** on the Mac were Windows line endings. `.gitattributes` now forces LF.
- **The old game does run on Apple Silicon** with the system GLUT framework and PyOpenGL from PyPI; no fiddling was needed. It opens fullscreen with no window controls: Q quits.
- **v1's physics speed depended on the machine** (per-frame physics on a 2 ms timer) while its fire cooldown used wall-clock time. The port fixes both to ticks.
- **v1 could be tested without a window.** Stubbing about twenty OpenGL names is enough to import `scripts/classes.py` and call `player.move()` in a loop. That turned "same feel" into an exact comparison, and the port matched on the first run.
- **v1's players spawn inside solid tiles** and are pushed up onto them over the first few ticks. p1 ends up in a tunnel at (80, 720), p2 on a narrow platform at (900, 450). Scripted tests must wait about 90 ticks before doing anything.
- **v1's bullet list bug** (removing while iterating) is fixed in `World` and patched in the recorder, so traces and port agree.
- **pygbag builds contain no runtime.** `build/web` is 80 KB; Python and pygame-ce come from a third-party CDN at page load. A plain static server on localhost produced a blank page with a 404 for the pygame-ce wheel; pygbag's own test server is needed locally. Static hosting is untested.
- **`websockets` does not exist in the browser.** The spike used JavaScript's `WebSocket` through `platform.window.eval` and polled it once per frame, which adds up to one frame of latency.
- **`data/maps/0–2.json` are not usable as they are** (Y-down, 16 px, no spawns).
- **The release notes for `v1` briefly @-mentioned the three other contributors.** That was edited out within a minute; GitHub may still have notified them.
- **Chrome automation hung** on a "Leave site?" dialog from the pygbag page after the measurements. A tab on `localhost:8000` may still be open; close it by hand.
- **The spike leaves untracked files** in `spikes/pygbag/data` and `spikes/pygbag/build` on branches other than `spike/pygbag`. They are ignored there; do not `git add -A` on other branches.
