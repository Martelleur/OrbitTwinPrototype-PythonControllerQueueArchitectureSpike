from __future__ import annotations
import tkinter as tk
from typing import Callable
from domain.messages import Envelope
from .channels import ChannelRegistry

def tk_pump(root: tk.Tk, reg: ChannelRegistry, on_event: Callable[[Envelope], None], every_ms: int = 30) -> None:
    def _drain():
        for name in reg.names():
            for env in reg.channel(name).try_drain():
                on_event(env)
        root.after(every_ms, _drain)
    _drain()
