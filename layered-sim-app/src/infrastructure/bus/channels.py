from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Dict, Iterable
import queue

T = TypeVar('T')

@dataclass(frozen=True)
class ChannelConfig:
    name: str
    maxsize: int = 0
    policy: str = 'block'   # 'block' | 'drop_new' | 'drop_old' | 'latest'

class Channel(Generic[T]):
    def __init__(self, cfg: ChannelConfig):
        self.cfg = cfg
        self._q: queue.Queue[T] = queue.Queue(maxsize=cfg.maxsize)

    def put(self, item: T) -> None:
        p = self.cfg.policy
        if p == 'block':
            self._q.put(item)
        elif p == 'drop_new':
            try: self._q.put_nowait(item)
            except queue.Full: pass
        elif p == 'drop_old':
            while True:
                try:
                    self._q.put_nowait(item); break
                except queue.Full:
                    try: self._q.get_nowait()
                    except queue.Empty: break
        elif p == 'latest':
            while True:
                try:
                    self._q.put_nowait(item); break
                except queue.Full:
                    try: self._q.get_nowait()
                    except queue.Empty: break

    def get(self, timeout: Optional[float] = None):
        return self._q.get(timeout=timeout)

    def try_drain(self) -> Iterable[T]:
        while True:
            try: yield self._q.get_nowait()
            except queue.Empty: break

class ChannelRegistry:
    def __init__(self, configs: Iterable[ChannelConfig]):
        self._by_name: Dict[str, Channel] = {cfg.name: Channel(cfg) for cfg in configs}
    def channel(self, name: str) -> Channel:
        return self._by_name[name]
    def names(self):
        return list(self._by_name.keys())
