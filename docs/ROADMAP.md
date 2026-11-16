# Project GG — Roadmap & Backlog

2026-11-12 · @Ayman

## Summary

**Don't fix the PyOpenGL renderer. Replace it.** The game is 2D sprites on a grid, so OpenGL adds nothing here. Port rendering to pygame-ce, which runs on desktop *and* in the browser through pygbag. That gives you both directions from one Python codebase instead of having to choose one.

The plan in one line: pull the game rules out into a headless core, give it a pygame-ce client (desktop + web), and run that same core as an authoritative WebSocket game server on Kubernetes with Agones. About 7 phases over roughly 15 weeks, in 2-week sprints.

**Decision to lock in Sprint 0 (ADR-001):** this direction. Everything after Phase 1 depends on it.

**Strongest case against it:**

- **OpenGL was the original point.** This was a graphics-course game. Dropping OpenGL throws away the part that was coursework. If learning modern GL (VBOs, shaders) still matters to you, it goes in the icebox as a separate renderer behind the same interface, not on the critical path.
- **pygbag has costs.** Builds are large (they ship a Python runtime), run slower than native, and allow networking only over WebSockets, not raw sockets or threads. The design below accepts all three.
- **Netcode for a platformer is hard.** With server authority and no prediction, a player in Cairo on an EU server will feel roughly 60–100 ms of input delay. That's fine for a v1 and fixable later with client prediction (icebox). I'm moderately confident in that latency range; measure it in Phase 3.

## Right now: Sprint 0

Sprint 0 runs 2026-11-15 to 2026-11-19. Its goal is Phase 0's gate: the repo runs on the Mac, CI is green, the board is live and the two of you agree on how you work. Sprint 1 follows from 2026-11-22 to 2026-12-03.

### Meetings

| When | Meeting | Length | What comes out of it |
|---|---|---|---|
| Start of Sprint 0 | **Kickoff + Sprint 0 planning:** walk through this doc; settle Node vs Python for the matchmaker; agree the area split (rules + physics vs renderer + assets); each of you states real hours per week; agree the working agreement and meeting days | 90 min | ADR-001 accepted, board loaded with Phase 0 issues, capacity in hours |
| End of Sprint 0 | **Interface design session:** define `World.step(inputs)`, the snapshot shape and the `Renderer` interface before anyone touches the refactor | 60 min | ADR-002 + stub interfaces merged, so you can work in parallel without conflicts |
| End of Sprint 0 | **Review + retro, then Sprint 1 planning** | 30 + 15 + 45 min | Gate demoed; one thing to change; Sprint 1 issues picked to fit your capacity |
| Every working day | **Async check-in** in your chat: done / next / blocked, 3 lines | 2 min | Blockers surface the same day |
| Mid-sprint, from Sprint 1 | **Backlog refinement:** size and split the next sprint's issues | 30 min | Next planning takes 30 min, not 2 hours |

From Sprint 1 on, every sprint repeats the same rhythm: planning on day 1, refinement mid-sprint, review + retro on the last day.

### This week's checklist

- [ ] Ayman: book the kickoff with your friend
- [ ] Ayman: ask him Node or Python for the matchmaker, before the kickoff
- [ ] Ayman: protect `main` (PR + 1 review + CI) — task 0.6
- [ ] Ayman: tag the current state as `v1` with a GitHub release
- [ ] Friend: create the GitHub Projects board and load the Phase 0 issues — task 0.2
- [ ] Split the rest of Phase 0 (0.3–0.7) between you at the kickoff
- [ ] Both: book the interface design session and the end-of-sprint review

## Repo audit

`AymanOHM/project_gg` holds about 1,070 lines of Python (`game.py` + 8 modules in `scripts/`). The last commit was May 2024. Rendering and game logic are tangled together, so the game can't run headless as a server until they're separated.

