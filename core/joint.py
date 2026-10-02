"""
Módulo de articulación rotacional (Joint).
Gestiona topes físicos mecánicos, normalización y asignación segura de ángulos.
"""

class Joint:
    def __init__(self, name: str, min_deg: float = 0.0, max_deg: float = 80.0):
        self.name = name
        self.min_deg = float(min_deg)
        self.max_deg = float(max_deg)
        self._current_angle = float(min_deg)

    @property
    def angle(self) -> float:
        """Ángulo actual de la articulación en grados."""
        return self._current_angle

    @angle.setter
    def angle(self, deg: float):
        """Asigna el ángulo garantizando el estricto cumplimiento de topes físicos."""
        self._current_angle = float(max(self.min_deg, min(self.max_deg, deg)))

    @property
    def normalized(self) -> float:
        """Retorna el estado de flexión normalizado en el intervalo [0.0, 1.0]."""
        if self.max_deg == self.min_deg:
            return 0.0
        return (self._current_angle - self.min_deg) / (self.max_deg - self.min_deg)

    def set_normalized(self, value: float):
        """Asigna el ángulo a partir de una señal de control normalizada [0.0, 1.0]."""
        val_clamped = max(0.0, min(1.0, float(value)))
        self.angle = self.min_deg + val_clamped * (self.max_deg - self.min_deg)

    def __repr__(self) -> str:
        return f"Joint({self.name}: {self._current_angle:.2f}° [{self.min_deg}° - {self.max_deg}°])"