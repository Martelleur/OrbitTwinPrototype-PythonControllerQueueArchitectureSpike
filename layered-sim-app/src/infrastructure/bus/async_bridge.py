from __future__ import annotations
import asyncio
from typing import Dict
from domain.messages import Envelope
from .channels import ChannelRegistry

class AsyncBridge:
    def __init__(self, reg: ChannelRegistry, poll_interval: float = 0.02):
        self.reg = reg
        self.poll_interval = poll_interval
        self.queues: Dict[str, asyncio.Queue[Envelope]] = {name: asyncio.Queue() for name in reg.names()}
        self._task: asyncio.Task | None = None
        self._stopping = asyncio.Event()

    def start(self):
        if self._task is None: self._task = asyncio.create_task(self._pump())

    async def stop(self):
        self._stopping.set()
        if self._task: await self._task

    async def _pump(self):
        while not self._stopping.is_set():
            for name in self.reg.names():
                ch = self.reg.channel(name)
                for env in ch.try_drain():
                    self.queues[name].put_nowait(env)
            await asyncio.sleep(self.poll_interval)