| Area | Finding | Impact | Fix in |
|---|---|---|---|
| Rendering | `Texture.bind()` calls `glTexImage2D` on every draw, re-uploading every sprite to the GPU every frame | Biggest performance problem | Phase 1 (port) |
| Rendering | Texture IDs are `random.randint(1, 1000)`; the ID `glGenTextures` returns is ignored | Textures can collide | Phase 1 |
| Rendering | `player.update_tex()` creates a new `Texture` every frame | GPU memory leak | Phase 1 |
| Rendering | Immediate mode (`glBegin`/`glEnd`), GLUT window, no VBOs or shaders | Legacy GL; GLUT is fragile on macOS | Phase 1 (dropped) |
| Game loop | `glutTimerFunc(2)` drives `draw()`; physics moves a fixed amount per frame | Game speed depends on the machine; no fixed timestep | Phase 1 |
| Coupling | `player.move()` draws the health bar; `Bullet.update()` reaches into `game.player` and `game.enemy` | Can't run without a window or with more than 2 players | Phase 1 |
| Bugs | `Bullets.update()` removes from the list while iterating it | Bullets get skipped | Phase 1 |
| Bugs | No restart after a round (stage 2 is a dead end; only Q exits) | Not a complete game loop | Phase 2 |
| Naming | `player` is controlled by the numpad, `enemy` by WASD; the win screen keys off `enemy.health` | Confusing; error-prone in netcode | Phase 1 |
| Content | `data/sfx` and `data/music.wav` exist but are never loaded; `data/maps/0–2.json` unused (root `map.json` is used); `editor.py` uses a separate pygame stack | Unfinished features | Phase 2 |
| Repo | `libs/` vendors 45 MB of Windows-only Python 3.7 binaries (`.pyd`, `.dll`); `.idea/`, a `.rar` and a `.psd` are committed; `.git` is 29 MB | Only runs on Windows + Py3.7; won't run on your M3 Mac | Phase 0 |
| Quality | No tests, CI, packaging, or Python version pin | Nothing to deploy yet | Phase 0 |

Worth keeping: the movement feel (double jump, wall jump, fast fall), `Rect` collision, the tilemap format, and all the art.

## Target architecture

One Python rules package, `gg_core`, runs in three places: the desktop client, the browser client and the game server. The server is authoritative: clients send inputs only, so the server decides every hit.

_[diagram: target architecture · client, matchmaker, Agones, game servers]_

The matchmaker returns the allocated server's address and a join token. Everything after that is a direct WebSocket between client and game server. The cluster runs locally on k3d until Phase 4 moves it to a cloud provider.

## Phases

Seven phases over 16 weeks. The game work comes first and is timeboxed to 6 weeks, because everything after it is DevOps work on top of it. Each phase ends with a gate: a demo you can run, not a feeling that it's done.

_[diagram: roadmap · 7 phases over 16 weeks, with gates]_

Sizes: **S** ≤ 1 day, **M** 2–3 days, **L** about a week. Work is split equally: each person takes both game and DevOps tasks every sprint. In the refactor, split by area so you don't edit the same code: one owns rules and physics, the other the renderer and assets, with the interface agreed first. Owners below are a starting suggestion; rebalance at sprint planning. Both review everything.

### Phase 0 — Foundations (Sprint 0, week 1)

**Goal:** a clean repo that runs on Mac and Linux, plus the board and the key decision. **Gate:** a fresh clone → `uv sync` → the old game runs on the M3 Mac, or its movement and combat behaviour is captured as characterization tests; CI is green on `main`.

| ID | Task | Owner | Size |
|---|---|---|---|
| 0.1 | Write ADR-001: pygame-ce + pygbag client, authoritative server, Agones | Both | S |
| 0.2 | GitHub Projects board, labels, issue templates; load this backlog as issues | Friend | S |
| 0.3 | Tag `v1` + GitHub release, then one normal commit on `main` deleting `libs/`, `.idea/`, the `.rar` and the `.psd` (no history rewrite) | Ayman | S |
| 0.4 | Pin Python 3.12; `pyproject.toml` with uv; real dependencies instead of vendored ones | Ayman | S |
| 0.5 | ruff + pre-commit; GitHub Actions running lint + pytest on every PR | Friend | M |
| 0.6 | Branch protection: PR, 1 review and green CI to merge | Friend | S |
| 0.7 | Dockerfile / dev container for the toolchain | Friend | M |
| 0.8 | `LICENSE` + `CREDITS.md`; verify the art and audio licences before any public web deploy | Ayman | S |

### Phase 1 — Engine refactor (Sprints 1–2, weeks 2–4)

**Goal:** the rules live in a headless `gg_core` package and pygame-ce draws them; it plays the same as before. **Gate:** `gg_core` imports no pygame or OpenGL; a test runs 10,000 ticks headless; local 2-player plays like the original.

| ID | Task | Owner | Size |
|---|---|---|---|
| 1.1 | Layout: `gg_core/` (rules), `gg_client/` (pygame-ce), `gg_server/` (later) | Ayman | S |
| 1.2 | Fixed timestep: 60 ticks/s with an accumulator; physics in units per tick | Ayman | M |
| 1.3 | Input as commands (`left, right, jump, fire, fast_fall`) instead of GLUT key callbacks | Ayman | M |
| 1.4 | Move entities, collision, bullets and health into `World.step(inputs)`; no drawing in logic | Ayman | L |
| 1.5 | `World.snapshot()` → plain dict (needed for netcode) | Ayman | S |
| 1.6 | pygame-ce renderer: sprite and animation cache, camera, tilemap, clouds, HUD | Friend | L |
| 1.7 | Fix the bullet-removal bug; rename `player`/`enemy` to `p1`/`p2` | Ayman | S |
| 1.8 | pytest: jump, wall jump, collision, bullet hit, round end | Friend | M |
| 1.9 | One map format + loader with validation | Ayman | S |
| 1.10 | Spike: one map rendering in a browser via pygbag (de-risks Phase 2) | Friend | S |
| 1.11 | Headless bot that generates inputs (reused in Phase 5 for load tests) | Friend | S |

