# Engineering journal

A running record of what was done in this project, why it was done that way, and how it works. It is written to be learned from: each entry names the problem, the reasoning, the mechanism, and where to look in the code. Newest entries are at the bottom.

Other documents answer different questions: `docs/ROADMAP.md` says what is planned, `docs/HANDOFF.md` says where the work stands today, and `docs/adr/` records the big decisions formally. This file is the story and the explanation.

**How to add an entry:** one entry per PR or decision. Use the same five headings. Write for someone who knows Python and backend work but has not seen this code. Explain terms the first time they appear.

---

## 1. Preserving the old game before changing anything

**Problem.** The repo held a working 2024 course game. The plan was to rebuild almost all of it. Once rebuilt, how would anyone see or run what it used to be?

**What we did.** Tagged the last original commit as `v1` and published a GitHub release for it. Then cleaned up with ordinary commits.

**Why this way.** There were two options. Rewriting history (for example with `git filter-repo`) would shrink the repo by removing the 45 MB of vendored binaries from every old commit, but it changes every commit hash, which breaks everyone's clones, open pull requests and links. A tag costs nothing, changes nothing, and gives a permanent name to "the original". For a portfolio the history is also evidence: it shows where the project started.

**How it works.** A git tag is a name that points at one commit and never moves. A GitHub release is a page attached to a tag, with notes and downloadable source archives. `git checkout v1` brings back the original at any time.

**Where to look.** `git show v1`, and the release page on GitHub.

---

## 2. From vendored libraries to a real dependency file

**Problem.** The game shipped its own copies of PyOpenGL and pygame inside `libs/`, built for Windows and Python 3.7. It could not start on a Mac or on Linux, and nobody could tell which versions it needed.

**What we did.** Deleted `libs/`. Added `pyproject.toml` (what the project needs), `uv.lock` (the exact versions that were resolved) and `.python-version` (3.12).

**Why this way.** Vendoring compiled libraries ties a project to one operating system and one Python version. Declaring dependencies lets a tool fetch the right build for each machine. `uv` was chosen because it also installs Python itself, so a new contributor needs one command: `uv sync`. Python 3.12 was chosen because that is the version pygbag runs in the browser, and the same rules code must run in both places.

**How it works.** `pyproject.toml` lists loose requirements (`pygame-ce>=2.5.2`). `uv lock` resolves them into `uv.lock`, which pins every package and its hashes. CI runs `uv sync --locked`, which fails if the lock file and `pyproject.toml` disagree, so what was tested is what gets installed. Dependency groups (`dev`, `web`, `legacy`) keep optional tools out of the default install.

**Worth knowing.** The distinction between a requirements file (what I want) and a lock file (what I got) is the basis of reproducible builds, and it comes back later in Docker images and in supply-chain security.

**Where to look.** `pyproject.toml`, `uv.lock`, `.python-version`.

---

## 3. Line endings: 3,104 files that had not changed

**Problem.** `git status` on the Mac showed 3,104 modified files. Nothing had been edited.

**What happened.** The working copy came from Windows, where text files end lines with two characters (CR LF). The repository stores one (LF). Git compared bytes and saw every line of every file as different.

**What we did.** Added `.gitattributes` with `* text=auto eol=lf`, so git normalises line endings on every machine, and marked images and audio as binary so git never tries to "fix" them.

**How to check next time.** `git diff --ignore-cr-at-eol --stat` shows what remains once line endings are ignored. Here it showed one blank line in one file.

**Where to look.** `.gitattributes`.

---

## 4. Continuous integration before the refactor, not after

**Problem.** A refactor of this size changes almost every line. Without automatic checks, a mistake made on day one is found on day ten.

**What we did.** Added ruff (linter and formatter), pre-commit (runs the checks before each commit locally) and a GitHub Actions workflow that runs ruff and pytest on every pull request.

**Why this way.** The roadmap had CI as a later task for the second developer. It was moved first because its value is highest while the code is changing fastest. The cost was small: one workflow file.

**How it works.** `.github/workflows/ci.yml` defines jobs. Each job starts a fresh Ubuntu machine, checks out the code, installs with `uv sync --locked`, and runs the checks. A red result blocks nothing by itself; branch protection is the separate GitHub setting that makes green CI a condition for merging.

**A trap we hit.** `web/build.sh` worked locally and failed in CI with "Permission denied". The script's executable bit had not been committed, because this Mac's git has `core.filemode` off and ignores permission changes. The fix was `git update-index --chmod=+x web/build.sh`. Lesson: CI runs on a clean machine and finds what your own machine hides.

