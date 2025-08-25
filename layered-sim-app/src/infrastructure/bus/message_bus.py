from __future__ import annotations
from typing import Iterable
from domain.messages import Envelope
from .channels import Channel, ChannelRegistry

class BusPublisher:
    def __init__(self, out_ch: Channel[Envelope]): self._ch = out_ch
    def publish(self, env: Envelope) -> None: self._ch.put(env)

class BusInbox:
    def __init__(self, in_ch: Channel[Envelope]): self._ch = in_ch
    def drain(self) -> Iterable[Envelope]: return self._ch.try_drain()
