"""
Modelo cinemático y geométrico del dedo para BionicHand.
Implementa cinemática directa y el acoplamiento del mecanismo de cuatro barras.
"""
import numpy as np
from core.joint import Joint
from config.dimensions import JOINT_LIMITS, COUPLING_RATIO_4BAR

class Finger:
    def __init__(
        self,
        name: str,
        origin: tuple,
        l1: float,
        l2: float,
        l_biela: float = None,
        is_thumb: bool = False
    ):
        self.name = name
        self.origin = np.array(origin, dtype=float)
        self.l1 = float(l1)
        self.l2 = float(l2)
        self.l_biela = float(l_biela) if l_biela is not None else None
        self.is_thumb = is_thumb

        if self.is_thumb:
            min_base, max_base = JOINT_LIMITS["thumb_base_flexion"]
            min_mid, max_mid = JOINT_LIMITS["thumb_pip_flexion"]
        else:
            min_base, max_base = JOINT_LIMITS["mcp_base_flexion"]
            min_mid, max_mid = JOINT_LIMITS["pip_middle_flexion"]

        self.mcp = Joint(f"{name}_mcp", min_deg=min_base, max_deg=max_base)
        self.pip = Joint(f"{name}_pip", min_deg=min_mid, max_deg=max_mid)

    def set_flexion(self, normalized_val: float):
        """Flexiona el dedo según la señal normalizada [0.0, 1.0]."""
        self.mcp.set_normalized(normalized_val)
        if self.is_thumb:
            self.pip.set_normalized(normalized_val * 0.90)
        else:
            self.pip.set_normalized(normalized_val * COUPLING_RATIO_4BAR)

    def get_positions(self) -> np.ndarray:
        """Retorna matriz (3, 2): [P0_Base, P1_Nudillo, P2_Yema] en milímetros."""
        theta1 = np.radians(self.mcp.angle)
        theta2 = np.radians(self.pip.angle)
        p0 = self.origin

        if self.is_thumb:
            p1 = p0 + np.array([self.l1 * np.cos(theta1), -self.l1 * np.sin(theta1)])
            phi = theta1 + theta2
            p2 = p1 + np.array([self.l2 * np.cos(phi), -self.l2 * np.sin(phi)])
        else:
            p1 = p0 + np.array([self.l1 * np.sin(theta1), -self.l1 * np.cos(theta1)])
            phi = theta1 + theta2
            p2 = p1 + np.array([self.l2 * np.sin(phi), -self.l2 * np.cos(phi)])

        return np.array([p0, p1, p2])

    def get_tip_position(self) -> np.ndarray:
        return self.get_positions()