**Where to look.** `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, the `[tool.ruff]` section of `pyproject.toml`.

---

## 5. Why the rendering library changed (ADR-001)

**Problem.** The game drew with PyOpenGL and GLUT. It needed to run in a browser as well as on the desktop, and its rules needed to run on a server with no window at all.

**What we decided.** Draw with pygame-ce. Build the browser version from the same Python code with pygbag. Make the server authoritative: clients send key state, the server decides what happens.

**Why.** The game is 2D sprites on a grid, so OpenGL was not buying anything. pygame-ce runs natively and, compiled to WebAssembly by pygbag, in a browser. One client codebase is cheaper to keep correct than two. Server authority means a modified client cannot cheat, and it is what a game-server platform like Agones is built around.

**How we knew it would work.** We did not assume. A spike (a small throwaway experiment built only to answer a question) drew the map and the player in Chrome and measured it: 60 frames per second, a 32 KB game bundle, about 11 MB of Python runtime downloaded once, and working WebSocket messages. See entry 9.

**The cost we accepted.** A page served over HTTPS may only open encrypted WebSockets (`wss://`). Agones gives each game server a bare IP address and port with no certificate. Getting a browser connected to a game server therefore needs extra infrastructure (roadmap task 4.9). The alternative, desktop-only online play, would have avoided that but removed "click this link and play online".

**Where to look.** `docs/adr/001-architecture-direction.md`, `docs/spikes/pygbag.md`.

---

## 6. Separating rules from drawing

**Problem.** In the original, `player.move()` moved the player, checked collisions, fired the gun, updated bullets, decided who won, and drew the health bar. Bullets reached into a global `game` object to find players. Nothing could run without a window, so nothing could run on a server or in a test.

**What we did.** Split the code into `gg_core` (the rules, no drawing, standard library only) and `gg_client` (drawing, keyboard, sound). The rules expose two calls: `World.step(inputs)` advances the game by one tick, and `World.snapshot()` returns what the world looks like as plain dictionaries.

**Why this shape.** Three different programs need the rules: the desktop client, the browser client and the server. If the rules import pygame, the server needs a display library; if they read the keyboard, they cannot take input from a network. Making the rules a pure function of "previous state plus inputs" removes both problems. The renderer only ever receives snapshots, which is also exactly what a network client will receive from the server, so the same renderer works offline and online.

**How it works.**
- **Fixed timestep.** The original moved things a fixed distance per drawn frame, so a faster computer ran a faster game. Now one call to `step` is always 1/60 of a second of game time. The client measures real time and calls `step` as many times as needed (`gg_core/clock.py`, the "accumulator" pattern).
- **Inputs as held buttons.** An input says which buttons are down during a tick, not "the jump key was just pressed". The world works out the moment of pressing itself. Held state can be sent over a network repeatedly without harm; a lost or duplicated "pressed" event would change the game.
- **Determinism.** The world never reads the clock and never uses unseeded randomness. The same level and the same inputs always produce the same game. That property is what makes exact testing possible (entry 7), and later replays and lag compensation.

**Where to look.** `gg_core/world.py`, `gg_core/inputs.py`, `gg_core/clock.py`, `gg_client/renderer.py`, and `docs/adr/002-core-interfaces.md`.

---

## 7. Proving the rewrite behaves like the original

**Problem.** "It should feel the same" cannot be reviewed. A rewrite of physics code can be wrong in ways that only show after an hour of play.

**What we did.** Ran the original game's own classes without a window and recorded what they did on every tick: position, speed, facing, animation, health, wall and floor contacts, every bullet. 28 scripted scenarios, about 8,000 ticks. The new code has to reproduce every number exactly.

**Why this way.** This is called a characterization test, or golden master: when you do not have a specification, the existing behaviour is the specification, so you capture it before changing anything. It is stronger than hand-written unit tests here because nobody had to guess what the rules were, quirks included.

**How it works.** The old classes call OpenGL when they are created and drawn. The recorder (`tools/record_v1_traces.py`, in the history before the v1 code was removed) put fake `OpenGL` modules into `sys.modules` whose functions do nothing, then imported the old code, which never noticed. It then called `player.move()` in a loop with scripted inputs and wrote the state to `tests/golden/v1_traces.json.gz`. `tests/test_v1_parity.py` replays the same inputs through `World` and compares.

**What it found.** The port matched on the first run, which says the reading of the old code was right. It also pinned down quirks nobody would have listed: players spawn inside solid tiles and are pushed up in the first ticks; the gun trails the player by one tick; a bullet can in principle hit the player who fired it.

**One deliberate difference.** The original removed bullets from a list while looping over it, which makes the loop skip the next bullet. The new code builds a new list. The recorder applied the same fix to the old code so the two stay comparable.

**Where to look.** `tests/test_v1_parity.py`, `tests/golden/`, and `tests/test_rules.py` for the same rules stated as readable numbers.

---

## 8. A level format with its own data in it

**Problem.** The original map file said `tile_size: 16` while the code hard-coded 45. Spawn points lived in `game.py`. A map file alone could not describe a level.

**What we did.** Defined a versioned JSON level format holding tile size, spawn points, the height below which a player has fallen out, and the tiles. The loader validates everything and fails with a message that names the problem.

**Why validate.** A level will eventually arrive at the server from somewhere else. Data that crosses a boundary should be checked at the boundary, once, so the rest of the code can trust it. A `format` number in the file means the format can change later without old files being misread.

