from __future__ import annotations
import json
import asyncio, signal
import websockets
from websockets.server import WebSocketServerProtocol
from channels import ChannelConfig, ChannelRegistry
from controller import Controller
from bridge_async import AsyncBridge
from messages import Envelope

def build_registry() -> ChannelRegistry:
    return ChannelRegistry([
        ChannelConfig("visual_frame", maxsize=1, policy="latest"),
        ChannelConfig("thermal_frame", maxsize=1, policy="latest"),
        ChannelConfig("lidar_frame",   maxsize=1, policy="latest"),
        ChannelConfig("kpi",           maxsize=1000, policy="drop_old"),
        ChannelConfig("detections",    maxsize=1000, policy="drop_old"),
        ChannelConfig("pose",          maxsize=1000, policy="drop_old"),
        ChannelConfig("setup",         maxsize=10, policy="block"),
        ChannelConfig("visual_image_msg",  maxsize=1000, policy="drop_old"),
        ChannelConfig("thermal_image_msg", maxsize=1000, policy="drop_old"),
        ChannelConfig("lidar_image_msg",   maxsize=1000, policy="drop_old"),
    ])

async def broadcaster(bridge: AsyncBridge, clients: set[WebSocketServerProtocol]):
    kpi_q = bridge.get_async_queue("kpi")
    while True:
        env: Envelope = await kpi_q.get()
        payload = {"topic": env.topic, "payload": env.payload, "ts": env.ts}
        msg = json.dumps(payload)
        stale = []
        for ws in list(clients):
            try:
                await ws.send(msg)
            except Exception:
                stale.append(ws)
        for ws in stale:
            clients.discard(ws)

async def handler(ws: WebSocketServerProtocol, reg: ChannelRegistry):
    await ws.send("hello")
    # If you need the URL path:
    # print("client requested path:", ws.path)

    setup_ch = reg.channel("setup")
    try:
        async for msg in ws:
            setup_ch.put(Envelope(topic="setup", payload={"raw": msg}, ts=0.0))
    except websockets.ConnectionClosed:
        pass

async def main():
    loop = asyncio.get_running_loop()

    reg = build_registry()
    ctl = Controller(reg)
    ctl.start()

    bridge = AsyncBridge(reg)
    bridge.start()

    clients: set[WebSocketServerProtocol] = set()

    async def ws_handler(ws: WebSocketServerProtocol):
        clients.add(ws)
        try:
            await handler(ws, reg)
        finally:
            clients.discard(ws)

    server = await websockets.serve(ws_handler, "127.0.0.1", 8765)
    print("WebSocket server on ws://127.0.0.1:8765")

    btask = asyncio.create_task(broadcaster(bridge, clients))

    stop = asyncio.Future()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.cancel)
        except NotImplementedError:
            pass
    try:
        await stop
    except:
        pass
    finally:
        btask.cancel()
        server.close()
        await server.wait_closed()
        await bridge.stop()
        ctl.stop()

if __name__ == "__main__":
    asyncio.run(main())
