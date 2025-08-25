from __future__ import annotations
import tkinter as tk
from channels import ChannelConfig, ChannelRegistry
from controller import Controller
from messages import Envelope

def build_registry() -> ChannelRegistry:
    return ChannelRegistry([
        ChannelConfig("visual_frame", maxsize=1, policy="latest"),
        ChannelConfig("thermal_frame", maxsize=1, policy="latest"),
        ChannelConfig("lidar_frame",   maxsize=1, policy="latest"),
        ChannelConfig("kpi",           maxsize=1000, policy="drop_old"),
        ChannelConfig("detections",    maxsize=1000, policy="drop_old"),
        ChannelConfig("pose",          maxsize=1000, policy="drop_old"),
        ChannelConfig("setup",         maxsize=10, policy="block"),
        ChannelConfig("visual_image_msg",  maxsize=1000, policy="drop_old"),
        ChannelConfig("thermal_image_msg", maxsize=1000, policy="drop_old"),
        ChannelConfig("lidar_image_msg",   maxsize=1000, policy="drop_old"),
    ])

def run_gui():
    reg = build_registry()
    ctl = Controller(reg)
    ctl.start()

    root = tk.Tk()
    root.title("Telemetry (KPI)")

    label = tk.Label(root, text="waiting…", width=40, font=("Segoe UI", 14))
    label.pack(padx=10, pady=10)

    pose_label = tk.Label(root, text="pose: —", width=60)
    pose_label.pack(padx=10, pady=5)

    def pump():
        for env in reg.channel("kpi").try_drain():
            label.config(text=f"KPI value: {env.payload['value']:.3f}")
        for env in reg.channel("pose").try_drain():
            p = env.payload
            pose_label.config(text=f"pose: x={p['x']:.3f} y={p['y']:.3f} yaw={p['yaw']:.3f}")
        root.after(30, pump)

    def on_close():
        ctl.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    pump()
    root.mainloop()

if __name__ == "__main__":
    run_gui()
