# bionic_hand/control/interfaces.py
from abc import ABC, abstractmethod
from typing import Tuple

class ICommandProvider(ABC):
    @abstractmethod
    def get_control_signals(self) -> Tuple[float, float, float]:
        """Retorna tupla normalizada (u_index, u_group, u_thumb) en [0.0, 1.0]."""
        pass