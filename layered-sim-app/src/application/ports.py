from __future__ import annotations
from typing import Protocol, Iterable, Optional
from domain.messages import Envelope

class EventPublisher(Protocol):
    def publish(self, env: Envelope) -> None: ...

class CommandInbox(Protocol):
    def drain(self) -> Iterable[Envelope]: ...

class ExternalProcess(Protocol):
    def poll(self) -> Optional[Envelope]: ...
