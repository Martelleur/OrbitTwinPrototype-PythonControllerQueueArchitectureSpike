from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal, TypedDict

Topic = Literal['visual_frame','thermal_frame','lidar_frame','kpi','detections','pose','setup','visual_image_msg','thermal_image_msg','lidar_image_msg']

class Telemetry(TypedDict):
    source: str
    value: float

class FrameMsg(TypedDict):
    path: str | None
    ts: float

class Detection(TypedDict):
    cls: str
    conf: float
    x: int
    y: int
    w: int
    h: int

class PoseMsg(TypedDict):
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    roll: float

@dataclass(frozen=True)
class Envelope:
    topic: Topic
    payload: Any
    ts: float
