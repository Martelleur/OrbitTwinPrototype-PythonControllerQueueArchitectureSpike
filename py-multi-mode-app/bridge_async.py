from __future__ import annotations
import asyncio
from typing import Dict
from channels import ChannelRegistry
from messages import Envelope

class AsyncBridge:
    """Polls registry channels and forwards items to asyncio queues (per topic).
    Run entirely on the asyncio thread; thread-safe because `Channel.try_drain` uses Queue.get_nowait().
    """
    def __init__(self, reg: ChannelRegistry, poll_interval: float = 0.02):
        self.reg = reg
        self.poll_interval = poll_interval
        self.async_queues: Dict[str, asyncio.Queue[Envelope]] = {name: asyncio.Queue() for name in reg.names()}
        self._task: asyncio.Task | None = None
        self._stopping = asyncio.Event()

    def get_async_queue(self, topic: str) -> asyncio.Queue[Envelope]:
        return self.async_queues[topic]

    def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._pump())

    async def stop(self):
        self._stopping.set()
        if self._task:
            await self._task

    async def _pump(self):
        while not self._stopping.is_set():
            for name in self.reg.names():
                ch = self.reg.channel(name)
                for env in ch.try_drain():
                    q = self.async_queues[name]
                    q.put_nowait(env)
            await asyncio.sleep(self.poll_interval)
