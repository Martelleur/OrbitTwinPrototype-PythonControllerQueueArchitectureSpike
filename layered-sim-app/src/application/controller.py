from __future__ import annotations
import threading, time
from typing import Optional
from .ports import EventPublisher, CommandInbox, ExternalProcess
from domain.messages import Envelope

class Controller:
    def __init__(self, events: EventPublisher, commands: CommandInbox, external: ExternalProcess, period_sec: float = 0.05):
        self.events = events
        self.commands = commands
        self.external = external
        self.period = period_sec
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive(): return
        self._thread = threading.Thread(target=self._run, name='ControllerThread', daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread: self._thread.join(timeout=2.0)

    def _run(self) -> None:
        while not self._stop.is_set():
            for env in self.commands.drain():
                self._handle_command(env)
            env = self.external.poll()
            if env is not None:
                self.events.publish(env)
            time.sleep(self.period)

    def _handle_command(self, env: Envelope) -> None:
        pass
