from __future__ import annotations
import tkinter as tk
from domain.messages import Envelope

class TkApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('KPI Telemetry')
        self.label = tk.Label(root, text='waiting…', width=40, font=('Segoe UI', 14))
        self.label.pack(padx=10, pady=10)

    def on_event(self, env: Envelope):
        if env.topic == 'kpi':
            self.label.config(text=f"KPI: {env.payload['value']:.3f}")
