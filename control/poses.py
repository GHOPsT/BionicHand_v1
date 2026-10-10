# bionic_hand/control/poses.py
from enum import Enum
from typing import Dict

class Pose(Enum):
    OPEN_HAND   = "Mano Abierta"
    POWER_GRASP = "Puño Cerrado"
    PINCH_GRIP  = "Pinza Fina"
    POINTING    = "Señalar"
    THUMBS_UP   = "Pulgar Arriba"
    OK_SIGN     = "Gesto OK"
    RELAX       = "Relajada"
    GRAB        = "Agarre Neutro"

POSE_ACTUATOR_MAP: Dict[Pose, Dict[str, float]] = {
    Pose.OPEN_HAND:   {"index": 0.00, "group": 0.00, "thumb": 0.00},
    Pose.POWER_GRASP: {"index": 0.95, "group": 0.95, "thumb": 0.90},
    Pose.PINCH_GRIP:  {"index": 0.828, "group": 0.00, "thumb": 0.262},
    Pose.POINTING:    {"index": 0.00, "group": 1.00, "thumb": 0.90},
    Pose.THUMBS_UP:   {"index": 0.95, "group": 0.95, "thumb": 0.00},
    Pose.OK_SIGN:     {"index": 0.90, "group": 0.00, "thumb": 0.85},
    Pose.RELAX:       {"index": 0.30, "group": 0.25, "thumb": 0.20},
    Pose.GRAB:        {"index": 0.85, "group": 0.80, "thumb": 0.50}
}

# Diccionario simple de posturas para main.py
HAND_POSES: Dict[str, tuple] = {
    "OPEN": (0.00, 0.00, 0.00),      # Mano abierta
    "FIST": (0.95, 0.95, 0.90),      # Puño cerrado
    "PINCH": (0.828, 0.00, 0.262),   # Pinza fina
    "POINTING": (0.00, 1.00, 0.90),  # Señalar
    "THUMBS_UP": (0.95, 0.95, 0.00), # Pulgar hacia arriba
    "OK_SIGN": (0.90, 0.00, 0.85),   # Gesto OK (índice y pulgar unidos)
    "RELAX": (0.30, 0.25, 0.20),     # Mano relajada (semi-abierta)
    "GRAB": (0.85, 0.80, 0.50)       # Agarre neutro
}