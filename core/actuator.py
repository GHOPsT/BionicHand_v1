"""
Abstracción de servomotores físicos para BionicHand.
Mapea comandos normalizados [0.0, 1.0] a pulsos PWM (microsegundos).
"""

class ServoActuator:
    def __init__(self, name: str, min_us: float = 1000.0, max_us: float = 2000.0, max_angle_deg: float = 180.0):
        self.name = name
        self.min_us = min_us
        self.max_us = max_us
        self.max_angle_deg = max_angle_deg
        self._command = 0.0

    @property
    def command(self) -> float:
        return self._command

    @command.setter
    def command(self, value: float):
        self._command = float(max(0.0, min(1.0, value)))

    @property
    def pwm_us(self) -> float:
        return self.min_us + self._command * (self.max_us - self.min_us)

    @property
    def shaft_angle_deg(self) -> float:
        return self._command * self.max_angle_deg