from __future__ import annotations
import time, math, random
from typing import Optional
from domain.messages import Envelope, Telemetry

class SimExternal:
    def __init__(self): self._phase = 0.0
    def poll(self) -> Optional[Envelope]:
        now = time.time()
        val = math.sin(self._phase) + random.uniform(-0.05, 0.05)
        self._phase += 0.05
        return Envelope(topic='kpi', payload=Telemetry(source='sim', value=val), ts=now)