### Phase 2 — Game polish (Sprint 3, weeks 5–6, timeboxed)

**Goal:** a complete local match that also runs in a browser. **Gate:** a public GitHub Pages URL where two people on one keyboard play a full best-of-3. This is your first deployment.

| ID | Task | Owner | Size |
|---|---|---|---|
| 2.1 | Round loop: countdown, best-of-3, restart, back to menu | Ayman | M |
| 2.2 | Menu + options: keybinds, volume, fullscreen | Ayman | M |
| 2.3 | Wire up the SFX and music already in `data/` | Friend | S |
| 2.4 | Map rotation across the 3 maps in `data/maps` | Ayman | S |
| 2.5 | One new mechanic from the README roadmap: dash | Ayman | M |
| 2.6 | Async game loop + pygbag build | Friend | M |
| 2.7 | CI: build the web bundle, deploy to GitHub Pages on tag | Friend | M |
| 2.8 | CI: PyInstaller desktop builds for Windows and macOS as release assets | Friend | M |
| 2.9 | Playtest with ~5 people; fix the top 3 complaints | Both | S |

Cut line: anything not listed here goes to the icebox, however small it looks.

### Phase 3 — Online multiplayer (Sprints 4–5, weeks 7–9)

**Goal:** two people on different machines play one match through your server. **Gate:** `docker compose up` on one cheap VPS; one browser and one desktop player finish a match; round-trip time and tick time are logged.

| ID | Task | Owner | Size |
|---|---|---|---|
| 3.1 | Protocol v1: versioned JSON over WebSocket (`hello`, `input`, `snapshot`, `match_end`) | Both | S |
| 3.2 | `gg_server`: asyncio + websockets, runs `World.step` at 60 Hz, sends snapshots at 20–30 Hz | Ayman | L |
| 3.3 | Client network mode: send inputs, render snapshots with interpolation | Ayman | L |
| 3.4 | Rooms: 2 players, join code, timeouts, disconnect handling | Ayman | M |
| 3.5 | Matchmaker (Node/TypeScript): Redis queue, pairs players, returns server address + token | Friend | L |
| 3.6 | Multi-stage, non-root, slim Dockerfiles for server and matchmaker | Friend | M |
| 3.7 | docker-compose: matchmaker, Redis, 2 game servers, Caddy for TLS | Friend | M |
| 3.8 | Measure input delay from Cairo to an EU VPS | Both | S |

### Phase 4 — Kubernetes platform (Sprints 6–7, weeks 10–12)

**Goal:** the whole stack runs on Kubernetes from code, with game servers managed by Agones. **Gate:** one command builds the cluster from nothing; the matchmaker allocates one Agones GameServer per match; teardown leaves nothing billing.

| ID | Task | Owner | Size |
|---|---|---|---|
| 4.1 | Local cluster (k3d or kind) + Agones via Helm, versions pinned | Friend | M |
| 4.2 | Agones Python SDK in `gg_server`: Ready, health, Allocated, Shutdown after the match | Ayman | M |
| 4.3 | Fleet + GameServerAllocation called by the matchmaker | Friend | M |
| 4.4 | Helm charts: matchmaker, Redis, web client | Friend | M |
| 4.5 | Terraform: cloud cluster, separate game-server node pool, firewall rules | Ayman | L |
| 4.6 | GitOps with Argo CD: `main` → staging, tag → prod | Ayman | M |
| 4.7 | Secrets with SOPS | Friend | S |
| 4.8 | Ingress + cert-manager for the matchmaker and web client | Friend | S |
| 4.9 | TLS WebSocket (`wss://`) path from a browser to an Agones game server: gateway or per-server certificates. An HTTPS page cannot open plain `ws://` | Open | L |

### Phase 5 — Observability & scale (Sprint 8, weeks 13–14)

**Goal:** you can see the system and push it until it breaks. **Gate:** a bot load test watched live in Grafana; FleetAutoscaler adds game servers under load and removes idle ones.

| ID | Task | Owner | Size |
|---|---|---|---|
| 5.1 | Prometheus metrics in `gg_server`: tick duration, players, matches, snapshot bytes | Ayman | M |
| 5.2 | Matchmaker metrics: queue length, time-to-match | Friend | S |
| 5.3 | kube-prometheus-stack, Grafana dashboards, Loki logs | Friend | M |
| 5.4 | Bot client (from 1.11) as a Kubernetes Job load generator | Ayman | M |
| 5.5 | FleetAutoscaler; step load up until something breaks, then fix it | Both | M |
| 5.6 | SLOs + alerts: time-to-match p95, tick-overrun rate | Both | S |

