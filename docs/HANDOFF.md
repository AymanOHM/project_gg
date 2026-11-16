# Handoff

Last updated: 2026-11-16, 07:00 Cairo

## Status

Phases 0 and 1 are implemented, and most of Phase 2's gate is met: the game is rebuilt as `gg_core` (headless rules, matching v1 tick for tick) plus `gg_client` (pygame-ce, sprites, sound), plays a best of three, and runs in a browser at https://aymanohm.github.io/project_gg/play/ . The v1 code is removed on the last branches. **Fifteen PRs (#26–#40) are open and stacked; nothing is merged or reviewed.** The hosting direction is decided (ADR-001) and the backlog proposals are applied to the roadmap.

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
| [#39](https://github.com/AymanOHM/project_gg/pull/39) | `feat/web-build` | 2.6, 2.7 | Based on #38. `web/build.sh`, CI web build, deploy workflow. Live at https://aymanohm.github.io/project_gg/play/ |
| [#40](https://github.com/AymanOHM/project_gg/pull/40) | `feat/audio` | 2.3, 2.10 | Based on #39. OGG audio, music and effects, `events` in the snapshot. **Listen to it**: nobody has heard the result |

The stack is one line, #26 → #28 → #29 → … → #40, with #27 (the spike) as a side branch off #26. **#27 conflicts with #38 and #39** in `pyproject.toml` and `uv.lock` (all three change dependency groups). Merge #27 last: merge `main` into it, keep `main`'s `pyproject.toml`, run `uv lock`, commit.

Before merging #38, play v1 and the rewrite side by side from the #37 branch; after #38 the original only exists at tag `v1`.

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
| 0.1 | ADR-001 accepted |
| 1.6a, 1.6b | Sprite renderer, clouds, welcome and win screens |
| 1.12 | v1 code and OpenGL dependencies removed |
| 2.6, 2.7 | pygbag build script, CI web build, Pages deploy workflow; a hand-published build is live |
| 2.3, 2.10 | Music and effects; audio converted to OGG |

## Decisions

### Made by Ayman (2026-11-16)

- `v1` is `origin/main` at `af4e694`.
- Reference frame rate is 60 fps: one old frame is one tick. Parity need not be strict.
- Roadmap amendments approved and applied: relaxed Phase 0 gate, task 0.8, task 4.9.
- A separate roadmap task for golden-master traces was not approved. The traces exist as test tooling inside the refactor PR instead.

### Made by Ayman (2026-11-16)

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

For the next model. Do them in order; each is one branch and one PR, branched from the newest open branch (`feat/audio`) or from `main` once the stack is merged. Do not start a step whose precondition is not met; go to the next one.

1. **Review fixes come first.** If Ayman or his friend comment on PRs #26–#40, fix with new commits on that PR's branch. Never rebase or force-push. After changing a lower branch, merge it upward into each branch above it, in order, and push.
2. **0.8, the rest:** delete assets the game never loads. Follow the last checkbox of `docs/issues/0.8-asset-licences.md`; `web/build.sh` lists exactly what the game loads. Keep `data/maps/` and `data/sfx/dash.ogg`.
3. **2.4 convert the three maps.** For each of `data/maps/0.json`, `1.json`, `2.json`: write a level file `data/levels/<name>.json` in the format of `gg_core/level.py`. These maps are Y-down, so negate each tile's `y`; keep only `grass` and `stone` tiles plus `decor`; use `tile_size` 45; choose two spawn points that stand on solid ground at least 10 tiles apart; set `kill_y` 300 px below the lowest tile. Add a test that each level loads and that both players are standing (`hit_down`) after 200 idle ticks. Then pass all levels to `Match([...])` in `gg_client/__main__.py`, load each in the renderer when `snapshot["match"]["level"]` changes, and add the files to `web/build.sh` (already copied: it copies `data/levels`). Precondition: none.
4. **2.2 menu and options** (keybinds, volume, fullscreen). Precondition: ask Ayman how much he wants; it is the largest remaining client task.
5. **2.8 desktop builds** with PyInstaller in CI. Precondition: none, but it needs macOS and Windows runners; ask Ayman before adding paid minutes.
6. **Switch Pages to the deploy workflow.** Precondition: #39 merged and Ayman has set Settings → Pages → Source to "GitHub Actions". Then run the "Deploy web build" workflow by hand and check the site.
7. **Do not start Phase 3** (server, protocol, matchmaker) without Ayman: the interface session and the matchmaker language come first.

After every step: update this file (Status, Done, Open PRs, Next steps), run `uv run ruff check . && uv run ruff format --check . && uv run pytest -q`, commit, push, open the PR with the sections listed in `CLAUDE.md`.

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
- **GitHub Pages is served from a hand-pushed `gh-pages` branch** (`/play/` and `/spike/`). It is not updated automatically; `deploy-web.yml` replaces it once Pages is switched to GitHub Actions.
- **`web/build.sh` failed in CI with "Permission denied".** This Mac has `core.filemode` off, so `chmod +x` was not recorded; `git update-index --chmod=+x` fixed it.
- **ffmpeg here has no libvorbis.** The OGG files were made with ffmpeg's built-in Vorbis encoder. Nobody has listened to them.
- **A point-blank shot never appears in `snapshot["bullets"]`** (created, hit and removed in one tick). That is why the snapshot has `events`.
- **Untracked files to leave alone:** `spikes/` (on every branch except `spike/pygbag`) and `test.py` (an old scratch file of Ayman's). Never `git add -A` at the repo root.
