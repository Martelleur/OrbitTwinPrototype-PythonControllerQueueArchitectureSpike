from __future__ import annotations
import threading, time, math, random
from typing import Callable
from channels import ChannelRegistry
from messages import Envelope, Telemetry, FrameMsg, Detection, PoseMsg

class Controller:
    """Runs in a background thread. Talks only to the ChannelRegistry."""
    def __init__(self, reg: ChannelRegistry, on_error: Callable[[Exception], None] | None = None):
        self.reg = reg
        self._stop = threading.Event()
        self._on_error = on_error or (lambda e: None)
        self._thread: threading.Thread | None = None
        self._t0 = time.perf_counter()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, name="ControllerThread", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    # --- Example "external process" simulation ---
    def _run(self):
        try:
            phase = 0.0
            while not self._stop.is_set():
                now = time.time()

                # 1) Read commands/setup if any
                setup_ch = self.reg.channel("setup")
                for env in setup_ch.try_drain():
                    # Apply setup/config commands here (env.payload)
                    pass

                # 2) Push telemetry / KPI
                val = math.sin(phase) + random.uniform(-0.05, 0.05)
                env = Envelope(topic="kpi", payload=Telemetry(source="sim", value=val), ts=now)
                self.reg.channel("kpi").put(env)

                # 3) Pose and detections
                pose = Envelope(topic="pose", payload=PoseMsg(x=math.sin(phase), y=math.cos(phase), z=0.0,
                                                              yaw=phase%6.28, pitch=0.0, roll=0.0), ts=now)
                self.reg.channel("pose").put(pose)

                det = Envelope(topic="detections", payload=Detection(cls="target", conf=0.9,
                                                                     x=42, y=40, w=100, h=80), ts=now)
                self.reg.channel("detections").put(det)

                # 4) Frames (latest wins)
                for t in ("visual_frame","thermal_frame","lidar_frame"):
                    frame = Envelope(topic=t, payload=FrameMsg(path=None, ts=now), ts=now)
                    self.reg.channel(t).put(frame)

                # 5) Image message logs (bounded)
                for t in ("visual_image_msg","thermal_image_msg","lidar_image_msg"):
                    msg = Envelope(topic=t, payload={"saved": True, "path": f"/tmp/{t}_{int(now)}.png"}, ts=now)
                    self.reg.channel(t).put(msg)

                phase += 0.05
                time.sleep(0.05)  # simulate I/O pace
        except Exception as e:
            self._on_error(e)
