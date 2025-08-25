from __future__ import annotations
import asyncio
from application.controller import Controller
from application.ports import EventPublisher, CommandInbox, ExternalProcess
from domain.messages import Envelope
from infrastructure.bus.channels import ChannelRegistry, ChannelConfig
from infrastructure.bus.message_bus import BusPublisher, BusInbox
from infrastructure.bus.async_bridge import AsyncBridge
from infrastructure.external.external_proc import SimExternal
from .websocket_app import run_server

def build_registry() -> ChannelRegistry:
    return ChannelRegistry([
        ChannelConfig('kpi', maxsize=1000, policy='drop_old'),
        ChannelConfig('setup', maxsize=10, policy='block'),
    ])

async def main():
    reg = build_registry()
    bridge = AsyncBridge(reg)
    bridge.start()

    events: EventPublisher   = BusPublisher(reg.channel('kpi'))
    commands: CommandInbox   = BusInbox(reg.channel('setup'))
    external: ExternalProcess = SimExternal()
    ctl = Controller(events, commands, external)
    ctl.start()

    def on_setup(raw: str):
        reg.channel('setup').put(Envelope(topic='setup', payload={'raw': raw}, ts=0.0))

    server, btask = await run_server(bridge, on_setup)
    print('WebSocket server on ws://127.0.0.1:8765')

    try:
        await asyncio.Future()
    finally:
        btask.cancel()
        server.close()
        await server.wait_closed()
        await bridge.stop()
        ctl.stop()