### Phase 6 — DevSecOps & reliability (Sprint 9, weeks 15–16)

**Goal:** the pipeline enforces security and you've practiced failing. **Gate:** CI blocks an image with a critical CVE; one chaos drill is written up as a blameless postmortem.

| ID | Task | Owner | Size |
|---|---|---|---|
| 6.1 | Trivy (images + IaC) and Semgrep in CI | Friend | S |
| 6.2 | SBOM with Syft + cosign signing, verified at admission | Ayman | M |
| 6.3 | NetworkPolicies, Pod Security Standards, least-privilege RBAC | Ayman | M |
| 6.4 | Rate limiting + token checks on room joins | Ayman | S |
| 6.5 | Chaos drills: kill a game server mid-match, kill Redis, drain a node | Both | M |
| 6.6 | Runbooks + one postmortem | Friend | S |
| 6.7 | Canary releases for the matchmaker with Argo Rollouts | Friend | M |

## Backlog

**Now (Sprint 0 + Sprint 1):** all of Phase 0, then 1.1–1.3, 1.7 and the pygbag spike 1.10. The spike comes early on purpose: if pygbag can't run your sprites in week 3, the plan changes before Phase 2 is built on it.

**Next:** the rest of Phase 1, then Phase 2. Re-plan Phases 3–6 at the end of Sprint 3, once you know your real velocity.

**Ongoing:** a LinkedIn learning series on the game's evolution. One post per phase gate, with a demo or screenshot, focused on what broke and how it was fixed. First post after Phase 1.

**Icebox** (good ideas, not on the critical path):

- Client-side prediction + server reconciliation (the fix for input delay)
- Accounts, match history and leaderboard (Django + Postgres)
- Replays: store input logs in object storage and re-simulate them
- Spectator mode
- More than 2 players, or team modes
- Controller support
- Level editor in the browser (replacing `scripts/editor.py`)
- A modern OpenGL renderer (moderngl, VBOs, shaders) behind the same renderer interface, if you want the graphics learning back
- WebRTC/UDP transport; multi-region servers

### Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Game work eats the DevOps time | High | Phase 2 is timeboxed with a hard cut line |
| Full-time training leaves less time than planned | High | Re-plan at the end of Sprint 3 using real velocity; cut Phase 6 scope before cutting gates |
| pygbag can't handle part of the client | Medium | Spike 1.10 in week 3; fallback = desktop client only + a thin browser client later |
| Online play feels laggy | Medium | Measure in 3.8; prediction is in the icebox |
| Cloud bill | Medium | Do 90% of the work on a local cluster; billing alerts; `terraform destroy` after each session |
| Agones and Kubernetes versions drift | Low | Pin both; check the Agones compatibility table before upgrading |

### Hosting and keeping proof after the cloud is shut down

- **Terraform is the snapshot.** The whole AWS setup lives as code in the repo, so anyone can read exactly what you built, and one command rebuilds it for a live demo the same day.
- **Cloud only in short, timed sessions.** Do most of the work on a local cluster; set AWS budget alerts; run `terraform destroy` at the end of every session.
- **Capture evidence before the final teardown:** a short demo video of a match going through the matchmaker, Grafana screenshots from a load test, the architecture diagram, and a write-up of what broke and how you fixed it.
- **Keep one thing permanently live for free:** the web version on GitHub Pages, so there's always a link people can click.
- These artifacts double as material for the LinkedIn series.

## Working agreement

- **Cadence:** 2-week sprints. Planning on day 1 (30 min), an async daily update in chat, review + retro on the last day. The review is a live demo of the gate.
- **Board:** GitHub Projects with Backlog → Ready → In progress → Review → Done. Each task ID above becomes one issue. WIP limit: 2 issues per person.
- **Branching:** trunk-based. Short-lived branches off `main`, conventional commits, squash merge.
- **Definition of done:** merged through a PR reviewed by the other person, CI green, tests for any logic change, README or runbook updated if behaviour changed.
- **Decisions:** anything that's hard to reverse gets a one-page ADR in `docs/adr/`, starting with ADR-001.
- **Rotation:** swap ownership of at least one ops task per sprint, so both of you touch CI, Kubernetes, Terraform and observability, not just one.

## Sources

- Agones 1.60.0 release notes (Kubernetes 1.34–1.36 support)
- Agones blog: 1.58.0 adds a Python SDK
- pygbag on GitHub (pygame-ce only)
- pygbag packaging notes (async loop, `main.py` entry, large builds)
- Python forum: pygbag networking (WebSockets yes, threads no)
- AymanOHM/project_gg