**Where to look.** `gg_core/level.py`, `data/levels/arena.json`, `tests/test_level.py`.

---

## 9. The pygbag spike and what "it works" had to mean

**Problem.** The whole plan rested on Python running a game in a browser. If that failed in week six, six weeks were lost.

**What we did.** Built the smallest thing that could fail in the interesting ways: one map, one animated player, keyboard input, and a WebSocket round trip. Measured frame rate, download size, load time and input. Wrote down what broke.

**What broke, and the lessons.**
- A plain static file server on localhost showed a blank grey page. The page looked for the pygame-ce package on its own host. pygbag's test server quietly proxies that request. On GitHub Pages it worked, because on a real host the page fetches from pygbag's CDN. Lesson: test in the environment you will deploy to; a development server can hide a problem and can also invent one.
- The game bundle contains no Python. The interpreter and pygame-ce are downloaded from a third-party CDN when the page opens. That is a dependency on someone else's uptime, written down as a risk.
- The normal Python `websockets` library does not exist in the browser. The spike used the browser's own `WebSocket` object through pygbag's bridge to JavaScript. So the client will need one small interface with two implementations.

**Why a spike is throwaway.** Its job is to produce knowledge, not code. Keeping it as the base of the real client would carry its shortcuts forward. It lives in `spikes/` and nothing imports it.

**Where to look.** `docs/spikes/pygbag.md`, `spikes/pygbag/`.

---

## 10. Rounds, matches and where "flow" belongs

**Problem.** The original ended at the first death; only quitting worked after that. A match needs a countdown, several rounds, a score and a winner.

**What we did.** Added `Match`, which owns a `World` and has the same `step` and `snapshot` calls. It runs the countdown, pauses after each round, keeps score and creates a fresh `World` for the next round.

**Why a wrapper and not more code inside `World`.** `World` is the part proven against the original. Leaving it untouched means the proof still holds. `Match` adds only things the original never had, so there is nothing to compare it with and ordinary tests are enough. This is composition: a new object uses an old one rather than changing it.

**Where to look.** `gg_core/match.py`, `tests/test_match.py`.

---

## 11. The renderer, and three bugs that disappeared

**Problem.** The audit of the original found that it uploaded every sprite to the graphics card on every draw, created a new texture object for the player every frame, and used random numbers as texture ids.

**What we did.** `SpriteRenderer` loads, scales and mirrors every image once and only copies pixels during `draw`. A test replaces the image-loading functions with ones that raise an error and then draws 50 frames; if `draw` ever loads an image again, the test fails.

**Why the test matters more than the fix.** Performance mistakes come back silently. A test that fails when someone reintroduces per-frame loading keeps the fix in place after everyone has forgotten why it was there.

**How drawing is kept separate.** The renderer receives a snapshot dictionary and a level, nothing else. The world's coordinates have Y pointing up and positions at the bottom-left of each rectangle; pygame has Y pointing down and positions at the top-left. `gg_client/camera.py` does that conversion in one place.

**Where to look.** `gg_client/sprite_renderer.py`, `gg_client/camera.py`, `tests/test_client_smoke.py`.

---

## 12. Sound, and why the rules had to report events

**Problem.** The client needs to play a sound when someone shoots or is hit. The first idea was to compare two snapshots: a new bullet means a shot, lower health means a hit.

**What went wrong with that idea.** At point-blank range a bullet is created, hits and is removed inside a single tick. It never appears in any snapshot, so no shot sound would play. A test shows this case.

**What we did.** The world records what happened during each tick (`jump`, `shot`, `hit`) and the snapshot carries that list. The client plays sounds from the list.

**The general lesson.** A snapshot is state at an instant. Some things are events between instants. If consumers need events, the producer has to send them; they cannot always be reconstructed from state. The same question returns with networking: a server that sends 20 snapshots per second while simulating 60 ticks must collect the events of the ticks in between.

**Also here.** The audio went from 18 MB of WAV to 1.1 MB of OGG, because the browser build downloads every asset and pygbag expects OGG.

**Where to look.** `gg_core/world.py` (`_events`), `gg_client/audio.py`, ADR-002.

---

## 13. Deploying the browser build

**Problem.** The Phase 2 gate is a public URL where two people can play.

**What we did.** `web/build.sh` copies the code and only the assets the game loads into a staging folder and runs pygbag on it. CI builds it on every pull request. A second workflow, `deploy-web.yml`, publishes it to GitHub Pages when a version tag is pushed or when started by hand.

**How Pages deployment works.** GitHub Pages has two modes. In the older one it serves whatever is in a branch. In the newer one a workflow builds the site, uploads it as an artifact, and a deploy step publishes that artifact. The second mode means the published site is always the output of a recorded, repeatable build, not something pushed by hand. The workflow needs `pages: write` and `id-token: write` permissions and runs in an environment called `github-pages`, which by default only accepts deployments from the default branch. That is why the workflow had to be on `main` before it could run.

