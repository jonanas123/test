"""
Middleware - Gerenciador de Climatização (HVAC).

Controla o sistema de ar-condicionado, aquecimento e ventilação
com limites de segurança e validações.
"""

import logging
from dataclasses import dataclass

from src.hal.hvac_hal import (
    HVACInterface,
    HVACState,
    MAX_FAN_SPEED,
    MAX_TEMP_CELSIUS,
    MIN_FAN_SPEED,
    MIN_TEMP_CELSIUS,
)

logger = logging.getLogger(__name__)

TEMP_STEP = 0.5


@dataclass
class ClimateStatus:
    """Status de climatização para a HMI."""
    power_on: bool
    target_temp: float
    current_temp: float
    fan_speed: int
    max_fan: int
    ac_on: bool


class HVACManager:
    """Gerencia o sistema de climatização com validações de segurança."""

    def __init__(self, hvac_hal: HVACInterface) -> None:
        self._hvac = hvac_hal

    def get_status(self) -> ClimateStatus:
        """Retorna o status atual da climatização."""
        state: HVACState = self._hvac.get_state()
        return ClimateStatus(
            power_on=state.power_on,
            target_temp=state.target_temp_celsius,
            current_temp=state.current_temp_celsius,
            fan_speed=state.fan_speed,
            max_fan=MAX_FAN_SPEED,
            ac_on=state.ac_on,
        )

    def increase_temperature(self) -> float:
        """Aumenta a temperatura em 0.5°C."""
        state = self._hvac.get_state()
        new_temp = state.target_temp_celsius + TEMP_STEP
        if new_temp > MAX_TEMP_CELSIUS:
            logger.warning(
                "[HVAC-MGR] Temperatura máxima atingida: %.1f°C.",
                MAX_TEMP_CELSIUS,
            )
            return state.target_temp_celsius
        return self._hvac.set_temperature(new_temp)

    def decrease_temperature(self) -> float:
        """Diminui a temperatura em 0.5°C."""
        state = self._hvac.get_state()
        new_temp = state.target_temp_celsius - TEMP_STEP
        if new_temp < MIN_TEMP_CELSIUS:
            logger.warning(
                "[HVAC-MGR] Temperatura mínima atingida: %.1f°C.",
                MIN_TEMP_CELSIUS,
            )
            return state.target_temp_celsius
        return self._hvac.set_temperature(new_temp)

    def set_temperature(self, temp: float) -> float:
        """Define a temperatura diretamente."""
        return self._hvac.set_temperature(temp)

    def increase_fan(self) -> int:
        """Aumenta a velocidade do ventilador."""
        state = self._hvac.get_state()
        new_speed = state.fan_speed + 1
        if new_speed > MAX_FAN_SPEED:
            logger.warning("[HVAC-MGR] Ventilador já na velocidade máxima.")
            return state.fan_speed
        return self._hvac.set_fan_speed(new_speed)

    def decrease_fan(self) -> int:
        """Diminui a velocidade do ventilador."""
        state = self._hvac.get_state()
        new_speed = state.fan_speed - 1
        if new_speed < MIN_FAN_SPEED:
            logger.warning("[HVAC-MGR] Ventilador já na velocidade mínima.")
            return state.fan_speed
        return self._hvac.set_fan_speed(new_speed)

    def toggle_ac(self) -> bool:
        """Liga/desliga o A/C."""
        return self._hvac.toggle_ac()

    def toggle_power(self) -> bool:
        """Liga/desliga o sistema HVAC."""
        return self._hvac.toggle_power()
