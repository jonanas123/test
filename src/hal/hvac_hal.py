"""
HAL - Abstração do sistema HVAC (Heating, Ventilation and Air Conditioning).

Define a interface para controle de climatização e fornece
uma implementação mock.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)

MIN_TEMP_CELSIUS = 16.0
MAX_TEMP_CELSIUS = 30.0
MIN_FAN_SPEED = 0
MAX_FAN_SPEED = 5


@dataclass
class HVACState:
    """Estado atual do sistema de climatização."""
    power_on: bool = False
    target_temp_celsius: float = 22.0
    current_temp_celsius: float = 25.0
    fan_speed: int = 1
    ac_on: bool = False
    recirculate: bool = False


class HVACInterface(ABC):
    """Interface abstrata para o sistema HVAC."""

    @abstractmethod
    def initialize(self) -> bool:
        """Inicializa o sistema HVAC."""

    @abstractmethod
    def get_state(self) -> HVACState:
        """Retorna o estado atual do HVAC."""

    @abstractmethod
    def set_temperature(self, temp_celsius: float) -> float:
        """Define a temperatura alvo. Retorna a temperatura efetiva."""

    @abstractmethod
    def set_fan_speed(self, speed: int) -> int:
        """Define a velocidade do ventilador (0-5). Retorna a velocidade efetiva."""

    @abstractmethod
    def toggle_ac(self) -> bool:
        """Liga/desliga o compressor A/C. Retorna o novo estado."""

    @abstractmethod
    def toggle_power(self) -> bool:
        """Liga/desliga o sistema HVAC. Retorna o novo estado."""

    @abstractmethod
    def shutdown(self) -> None:
        """Desliga o sistema HVAC."""


class MockHVAC(HVACInterface):
    """Implementação mock do sistema HVAC."""

    def __init__(self) -> None:
        self._state = HVACState()

    def initialize(self) -> bool:
        logger.info("[HVAC] Inicializando sistema de climatização (mock)...")
        self._state.power_on = True
        self._state.ac_on = True
        self._state.fan_speed = 2
        logger.info(
            "[HVAC] Sistema inicializado: %.1f°C, ventilador=%d.",
            self._state.target_temp_celsius,
            self._state.fan_speed,
        )
        return True

    def get_state(self) -> HVACState:
        return self._state

    def set_temperature(self, temp_celsius: float) -> float:
        clamped = max(MIN_TEMP_CELSIUS, min(MAX_TEMP_CELSIUS, temp_celsius))
        self._state.target_temp_celsius = clamped
        logger.info("[HVAC] Temperatura alvo ajustada para %.1f°C.", clamped)
        return clamped

    def set_fan_speed(self, speed: int) -> int:
        clamped = max(MIN_FAN_SPEED, min(MAX_FAN_SPEED, speed))
        self._state.fan_speed = clamped
        if clamped == 0:
            self._state.power_on = False
        else:
            self._state.power_on = True
        logger.info("[HVAC] Velocidade do ventilador ajustada para %d.", clamped)
        return clamped

    def toggle_ac(self) -> bool:
        self._state.ac_on = not self._state.ac_on
        status = "LIGADO" if self._state.ac_on else "DESLIGADO"
        logger.info("[HVAC] Compressor A/C %s.", status)
        return self._state.ac_on

    def toggle_power(self) -> bool:
        self._state.power_on = not self._state.power_on
        status = "LIGADO" if self._state.power_on else "DESLIGADO"
        logger.info("[HVAC] Sistema HVAC %s.", status)
        return self._state.power_on

    def shutdown(self) -> None:
        self._state.power_on = False
        self._state.ac_on = False
        self._state.fan_speed = 0
        logger.info("[HVAC] Sistema de climatização desligado.")