**Why build in CI on every PR as well.** A change that breaks the browser build should fail at review time, not on release day.

**Where to look.** `web/build.sh`, `.github/workflows/deploy-web.yml`, the `web-build` job in `ci.yml`.

---

## 14. Stacked pull requests, and how they were merged

**Problem.** The work was done in one long session. One enormous pull request cannot be reviewed.

**What we did.** Each step was its own branch, based on the previous one, with its own pull request: a stack. Each PR shows only its own change.

**How it was merged.** Ayman's rule: merge into feature branches freely, and into `main` only at major milestones. So the Phase 1 PRs were merged downward, each into the branch below it, until one branch held all of Phase 1; that branch went into `main` as one milestone. Merge commits were used, not squashes, because squashing a lower PR rewrites the commits the upper branches are built on and makes them conflict.

**A complication.** The PR that deletes the original game was held back on purpose, but two later PRs (browser build, sound) were stacked on top of it. Their commits were re-applied on a new branch from `main` with `git cherry-pick`, which copies a commit's change onto a different base. The two original PRs were closed as superseded.

**Lesson.** Stack order is dependency order. Put the change most likely to be delayed at the top of a stack, not in the middle.

---

## 15. A journal, because finished code does not teach

**Problem.** After the first long session the repo had working code, tests and pull requests, but nothing that explained the reasoning to the person the project is meant to teach.

**What we did.** Started this file, wrote entries 1 to 14 from what had happened, and made a rule in `CLAUDE.md` that every change adds an entry.

**Why a separate file.** A PR description says what changed and how to test it, and is read once at review. An ADR records one decision formally. Neither is a place to explain a mechanism, a mistake or a general lesson, and both are scattered. One file read top to bottom tells the story in order.

---

## 16. A menu that is logic first and pixels second

**Problem.** The game needed a main menu and options (volume, fullscreen, key bindings), drawn like the welcome screen: white block letters with a dark shadow.

**What we did.**
- `gg_client/menu.py`: a `Menu` class that holds which screen and line are selected and reacts to key presses, and a separate `draw_menu` function that draws it.
- `gg_client/settings.py`: a `Settings` object saved as JSON in `~/.project_gg/settings.json`.
- The welcome image is replaced by the menu; the sky, clouds and gentle bob are kept.

**Why split logic from drawing.** `Menu.handle_key(key)` takes a key code and returns `"play"`, `"quit"` or nothing. It needs no window, so every path through the menu is covered by fast tests: wrapping selection, volume limits, rebinding a key, cancelling a rebind. It is the same idea as `gg_core` and the renderer, at a smaller scale: keep decisions in code that can run anywhere, and keep the part that touches the screen thin.

**How the lettering works.** There is no pixel font file in the repo, and the welcome screen's lettering exists only as a picture. `pixel_text` renders text small with smoothing turned off, then enlarges it with nearest-neighbour scaling, which copies each pixel into a square block. A dark copy drawn one pixel down and right before scaling becomes the shadow. The result is close to the welcome screen, not identical; an exact match needs the original font.

**How settings are kept safe.** Saved data is treated as untrusted: every value is checked when loading, and anything missing or wrong falls back to the default rather than stopping the game. Keys are stored by name (`"space"`) instead of by number, so the file stays valid if pygame changes its key codes. In the browser nothing is saved, because the page has no lasting file system.

**A detail worth noticing.** While the menu waits for a new key for a binding, every key must be accepted, including W, S and Enter, which normally move the cursor. So that state is checked first in `handle_key`, before any navigation.

**Fullscreen.** The window is opened with pygame's `SCALED` flag: the game always draws at 1280x720 and SDL stretches the picture to the window or screen. Toggling fullscreen then needs no change anywhere else.

**Where to look.** `gg_client/menu.py`, `gg_client/settings.py`, `tests/test_menu.py`.

---

## 17. Three more levels, and converting data between conventions

**Problem.** `data/maps/0–2.json` came from the tutorial the art is from. They looked like ready-made levels, but they follow different conventions from this game: Y points down, positions are in 16-pixel units, there are no spawn points for two duelling players, and decoration is stored as free-floating pixel positions.

**What we did.** Extended `tools/convert_v1_map.py` with a `--y-down` mode and produced `meadow`, `cliffs` and `towers` in `data/levels/`. The client now plays one level per round, in order, starting with the original arena.

**How the conversion works.**
- **Flipping.** In a Y-down map, row 3 is above row 15. In this game's Y-up world it must be the other way round, so every tile's `y` is negated. The tile pictures are not flipped, only their positions, so grass still has its green edge on top.
- **Spawns.** The tutorial maps mark where its player and its enemies start. The converter takes the player marker and the enemy marker farthest from it horizontally, converts both from 16-pixel units to this game's 45-pixel tiles, and names the left one `p1`.
- **Falling out.** `kill_y` is set 300 pixels below the lowest tile.

