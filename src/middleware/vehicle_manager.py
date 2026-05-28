"""
Middleware - Gerenciador de Integração Veicular.

Processa dados do veículo recebidos via CAN Bus, gera alertas
e fornece informações formatadas para a HMI.
"""

import logging
from dataclasses import dataclass, field

from src.hal.can_bus import CANBusInterface, DoorPosition, VehicleData

logger = logging.getLogger(__name__)

SPEED_LIMIT_ALERT_KMH = 120.0
FUEL_LOW_THRESHOLD_PERCENT = 15.0
ENGINE_TEMP_HIGH_CELSIUS = 110.0


@dataclass
class VehicleAlert:
    """Alerta gerado pela análise dos dados veiculares."""
    level: str  # "INFO", "WARNING", "CRITICAL"
    message: str


@dataclass
class VehicleStatus:
    """Status processado do veículo para a HMI."""
    speed_kmh: float = 0.0
    rpm: int = 0
    fuel_level_percent: float = 100.0
    engine_temp_celsius: float = 90.0
    doors_open: list[str] = field(default_factory=list)
    parking_brake: bool = True
    headlights_on: bool = False
    alerts: list[VehicleAlert] = field(default_factory=list)

    @property
    def fuel_bar(self) -> str:
        """Barra visual do nível de combustível."""
        filled = int(self.fuel_level_percent / 10)
        return "█" * filled + "░" * (10 - filled)

    @property
    def speed_display(self) -> str:
        """Velocidade formatada."""
        return f"{self.speed_kmh:.0f} km/h"


class VehicleManager:
    """Processa e monitora dados veiculares vindos do CAN Bus."""

    def __init__(self, can_bus_hal: CANBusInterface) -> None:
        self._can = can_bus_hal
        self._last_data = VehicleData()

    def read_data(self) -> VehicleStatus:
        """Lê dados do CAN Bus e retorna status processado com alertas."""
        raw: VehicleData = self._can.read_vehicle_data()
        self._last_data = raw

        alerts = self._check_alerts(raw)

        return VehicleStatus(
            speed_kmh=round(raw.speed_kmh, 1),
            rpm=raw.rpm,
            fuel_level_percent=round(raw.fuel_level_percent, 1),
            engine_temp_celsius=round(raw.engine_temp_celsius, 1),
            doors_open=[d.value for d in raw.doors_open],
            parking_brake=raw.parking_brake,
            headlights_on=raw.headlights_on,
            alerts=alerts,
        )

    @staticmethod
    def _check_alerts(data: VehicleData) -> list[VehicleAlert]:
        """Analisa dados do veículo e gera alertas quando necessário."""
        alerts: list[VehicleAlert] = []

        if data.speed_kmh > SPEED_LIMIT_ALERT_KMH:
            alerts.append(VehicleAlert(
                "WARNING",
                f"Velocidade alta: {data.speed_kmh:.0f} km/h! Reduza a velocidade.",
            ))

        if data.fuel_level_percent < FUEL_LOW_THRESHOLD_PERCENT:
            alerts.append(VehicleAlert(
                "WARNING",
                f"Combustível baixo: {data.fuel_level_percent:.1f}%. Abasteça em breve.",
            ))

        if data.engine_temp_celsius > ENGINE_TEMP_HIGH_CELSIUS:
            alerts.append(VehicleAlert(
                "CRITICAL",
                f"Temperatura do motor alta: {data.engine_temp_celsius:.1f}°C!",
            ))

        if data.doors_open:
            door_names = ", ".join(d.value for d in data.doors_open)
            alerts.append(VehicleAlert(
                "INFO",
                f"Porta(s) aberta(s): {door_names}.",
            ))

        return alerts
