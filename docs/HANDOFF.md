# Handoff

Last updated: 2026-11-16, evening, Cairo

## Status

`main` holds Phase 0, Phase 1 and the playable part of Phase 2: `gg_core` (headless rules matching v1 tick for tick), `gg_client` (pygame-ce, sprites, sound, best of three) and the browser build, which is deployed by GitHub Actions to https://aymanohm.github.io/project_gg/ . The original game is still in the repo; its removal (PR #38) is held until Ayman has compared the two. Day-to-day work merges into the `phase-2` branch; `main` moves only at milestones. Phase 2 was merged into `main` on 2026-11-16 (#49) and `deploy-web` was run by hand afterwards, so the public page shows that build (menu, four levels, dash). No version tag exists yet, so no desktop build has been published. Nobody has play-tested or listened to the rewrite yet.

## Branches and PRs

- **`main`**: milestones only. Merged so far: #26 (Phase 0), #28 (Phase 1; it contains #29–#37), #27 (pygbag spike), #41 (browser build and sound; it replaced #39 and #40, which are closed), #49 (Phase 2; it contains #43–#48).
- **`phase-2`**: the integration branch. Open PRs against it and merge them there when CI is green.
- **[#38](https://github.com/AymanOHM/project_gg/pull/38) `chore/remove-v1-code`**: open, held. Do not merge. It is out of date with `main` and will need `main` merged into it, or redoing, when Ayman gives the go-ahead (`docs/issues` no longer has its checklist; the PR description lists what it deletes).
- The `gh-pages` branch is a leftover from the first hand-published build. Pages no longer uses it.

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

### Made by Ayman (2026-11-16)

- **Hosting: web multiplayer with the same client on desktop.** Written up as `docs/adr/001-architecture-direction.md` (Accepted).
- **Backlog proposals B1–B14: all accepted** and applied to `docs/ROADMAP.md`. `docs/proposals/2026-11-16-backlog.md` is kept as the record.
- **1.6 (sprite renderer) moves to Ayman's column**, because 2.2 waits on it.
- **Go-ahead to publish the pygbag spike to GitHub Pages** for the static-hosting check.

### Made by Ayman (2026-11-16, second round)

- **Merging:** PRs may be merged into feature branches; `main` only at major milestones.
- **The second developer is out of the loop for now.** Do not wait for his review.
- **v1 removal is delayed:** keep PR #38 unmerged.
- **No play-test until Ayman is back;** carry on with the current behaviour.
- **Licences:** Ayman handles them at the end. Do not spend more time on them.
- **ADR-002 accepted.** Bullets may hit their shooter and round end keeps v1's order.
- **Pages source is GitHub Actions;** `main` is protected from deletion.
- **Menu (2.2) must look like the welcome screen** (white pixel lettering with a dark shadow).
- **Desktop builds (2.8) are approved.** Phase 3 still waits for the interface session.
- **Keep a learning journal** (`docs/JOURNAL.md`): the why and how of every change.

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

For the next model. Each step is one branch off `phase-2` and one PR into `phase-2`; merge it when CI is green. Add a `docs/JOURNAL.md` entry in every PR.

1. **2.2 menu and options: done** (PR #43). Not done: a pause screen inside a match (Esc goes straight back to the menu).
2. **2.4 levels: done** (`meadow`, `cliffs`, `towers`; rotation in `LEVEL_ORDER`). `tests/test_level_reachability.py` proves each player can reach the other's start on every level. The camera zooms out (up to 1.6x) when players are far apart; its cost in the browser is unmeasured.
3. **2.8 desktop builds: done** (`desktop/build.sh`, `release-desktop.yml`). The zips are attached to a release when a version tag such as `v2.0` is pushed; no such tag exists yet. Builds are unsigned.
4. **0.8, the rest: done.** 79 unused images deleted. Kept on purpose: `data/maps/` (source of the converted levels, which are not play-tested yet), `data/sfx/dash.ogg` (for 2.5) and `data/images/welcome.png` (only v1 loads it; delete it with v1 in PR #38). Licences are still unverified; Ayman handles them.
5. **2.5 dash: done.** Left Shift for p1, `.` for p2. Distance, duration and cooldown (`gg_core/constants.py`) are untested guesses; nobody has played it. A dash gives no protection from bullets.
6. **Milestone: done.** #49 merged into `main` and the page redeployed, both on Ayman's word. A version tag (which publishes the desktop zips) is still his call. New work keeps going to `phase-2` until he names the next integration branch.
7. **Do not start Phase 3** (server, protocol, matchmaker) without Ayman.

Every numbered step that could be done without Ayman is done. What is left needs him:

- **Play it** (task 2.9). Things to judge: the dash numbers, whether `cliffs` and `towers` are playable, the sound balance, the menu lettering, and the rewrite against v1 (which decides PR #38).
- **Small work that is in scope if he wants it:** a pause screen inside a match.
- **Phase 3** starts with the interface session and the matchmaker language decision.

After every step: update this file, run `uv run ruff check . && uv run ruff format --check . && uv run pytest -q`, commit, push, open the PR with the sections listed in `CLAUDE.md`.

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
