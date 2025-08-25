from __future__ import annotations
import asyncio, json, websockets
from websockets.server import WebSocketServerProtocol
from typing import Callable, Set, Tuple
from domain.messages import Envelope
from infrastructure.bus.async_bridge import AsyncBridge

async def broadcaster(bridge: AsyncBridge, clients: Set[WebSocketServerProtocol]):
    q = bridge.queues['kpi']
    while True:
        env: Envelope = await q.get()
        msg = json.dumps({'topic': env.topic, 'payload': env.payload, 'ts': env.ts})
        dead = []
        for ws in list(clients):
            try: await ws.send(msg)
            except Exception: dead.append(ws)
        for ws in dead: clients.discard(ws)

async def run_server(bridge: AsyncBridge, on_setup: Callable[[str], None]):
    clients: Set[WebSocketServerProtocol] = set()

    async def handler(ws: WebSocketServerProtocol):
        await ws.send('hello')
        clients.add(ws)
        try:
            async for text in ws:
                on_setup(text)
        finally:
            clients.discard(ws)

    server = await websockets.serve(handler, '127.0.0.1', 8765)
    btask = asyncio.create_task(broadcaster(bridge, clients))
    return server, btask
