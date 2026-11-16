# ADR-001: Architecture direction — pygame-ce client on web and desktop, authoritative server on Agones

- **Status:** Accepted (Ayman, 2026-11-16). To be presented at the kickoff.
- **Date:** 2026-11-16
- **Covers:** roadmap task 0.1; the hosting decision that followed spike 1.10

## Context

Project GG was a PyOpenGL and GLUT course game that ran only on Windows with Python 3.7. It is being rebuilt as a DevOps portfolio project. Two things had to be chosen: what draws the game, and who can play online (browser players, desktop players, or both).

The pygbag spike (`docs/spikes/pygbag.md`) measured the browser option: 60 fps in Chrome, working keyboard input, working WebSocket messages through JavaScript interop, a 32 KB game bundle and a runtime of about 11 MB (gzip) loaded from a CDN.

## Decision

1. **Rendering moves from PyOpenGL to pygame-ce.** The game is 2D sprites on a grid; OpenGL adds nothing, and pygame-ce runs both natively and, through pygbag, in a browser.
2. **One client, two targets.** The same `gg_client` code is the desktop build and the web build.
3. **Online play works from the browser and from the desktop.** Both connect to the game server over WebSocket.
4. **The server is authoritative.** Clients send held buttons only; the server runs `gg_core` at 60 ticks per second and sends snapshots.
5. **Game servers run on Kubernetes under Agones**, one per match, allocated by a matchmaker.
6. **Everything that crosses a process boundary is versioned JSON**, so the matchmaker can be written in Node or Python.

## Alternatives considered

- **Keep OpenGL and fix the renderer.** Keeps the coursework; cannot run in a browser without a rewrite to WebGL, and GLUT is unmaintained. A moderngl renderer stays possible later behind the `Renderer` protocol.
- **Desktop-only online play; the web page for local play only.** Removes the hardest networking task (4.9), because desktop clients can use plain `ws://` to an Agones port. Rejected because nobody could try online play from a link, which is the point of a portfolio piece.
- **Decide after Phase 2.** Costs nothing now, but leaves the protocol and the client transport undefined while Phase 3 is planned.
- **A JavaScript web client next to the Python one.** Smaller download; two clients to keep in step with the rules.

## Consequences

- An HTTPS page can only open `wss://`. Agones exposes a bare node address and port, so a TLS path from the browser to each game server has to be designed and built (task 4.9). It is the task most likely to threaten the Phase 4 gate.
- The `websockets` library does not run in the browser. The client needs a transport interface with a desktop and a browser implementation (task 3.9). The browser one is polled once per frame, adding up to 16 ms.
- `gg_core` stays standard-library-only so it loads in the browser without extra packages.
- The client loop is `async` from the start.
- The web build loads its runtime from a third-party CDN unless it is self-hosted (decide in task 2.7).
- With no client-side prediction, a player far from the server feels the round trip as input delay. Measure in 3.8; prediction is in the icebox.
- Audio must be OGG (task 2.10).
