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
    Pose.PINCH_GRIP:  {"index": 0.828, "group": 0.00, "thumb": 0.262},
    Pose.POINTING:    {"index": 0.00, "group": 1.00, "thumb": 0.90}
}

# Diccionario simple de posturas para app_desktop.py
HAND_POSES: Dict[str, tuple] = {
    "OPEN": (0.00, 0.00, 0.00),      # Mano abierta
    "FIST": (0.95, 0.95, 0.90),      # Puño cerrado
    "PINCH": (0.828, 0.00, 0.262),     # Pinza fina
    "POINTING": (0.00, 1.00, 0.90)   # Señalar
}