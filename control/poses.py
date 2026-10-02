# bionic_hand/control/poses.py
from enum import Enum
from typing import Dict

class Pose(Enum):
    OPEN_HAND   = "Mano Abierta"
    POWER_GRASP = "Puño Cerrado"
    PINCH_GRIP  = "Pinza Fina"
    POINTING    = "Señalar"

POSE_ACTUATOR_MAP: Dict[Pose, Dict[str, float]] = {
    Pose.OPEN_HAND:   {"index": 0.00, "group": 0.00, "thumb": 0.00},
    Pose.POWER_GRASP: {"index": 0.95, "group": 0.95, "thumb": 0.90},
    Pose.PINCH_GRIP:  {"index": 0.75, "group": 0.00, "thumb": 0.85},
    Pose.POINTING:    {"index": 0.00, "group": 1.00, "thumb": 0.90}
}