"""pygbag spike (roadmap task 1.10). Throwaway code: not the real client.

Renders map.json and a player with idle/run animation, runs v1-like movement,
and measures frame rate, asset load time and a WebSocket round trip.

Desktop:  uv run python spikes/pygbag/main.py   (after ./spikes/pygbag/build.sh --assets-only)
Browser:  ./spikes/pygbag/build.sh, then serve spikes/pygbag/build/web
"""

import asyncio
import json
import os
import sys
import time

import pygame as pg

WEB = sys.platform == "emscripten"
W, H = 1280, 720
TILE = 45
PHYSICS = {"grass", "stone"}
HERE = os.path.dirname(os.path.abspath(__file__))
WS_URL = "ws://localhost:8765"

metrics = {"web": WEB, "python": sys.version.split()[0], "pygame": pg.version.ver}


def publish():
    """Expose metrics to the page so they can be read from the browser console."""
    if WEB:
        import platform

        platform.window.gg_metrics = json.dumps(metrics)


def load_dir(path, scale):
    names = sorted(os.listdir(path), key=lambda n: int(n.split(".")[0]))
    out = []
    for n in names:
        img = pg.image.load(os.path.join(path, n)).convert_alpha()
        out.append(pg.transform.scale(img, scale))
    return out


class WebSocketProbe:
    """Round-trip probe using the browser's WebSocket through JS interop."""

    JS = """
    (function(url){
      var s = {state:'connecting', inbox:[], sock:null};
      try {
        s.sock = new WebSocket(url);
        s.sock.onopen = function(){ s.state='open'; };
        s.sock.onmessage = function(e){ s.inbox.push(e.data); };
        s.sock.onerror = function(){ s.state='error'; };
        s.sock.onclose = function(){ if (s.state!=='error') s.state='closed'; };
      } catch (e) { s.state='error:'+e; }
      window.gg_ws = s;
    })('%s')
    """

    def __init__(self):
        self.sent_at = None
        self.rtts = []
        self.ok = False
        if WEB:
            import platform

            self.win = platform.window
            try:
                self.win.eval(self.JS % WS_URL)
                self.ok = True
            except Exception as e:  # noqa: BLE001 - spike: record whatever breaks
                metrics["ws_error"] = repr(e)

    def poll(self):
        if not self.ok:
            return
        s = self.win.gg_ws
        metrics["ws_state"] = str(s.state)
        if str(s.state) != "open" or len(self.rtts) >= 200:
            return
        while int(s.inbox.length) > 0:
            s.inbox.shift()
            if self.sent_at is not None:
                self.rtts.append((time.perf_counter() - self.sent_at) * 1000)
                self.sent_at = None
        if self.sent_at is None:
            self.sent_at = time.perf_counter()
            s.sock.send(
                json.dumps({"t": "input", "left": False, "right": True, "seq": len(self.rtts)})
            )
        if self.rtts:
            r = sorted(self.rtts)
            metrics["ws_rtt_ms_median"] = round(r[len(r) // 2], 2)
            metrics["ws_rtt_ms_max"] = round(r[-1], 2)
            metrics["ws_round_trips"] = len(r)


async def main():
    t0 = time.perf_counter()
    pg.init()
    screen = pg.display.set_mode((W, H))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 28)

    data = os.path.join(HERE, "data")
    tiles = {
        k: load_dir(f"{data}/tiles/{k}", (TILE, TILE))
        for k in ("grass", "stone", "decor", "large_decor")
    }
    anims = {a: load_dir(f"{data}/entities/player/{a}", (35, 55)) for a in ("idle", "run", "jump")}
    with open(os.path.join(data, "map.json")) as f:
        tilemap = json.load(f)["tilemap"]
    solid = {tuple(t["pos"]) for t in tilemap.values() if t["type"] in PHYSICS}
    metrics["asset_load_ms"] = round((time.perf_counter() - t0) * 1000)
    metrics["tiles"] = len(tilemap)

    # v1 constants: world is Y-up, position is the bottom-left corner.
    pos, vy, on_ground, flip, frame = [900.0, 600.0], 0.0, False, False, 0
    scroll = [0.0, 0.0]
    probe = WebSocketProbe()
    frame_ms, keys_seen, n = [], 0, 0

    def hits(x, y):
        for tx in range(int(x // TILE), int((x + 34.99) // TILE) + 1):
            for ty in range(int(y // TILE), int((y + 54.99) // TILE) + 1):
                if (tx, ty) in solid:
                    return True
        return False

    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return
            if e.type == pg.KEYDOWN:
                keys_seen += 1
                if e.key in (pg.K_UP, pg.K_w) and on_ground:
                    vy = 5.0
        k = pg.key.get_pressed()
        dx = (k[pg.K_RIGHT] or k[pg.K_d]) - (k[pg.K_LEFT] or k[pg.K_a])

        if dx and not hits(pos[0] + dx * 6, pos[1]):
            pos[0] += dx * 6
        flip = dx < 0 if dx else flip
        vy = max(-10.0, vy - 0.2)
        on_ground = False
        if hits(pos[0], pos[1] + vy):
            on_ground = vy < 0
            vy = 0.0
        else:
            pos[1] += vy
        if pos[1] < -300:
            pos, vy = [900.0, 600.0], 0.0

        scroll[0] += (pos[0] - W / 2 - scroll[0]) / 30
        scroll[1] += (pos[1] - H / 2 - scroll[1]) / 30

        screen.fill((72, 160, 211))
        for t in tilemap.values():
            sx = t["pos"][0] * TILE - scroll[0]
            sy = H - (t["pos"][1] * TILE - scroll[1]) - TILE
            if -TILE < sx < W and -TILE < sy < H:
                screen.blit(tiles[t["type"]][t["variant"]], (sx, sy))
        action = "jump" if not on_ground else "run" if dx else "idle"
        img = anims[action][(frame // 5) % len(anims[action])]
        screen.blit(
            pg.transform.flip(img, flip, False), (pos[0] - scroll[0], H - (pos[1] - scroll[1]) - 55)
        )
        frame += 1

        fps = clock.get_fps()
        hud = f"fps {fps:5.1f}  keys {keys_seen}  ws {metrics.get('ws_state', '-')} rtt {metrics.get('ws_rtt_ms_median', '-')}"
        screen.blit(font.render(hud, True, (0, 0, 0)), (10, 10))
        pg.display.flip()

        frame_ms.append(clock.tick(60))
        n += 1
        probe.poll()
        if n % 60 == 0:
            recent = sorted(frame_ms[-600:])
            metrics.update(
                frames=n,
                fps=round(fps, 1),
                frame_ms_median=recent[len(recent) // 2],
                frame_ms_p99=recent[int(len(recent) * 0.99) - 1],
                keys_seen=keys_seen,
                player_x=round(pos[0]),
            )
            publish()
            if not WEB and n % 300 == 0:
                print(metrics)
        await asyncio.sleep(0)


asyncio.run(main())