**Why a tool and not hand-edited files.** A conversion written as code can be read, reviewed and rerun; a hand-edited file of 300 tiles cannot. The tool also validates its output with the same loader the game uses, so it cannot write a level the game would refuse.

**How we know the levels are playable at all.** A test loads every shipped level, lets the world run for 200 ticks with nobody pressing anything, and checks that both players are standing on something, were not pushed sideways, and are at least ten tiles apart. That catches a spawn inside a wall or over a hole.

**What that test does not prove.** It does not prove the players can reach each other. These maps were designed for the tutorial's jump height, and here a jump is 65 pixels and a double jump twice that. `cliffs` and `towers` also start the players about 1,200 pixels apart on a 1,280-pixel-wide view, so both sit near the screen edges. A person has to play them; if they do not work, removing a level is one line in `LEVEL_ORDER`.

**Where to look.** `tools/convert_v1_map.py`, `data/levels/`, `LEVEL_ORDER` in `gg_client/__main__.py`, `tests/test_level.py`.

---

## 18. Desktop builds: shipping Python to people who do not have Python

**Problem.** Running the game needs uv, Python and the repo. A player wants one thing to download and double-click.

**What we did.** `desktop/build.sh` packages the game with PyInstaller. A workflow, `release-desktop.yml`, builds it on a macOS machine and a Windows machine, runs it for 30 frames to prove it starts, zips it, and attaches the zips to the GitHub release when a version tag is pushed.

**How PyInstaller works.** It follows the imports from an entry script, copies the Python interpreter, every imported module and the listed data files into one folder, and adds a small launcher program. Nothing is compiled to machine code; it is the same Python, bundled. Two consequences:
- **No cross-compiling.** The bundle contains that system's interpreter and libraries, so a Windows build must be made on Windows. That is why the workflow uses a matrix: the same steps run once per operating system.
- **Data files must be listed.** PyInstaller finds code by following imports, but it cannot know the game opens `data/images/...` at run time. Each folder is passed with `--add-data source:destination`.

**Why no code changed for asset paths.** The game locates its data relative to the `gg_client` package (`Path(__file__).parent.parent / "data"`). Inside the bundle the package sits in the bundle's own folder, so copying the data to the same relative place is enough. Code that used the current working directory instead would have broken here; this is the usual reason to build paths from `__file__`.

**The smoke test.** The workflow sets `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`, which tell SDL to use a fake screen and sound card, and runs the packaged program for 30 frames. A missing data file or module makes it exit with an error and fails the build. Without this step a broken package would only be discovered by the first person to download it.

**A trap we hit.** The first Windows build failed with `Unable to find '\\d\\a\\project_gg\\...\\data\\levels'`. The script built absolute paths in Git Bash, where drive D is written `/d/...`. PyInstaller is a native Windows program and read that as a path on the current drive. Relative paths mean the same thing to both, so the script now uses only those. Lesson: on Windows runners a bash script and the programs it starts may disagree about what a path looks like.

**Known limits.** The builds are not code-signed. macOS will say the app is from an unidentified developer (right-click, Open, the first time) and Windows SmartScreen may warn. Signing needs paid developer certificates.

**Where to look.** `desktop/build.sh`, `desktop/main.py`, `.github/workflows/release-desktop.yml`.

---

## 19. Deleting assets nothing loads

**Problem.** `data/images` held 178 files. The rewrite loads 98 of them and the original game one more. The rest were leftovers: a 14-file health bar pack, the tutorial's particles and enemy sprites, a second copy of the run animation, earlier drafts of the bullet and gun pictures. Every one of them is a file whose licence someone has to check before a public release (task 0.8), and a file a new reader has to wonder about.

**What we did.** Removed 79 files with `git rm`. `data/images` went from 872 KB to 488 KB.

**How "unused" was established.** By reading the code, not by guessing from file names. Three programs load images, and a file had to be unused by all three:
- the rewrite (`gg_client/sprite_renderer.py`), whose list is mirrored in `web/build.sh` and `desktop/build.sh`;
- the original game (`game.py`), which is still in the repo until Ayman has compared the two;
- the original's helper scripts in `scripts/`.

