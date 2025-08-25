from __future__ import annotations
import tkinter as tk
from application.controller import Controller
from application.ports import EventPublisher, CommandInbox, ExternalProcess
from infrastructure.bus.channels import ChannelRegistry, ChannelConfig
from infrastructure.bus.message_bus import BusPublisher, BusInbox
from infrastructure.bus.tk_pump import tk_pump
from infrastructure.external.external_proc import SimExternal
from .tk_app import TkApp

def build_registry() -> ChannelRegistry:
    return ChannelRegistry([
        ChannelConfig('kpi', maxsize=1000, policy='drop_old'),
        ChannelConfig('setup', maxsize=10, policy='block'),
    ])

def main():
    reg = build_registry()
    events: EventPublisher   = BusPublisher(reg.channel('kpi'))
    commands: CommandInbox   = BusInbox(reg.channel('setup'))
    external: ExternalProcess = SimExternal()
    ctl = Controller(events, commands, external)
    ctl.start()

    root = tk.Tk()
    ui = TkApp(root)

    tk_pump(root, reg, ui.on_event, every_ms=30)

    def on_close():
        ctl.stop()
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()

if __name__ == '__main__':
    main()
