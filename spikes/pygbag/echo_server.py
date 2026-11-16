"""WebSocket echo server for the spike's round-trip probe: uv run --with websockets python spikes/pygbag/echo_server.py"""

import asyncio

import websockets


async def echo(ws):
    async for msg in ws:
        await ws.send(msg)


async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()


asyncio.run(main())