That is why `welcome.png` stayed: the rewrite replaced it with the menu, but the original still opens it and would crash at start-up without it. It goes when the original goes (PR #38).

Two details needed care. Both programs load whole folders (`load_images('tiles/grass')`, `glob("*.png")`), so a file is "used" if its folder is, even though its name appears nowhere in the code. And `tiles/spawners` looked used, because the word appears in the tutorial maps, but only as markers that the converter turns into spawn points; no level draws one.

**What was kept on purpose.**
- `data/maps/`: the source the three converted levels were made from. Nobody has play-tested those levels yet, and if spawns have to move, the converter needs its input. `tests/test_maps.py` also reads them.
- `data/sfx/dash.ogg`: not loaded yet, but the dash (task 2.5) will use it.

**Why this is safe, and what it does not do.** Nothing is lost: every deleted file is still in the `v1` tag and in history, and `git checkout v1 -- path` brings one back. For the same reason the repository does not get smaller to clone. Git keeps every version of every file ever committed; deleting a file only removes it from the current snapshot. Shrinking a repo means rewriting history, which entry 1 explains was ruled out.

**How it was checked.** The tests draw every shipped level with the real renderer, so a missing tile or sprite fails them. CI builds the browser bundle, whose script copies files by name and stops if one is missing. For the original game, a short script confirmed every path `game.py` loads still exists.

**Where to look.** `CREDITS.md` (one row fewer to verify), `web/build.sh` for the list of what the game loads.

---

## 20. Dash: the first rule the original never had

**Problem.** Every rule so far was copied from the original and proven against recordings of it (entry 7). The dash (task 2.5) is new. It needs a new button, new physics and a new animation state, and it must not disturb anything the recordings prove.

**What we did.** Added a sixth button, `dash`. Pressing it moves the player 15 pixels per tick for 8 ticks (120 pixels, a little under three tiles), in the direction held, or the way the player faces if none is held. In the air the player keeps its height while dashing, so a dash crosses gaps. A wall or a jump ends it, and the next dash is available 45 ticks (0.75 s) after the last one began. Player 1 dashes with Left Shift, player 2 with `.`; both can be rebound in the menu.

**How it stays out of the way of the old rules.** All of the dash is behind one condition, `dash_ticks > 0`, and that counter only becomes non-zero when the dash button is pressed. The recordings never press it, so for them every new line is skipped and the 28 scenarios still match tick for tick, with the trace file untouched. That is the check that the change is purely additive: not "the tests were updated", but "the old tests could not tell anything happened".

**How it works, in the order a tick runs.**
1. *Press detection.* Like jump, dash acts on the tick the button goes from released to held (`dash_was_held`). Holding it does nothing more. This is the rule from entry 6: the client sends what is held, the world works out the moment.
2. *Start.* `_dash` checks the cooldown, sets `dash_ticks = 8`, stores the direction and records a `dash` event for the sound.
3. *Each tick of `_move`.* The normal horizontal speed is worked out as always and then overwritten with `dash_direction * 15`. The collision code after it is the same code that stops a running player, so walls work without any new code.
4. *Height.* If the player was in the air on the previous tick, vertical movement is set to zero for this tick and the falling speed is reset to zero afterwards. If the player was on the ground, the vertical part is left alone.

**Why the ground case is left alone.** This was the part that needed thought. The rules know a player is standing only because, every tick, gravity pulls them a fraction into the floor and the collision pass pushes them back out and sets `hit_down`. If a dash froze vertical movement on the ground too, that contact would vanish, the world would think the player was airborne, and pressing jump during a ground dash would silently use up the double jump. Keeping the tiny fall-and-land cycle running keeps the contact. When a ground dash runs off a ledge, the contact disappears by itself one tick later and the same dash turns into a hovering one.

**Why a jump cancels the dash.** Otherwise the hover rule would erase the jump's upward speed on the next tick and the jump key would appear to do nothing. Cancelling is also the more useful move for a player: dash, then jump out of it.

**Why 15 pixels per tick and not more.** Collision is checked once per tick at the new position. If something moves farther in one tick than the thing it should hit is wide, it can be on one side before the tick and on the other side after, and never overlap: this is called tunnelling. Tiles are 45 pixels, so 15 is safe, and a test dashes at a wall from 85 different distances to prove it. The constant has a comment saying so, because the tempting way to "make the dash feel better" is to raise it.

**The wire format.** `dash` was added at the end of the button list, so it takes bit 5 and the five existing bits keep their meaning. Reading an input from JSON treats a missing button as released. Both choices mean a sender that has never heard of dash still produces valid input. The snapshot gained a new `action` value and a new event type but its version stayed 1, because nothing was renamed or removed; ADR-002 records that and the reasoning.

**Tests that had to change, and why that is acceptable.** Two existing tests failed, both correctly. One used `"dash"` as its example of an unknown button; it is known now, so the example became `"crouch"`. The other asserted that no player ever moves faster than running speed over 10,000 random ticks; the limit is now the dash speed. Neither is a parity test. The rule in `CLAUDE.md` is about never loosening the comparison with the original, and that comparison was not touched.

**The picture.** The art has a one-frame pose called `slide` that the original loaded and never showed. The renderer draws the `dash` action with it (`ACTION_FOLDERS`), so the rules can name the action for what it is without renaming art files.

**What is not known.** Whether it feels good. The numbers are first guesses made without playing: distance, duration, cooldown, and whether a dash should protect from bullets (it does not). All three numbers are constants in one file. The random bot also presses dash now, which changes the games it plays for a given seed; nothing depended on the old ones.

**Where to look.** `gg_core/world.py` (`_dash`, and the `dashing` / `hovering` lines in `_move`), `gg_core/constants.py`, the dash section at the end of `tests/test_rules.py`, `docs/adr/002-core-interfaces.md`.

---

## 21. Asking for a milestone: what a gate does and does not prove

**Problem.** All the Phase 2 work that could be done alone was merged into `phase-2`. `main` only moves at milestones, and only when Ayman says so. How should the request be made so that the decision is easy and honest?

**What we did.** Opened one pull request from `phase-2` to `main`, "Phase 2 complete", and left it unmerged. Its description sets the roadmap's gate next to what was checked.

**Why an integration branch at all.** `main` is what the public page and the releases are built from, so it should only ever hold states someone has agreed to publish. `phase-2` is where finished pieces collect in the meantime. The milestone PR is then the one place where "is this ready to publish?" is asked, with the whole difference visible in one diff, instead of the question being spread over five small PRs that were each only about themselves.

**The gate, read literally.** "A public GitHub Pages URL where two people on one keyboard play a full best-of-3." Three different kinds of evidence are involved, and they should not be confused:
- *Automated and true now:* the tests play full matches headless, draw every level, and CI builds the browser bundle on every PR.
- *True only after a step that has not happened:* the public page is built from `main` by a workflow that runs on a tag or by hand. Merging does not publish. Until the workflow runs, the URL shows the old build.
- *Not automatable:* two people playing. No test says whether the dash feels right or whether the new levels are fun, or even crossable.

**The lesson.** Green CI answers "does it still do what the tests describe". A gate asks "does it do what we wanted". The gap between the two is exactly the list a reviewer needs, so the PR states it rather than leaving it to be discovered.

**What happened next.** Ayman approved it the same day. The PR was merged with a merge commit and `deploy-web` was started by hand on `main` (`gh workflow run deploy-web.yml --ref main`); the run built commit `35e004d` and the page answered with the new build. The two steps were separate commands, which is the point made above: merging and publishing are different decisions.

**Where to look.** PR #49; `.github/workflows/deploy-web.yml` for when the page is rebuilt.

---

## 22. Asking the physics whether a level can be crossed

**Problem.** Entry 17 ended with a doubt: the tutorial's maps were built for a different jump height, so on `cliffs` and `towers` the two players might never be able to reach each other. The handoff said a person had to play them to find out. Could the code answer it instead?

**What we did.** Wrote a test that searches for a route. For every shipped level and each player, it looks for a sequence of button presses that brings that player to within one tile of where the other one starts. All four levels pass in both directions.

**How the search works.** It is a best-first search, a relative of the breadth-first search used for mazes.
- A *state* is a copy of one player (position, speed, whether the double jump and the dash are available) plus the tick number.
- A *move* is one of eight button combinations (nothing, left, right, jump, jump left, jump right, dash left, dash right) held for five ticks. A jump or dash is pressed only on the first of the five ticks, because both act on the press, not the hold.
- The search keeps a priority queue of states ordered by distance to the goal. It takes the closest one, puts the real `World` into that state, plays each move through `World.step`, and adds the results to the queue.
- States that land in the same 15-pixel square with the same flags count as already visited. Without that the search would never end; with it, a level has a few thousand distinct places.

**Why use the real rules instead of a formula.** One could reason "a double jump rises about 130 pixels, so a ledge three tiles up is reachable". But the truth includes wall jumps, air control, the dash holding height, and corners that catch a player by a pixel. The rules already encode all of that, and they are a pure function of state and input (entry 6), so they can be run from any state as often as needed. This is the third thing determinism has paid for, after the parity tests and reproducible bot runs.

**What a pass and a fail mean.** They are not symmetric. A pass is a proof: the route was actually played, tick by tick, by the same code the game runs. A fail only means the search did not find a route. Because nearby positions are merged, it can discard the one state that would have made a tight jump. So the test's message says "no route found", not "impossible", and a second test feeds the search a sealed room to check that it does give up rather than pass everything.

**What it found on the way.** Run without the dash, the search fails in one direction on every level (for example p2 cannot get up to p1's tunnel in the arena). With the dash every direction works. One direction is enough for the players to meet, so the levels were playable before, but lopsided: one player had to come to the other.

**What it does not tell us.** Reachable is not the same as fun, and a route a search finds in 600 attempts may be one a person finds annoying. It also says nothing about the camera, which is the next entry's subject.

**Where to look.** `tests/test_level_reachability.py`.

---

## 23. A camera that widens, and why it draws big and shrinks

**Problem.** The camera followed the midpoint between the players at a fixed size of 1,280 by 720 world pixels. On `cliffs` and `towers` the players start about 1,200 pixels apart, so both stood at the very edges of the screen, and a player who climbed could leave the picture altogether.

**What we did.** The camera now has a `scale`: how many world pixels one screen pixel covers. It is 1 while the players are close. When they are far apart it grows, up to 1.6, until both are at least 250 pixels inside the left and right edges and 200 inside the top and bottom. It eases towards its target by 1/30 of the gap per frame, the same rule the original used for scrolling, so zoom and scroll move together.

**The design question: how do you draw a zoomed-out picture?** Entry 11 explained that every image is scaled once when it is loaded, and that `draw` only copies pixels. A zoom seems to break that: at scale 1.3 every tile should be 35 pixels, at 1.31 a little less, and the scale changes every frame while it eases. Three options:
- *Rescale every sprite whenever the scale changes.* That is the per-frame image work entry 11 removed, and it would fail that entry's test.
- *Only allow a few fixed zoom levels and cache sprites for each.* No per-frame scaling, but the camera would jump between levels, and tiles drawn at rounded sizes leave one-pixel seams.
- *Draw the world at normal size onto a larger surface, then shrink the whole picture once.* This is what we did.

**How it works.** The renderer keeps one surface of 2,048 by 1,152 pixels (1.6 screens). Each frame it asks the camera for the view size, takes that much of the big surface (`subsurface`, which is a window onto the same pixels, not a copy), and draws tiles, players and bullets on it exactly as before, with the same cached images. Then one call, `pygame.transform.smoothscale`, shrinks that picture onto the screen. The score and countdown are drawn afterwards, straight onto the screen, so the text stays the same size and stays sharp.

The camera's `to_screen` now answers in the coordinates of the view, not of the screen. At scale 1 those are the same thing, which is why none of the drawing code had to learn about zoom: it changed from "blit to the screen" to "blit to the canvas", and the canvas is the screen itself whenever the scale is 1.

**What it costs.** One shrink of up to 2.4 million pixels per frame. Measured on the Mac with a fake display: 0.5 ms per frame at scale 1 and about 2.5 ms zoomed out, against a budget of 16.7 ms at 60 frames per second. When the players are close the cost is zero, because the shrink is skipped. The browser was not measured; WebAssembly is slower, so that is the place to look if the web build stutters on the wide levels. The limit is one constant, `MAX_ZOOM_OUT`.

**Why stop at 1.6.** The sprites are small pixel art. Past a certain point the players are a few pixels tall and the game is unreadable, and the cost grows with the square of the scale. Beyond the limit the camera behaves as before: it centres on the midpoint and the players may leave the edges.

**A small trap.** Easing never quite arrives: the scale would hover at 1.0000001 for ever and the renderer would keep shrinking a picture by nothing. The camera snaps to exactly 1 once it is within a thousandth.

**Where to look.** `gg_client/camera.py`, the top of `SpriteRenderer.draw` in `gg_client/sprite_renderer.py`, and the three camera tests at the end of `tests/test_client_smoke.py`.

---

## 24. Pausing: stopping the game without stopping the program

**Problem.** Esc during a match threw the match away and showed the main menu. There was no way to stop for a moment, and no way to change the volume or a key without losing the score.

**What we did.** Esc now opens a pause menu over the frozen game: RESUME, OPTIONS, QUIT TO MENU. Esc again resumes. After a match has ended, Esc still goes straight to the main menu, because there is nothing left to pause.

**How pausing works.** It is one line. The loop already separated three things every frame: read events, advance the rules some number of ticks, draw. Pausing sets the number of ticks to zero and leaves the rest running:

```python
for _ in range(0 if paused else steps):
    match.step(inputs)
```

The window still redraws 60 times a second, the music plays, the clouds drift, the menu responds. Only game time stands still. This works because the rules never look at a clock (entry 6): a `Match` that is not stepped cannot change, however long the pause lasts. A game that measured elapsed time inside its physics would have to be told about the pause explicitly, or it would leap forward on resume.

**Why the clock is still advanced while paused.** `FixedStep.advance` is still called each frame and its result ignored. If it were skipped, the frame timer's next reading after resuming would not matter, but the fixed-step accumulator is fed from real time; calling it every frame keeps it from ever seeing one enormous gap and answering with a burst of catch-up ticks.

**Reusing the menu.** The pause menu is a fourth screen of the existing `Menu` class, so it got the lettering, keyboard handling and options screens for nothing. The one new idea is `root`: the options screen needs to know where BACK leads, and that is now the main menu or the pause menu depending on how it was reached. A menu with fixed "back" targets works until the same screen is reachable from two places; then the way back has to be remembered rather than hard-coded.

**A bug caught before it shipped.** `root` stays `"pause"` after resuming. If that match then ran to its end and the player pressed Esc, the game showed the main menu's place with the pause menu's contents. Leaving a finished match now calls `menu.open("main")`. The cause is general: state that is set on the way into something has to be reset on every way out, and there were two ways out.

**How it is tested.** The menu logic has plain tests, as in entry 16. For the loop, a test wraps `Match.step` in a counter, queues an Esc key press, runs twenty frames and checks the counter is zero; then Esc twice and checks it is not. It tests the property that matters (no ticks while paused) without reaching into the loop's variables.

**Rebinding during a match.** It works, with no code written for it: the loop reads `settings.keymap` every frame, so a key changed in the pause menu applies on the next tick.

**Where to look.** The event handling and the `paused` lines in `gg_client/__main__.py`; `open` and `root` in `gg_client/menu.py`.
