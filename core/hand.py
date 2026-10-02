"""
Controlador maestro de BionicHand.
Orquesta los 3 canales de servomotores y la cinemática de los 5 dedos.
"""
from typing import Dict, List
from config.dimensions import FINGER_DIMENSIONS, PALM_SPACING
from core.finger import Finger
from core.actuator import ServoActuator

class BionicHand:
    def __init__(self):
        # 1. Los 3 canales de servomotores reales
        self.servo_index = ServoActuator("Servo_Index")
        self.servo_group = ServoActuator("Servo_Group")
        self.servo_thumb = ServoActuator("Servo_Thumb_ASV15MG")

        # 2. Orígenes geométricos en la palma (X, Y en mm)
        x_idx, y_idx = 0.0, 70.0
        x_mid, y_mid = x_idx + PALM_SPACING["index_to_middle"], y_idx + 4.0
        x_rng, y_rng = x_mid + PALM_SPACING["middle_to_ring"], y_idx + 1.0
        x_pnk, y_pnk = x_rng + PALM_SPACING["ring_to_pinky"], y_idx - 6.0
        x_thb, y_thb = x_idx - 26.0, y_idx - PALM_SPACING["index_to_thumb_proj"] + 5.0

        # 3. Instanciación de dedos con parámetros del CAD
        self.thumb = Finger("Pulgar", (x_thb, y_thb), FINGER_DIMENSIONS["thumb"]["l1_proximal"], FINGER_DIMENSIONS["thumb"]["l2_distal"], is_thumb=True)
        self.index = Finger("Índice", (x_idx, y_idx), FINGER_DIMENSIONS["index"]["l1_proximal"], FINGER_DIMENSIONS["index"]["l2_distal"], l_biela=FINGER_DIMENSIONS["index"]["l_biela"])
        self.middle = Finger("Medio", (x_mid, y_mid), FINGER_DIMENSIONS["middle"]["l1_proximal"], FINGER_DIMENSIONS["middle"]["l2_distal"], l_biela=FINGER_DIMENSIONS["middle"]["l_biela"])
        self.ring = Finger("Anular", (x_rng, y_rng), FINGER_DIMENSIONS["ring"]["l1_proximal"], FINGER_DIMENSIONS["ring"]["l2_distal"], l_biela=FINGER_DIMENSIONS["ring"]["l_biela"])
        self.pinky = Finger("Meñique", (x_pnk, y_pnk), FINGER_DIMENSIONS["pinky"]["l1_proximal"], FINGER_DIMENSIONS["pinky"]["l2_distal"], l_biela=FINGER_DIMENSIONS["pinky"]["l_biela"])

        self.fingers: List[Finger] = [self.thumb, self.index, self.middle, self.ring, self.pinky]

    def set_actuators(self, u_index: float, u_group: float, u_thumb: float):
        """Aplica señales normalizadas [0.0, 1.0] a los 3 actuadores físicos."""
        self.servo_index.command = u_index
        self.servo_group.command = u_group
        self.servo_thumb.command = u_thumb

        # Propagación mecánica a los dedos
        self.index.set_flexion(self.servo_index.command)
        self.middle.set_flexion(self.servo_group.command)
        self.ring.set_flexion(self.servo_group.command)
        self.pinky.set_flexion(self.servo_group.command)
        self.thumb.set_flexion(self.servo_thumb.command)

    def get_joint_state(self) -> Dict[str, Dict[str, float]]:
        """Matriz de estados articulares en grados (salida para CoppeliaSim en Etapa 2)."""
        return {f.name: {"mcp_deg": f.mcp.angle, "pip_deg": f.pip.angle} for f in self.fingers}

    def get_telemetry(self) -> dict:
        return {
            "actuators": {
                "servo_index": {"cmd": self.servo_index.command, "pwm_us": self.servo_index.pwm_us},
                "servo_group": {"cmd": self.servo_group.command, "pwm_us": self.servo_group.pwm_us},
                "servo_thumb": {"cmd": self.servo_thumb.command, "pwm_us": self.servo_thumb.pwm_us},
            },
            "joints": self.get_joint_state(),
            "tips": {f.name: f.get_tip_position().tolist() for f in self.fingers}
        }