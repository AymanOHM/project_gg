# Handoff

Last updated: 2026-11-16

## Status

Phase 0 cleanup is in review (`chore/repo-cleanup`). `v1` is tagged and released. The old game starts on the M3 Mac after `uv sync`. Nothing from Phase 1 exists yet.

## Done this session

| Task | What | Where |
|---|---|---|
| 0.3 | `v1` tag + GitHub release on `af4e694` | https://github.com/AymanOHM/project_gg/releases/tag/v1 |
| 0.3 | Removed `libs/`, `.idea/`, the `.rar`, the `.psd`, `desktop.ini` | `chore/repo-cleanup` |
| 0.4 | Python 3.12 pin, `pyproject.toml`, `uv.lock` | `chore/repo-cleanup` |
| 0.5 | ruff, pre-commit, GitHub Actions (lint + pytest) | `chore/repo-cleanup` |
| 0.8 | `LICENSE` (MIT) and `CREDITS.md`; asset licences still unverified | `chore/repo-cleanup` |

## Open PRs and review notes

- `chore/repo-cleanup`: see the PR description.

## Decisions

**Made by Ayman (2026-11-16)**

- `v1` is `origin/main` at `af4e694`.
- Reference frame rate for "same feel" is 60 fps: one old frame is one tick. Parity does not have to be strict; make reasonable choices.
- Roadmap amendments approved and applied: relaxed Phase 0 gate, task 0.8, task 4.9.
- Not approved: a separate roadmap task for golden-master traces. Characterization tests are written as part of the refactor instead.

**Pending**

- Hosting direction (web multiplayer, desktop-only backend, or hybrid). Waits for the pygbag spike.
- Matchmaker language (Node vs Python). Ayman asks his friend.

**Decided without Ayman — please confirm**

- `ROADMAP.md` was untracked at the repo root; it now lives at `docs/ROADMAP.md`.
- PyOpenGL and Pillow are in a `legacy` dependency group, installed by default, skipped in CI.
- ruff does not lint `game.py` or `scripts/` (frozen v1 reference code).

## Tasks taken from the friend's column, and why

- **0.5** (ruff, pre-commit, CI): the refactor needs green CI under it from the first PR.

## Next steps

See the end of this file once the session wraps up. Current order: pygbag spike (1.10), ADR-001, ADR-002, `gg_core` refactor.

## Known risks and traps

- **PR #25 was merged into `feature_testing`, not `main`.** Its only code change removed four commented lines; it also added two images. `main` and `v1` do not contain it. `feature_testing` is 17 commits behind `main`.
- **The local working tree had 3,104 "modified" files.** They were CRLF line endings from a Windows checkout, plus one blank line in `game.py`. They are in `git stash` (`stash@{0}`, "pre-sprint working tree"). It is safe to drop: `git stash drop`. A `.gitattributes` now forces LF.
- **The old game runs on macOS** with the system GLUT framework and PyOpenGL 3.1.x. It opens fullscreen. Only start-up was checked (no errors for 10 seconds); nobody has looked at the picture yet.
- **Physics in v1 is per rendered frame**, on a 2 ms GLUT timer, so game speed depended on the machine. The fire cooldown is 250 ms of wall-clock time.
- **`data/maps/0–2.json` are not drop-in maps.** They use the tutorial's Y-down layout and have no spawn points for this game. `map.json` (Y-up, 45 px tiles, its `tile_size: 16` field ignored) is the only map v1 loads.
- **Asset licences are unverified** (`CREDITS.md`).
