# Spike: pygame-ce in the browser with pygbag (task 1.10)

2026-11-16 · code in `spikes/pygbag/` (throwaway)

## Verdict

**pygbag is good enough to build the web client on.** One `main.py` rendered `map.json` and the animated player at a steady 60 fps in Chrome, took keyboard input, and exchanged WebSocket messages with a Python server. Confidence: **high** that the game renders and plays in desktop Chrome; **medium** that the whole client ships on the web without a significant workaround, because of what was not tested (listed below).

## What was built

- An async game loop (`await asyncio.sleep(0)` each frame) that runs unchanged on desktop and in the browser.
- 252 tiles from `map.json`, drawn Y-up to Y-down with a following camera.
- Player sprite with idle, run and jump animations, and v1-like movement (run 6, jump 5, gravity 0.2).
- A WebSocket round-trip probe against a local `websockets` echo server.

## Numbers

Measured in Chrome on an M3 Pro MacBook Pro, pygbag 0.9.3, served by pygbag's test server.

| What | Result |
|---|---|
| Python / pygame-ce in the browser | 3.12.12 / 2.5.7 |
| Frame rate | 62.5 fps; frame time median 16 ms, p99 17 ms (1,620 frames) |
| Asset load (72 PNGs + map, after start-up) | 26 ms |
| Game bundle (`pygbag.apk`, code + spike assets) | 32 KB |
| Runtime download, uncompressed | about 22 MB (`main.wasm` 13.1, `main.data` 6.5, pygame-ce wheel 1.5, JS 1.2) |
| Runtime download, gzip from the CDN | about 11 MB (`main.wasm` 4.6, `main.data` 4.5, wheel 1.5, JS 0.2) |
| Cold load to "ready to start" | about 13 s, with the local test server fetching the runtime from the CDN on the way. Not a clean number. |
| WebSocket | Connects and echoes; 200 round trips, median 31.9 ms, max 33.7 ms on localhost |
| Keyboard | 41 of 41 synthetic key-down events arrived |

The 32 ms WebSocket figure is not network time. The loop polls the socket once per frame, so a reply is read one or two frames after the send. Over a real connection this adds up to one frame (16 ms) to the network delay.

## What broke, and what it means

1. **The runtime is not in the build.** `build/web` holds only `index.html` and the game bundle (80 KB). Python, pygame-ce and the loader are fetched from `pygame-web.github.io/cdn/0.9.3/` when the page opens. The game depends on a third-party CDN staying up and keeping that version. Self-hosting the runtime on GitHub Pages is possible and costs about 22 MB of static files.
2. **A plain static server on localhost fails** (GitHub Pages works; see the static-hosting check below). With `python -m http.server` the page asked `localhost:8000/cdn/cp312/pygame_ce-…whl` and got a 404, leaving a blank grey page with no visible error. pygbag's own test server proxies that path. On localhost the page looks for the wheel on its own host.
3. **The `websockets` library cannot be used in the browser.** The probe creates a JavaScript `WebSocket` through `platform.window.eval` and polls an inbox array each frame. The client therefore needs a small transport interface with two implementations: `websockets` on desktop, JavaScript interop on the web.
4. **The page waits for a click before starting.** Browsers need a user gesture to enable audio. The first click is a "start" screen whether we want one or not.
5. **Python 3.12 is what the browser runs**, so the 3.12 pin in `pyproject.toml` matches.

## Not tested

- Firefox, Safari and mobile browsers.
- Audio. `data/music.wav` is 12 MB and `data/sfx` is 6 MB; pygbag expects OGG, so these need converting before a web build.
- Held keys and two players on one keyboard in the browser (the automation only sends taps).
- `wss://` from an HTTPS page, and any connection that is not localhost.
- The full renderer: two players, bullets, clouds, HUD. The spike draws roughly 100 blits per frame; the real client will draw two to three times that.
- Load time on a slow connection.

## Consequences for the plan

- `gg_core` must stay pure Python with no third-party imports, so it loads in the browser without extra wheels.
- The client game loop must be `async` from the start (task 2.6 becomes a constraint on 1.6, not a later change).
- Task 2.7 needs a decision: load the runtime from the pygbag CDN or self-host it.
- New work: convert audio to OGG; add the client transport interface.

## Static-hosting check (2026-11-17, first part of task 2.7)

The spike build was published unchanged to GitHub Pages (branch `gh-pages`, folder `spike/`): https://aymanohm.github.io/project_gg/spike/

| What | Result |
|---|---|
| Starts on a static host | Yes, in Chrome. The blank page seen with a plain server on localhost does not happen here: on a real host the page loads the runtime and the pygame-ce wheel from `pygame-web.github.io` |
| Frame rate | 62.5 fps; frame time median 16 ms, p99 17 ms |
| Time until the "ready to start" prompt | about 6 s on a home connection, runtime not cached |
| What GitHub Pages serves | 80 KB (`index.html`, `pygbag.apk`, icon). Everything else comes from the pygbag CDN |
| WebSocket | Not tested: there is no public server to connect to yet |

So the localhost failure was a quirk of local development, not a deployment problem. The default setup (runtime from the pygbag CDN) is enough to ship; self-hosting the runtime stays an option if the CDN dependency becomes a concern. Firefox and Safari are still untested.

## How to reproduce

```bash
./spikes/pygbag/build.sh                                   # stage assets + build
uv run --with websockets python spikes/pygbag/echo_server.py &
uv run --group web pygbag spikes/pygbag                    # serves http://localhost:8000
```

Open the page, click once, move with the arrow keys or A/D, jump with Up or W. Metrics are in `window.gg_metrics` in the browser console.
