"""
HAL - Abstração da Rede CAN (Controller Area Network).

Define a interface abstrata para comunicação com o barramento CAN do veículo
e fornece uma implementação mock para simulação.
"""

import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class DoorPosition(Enum):
    FRONT_LEFT = "Dianteira Esquerda"
    FRONT_RIGHT = "Dianteira Direita"
    REAR_LEFT = "Traseira Esquerda"
    REAR_RIGHT = "Traseira Direita"
    TRUNK = "Porta-malas"


@dataclass
class VehicleData:
    """Dados recebidos do barramento CAN do veículo."""
    speed_kmh: float = 0.0
    rpm: int = 0
    fuel_level_percent: float = 100.0
    engine_temp_celsius: float = 90.0
    doors_open: list[DoorPosition] = field(default_factory=list)
    parking_brake: bool = True
    headlights_on: bool = False


class CANBusInterface(ABC):
    """Interface abstrata para comunicação com o barramento CAN."""

    @abstractmethod
    def initialize(self) -> bool:
        """Inicializa a conexão com o barramento CAN."""

    @abstractmethod
    def read_vehicle_data(self) -> VehicleData:
        """Lê dados atuais do veículo via CAN."""

    @abstractmethod
    def send_message(self, arbitration_id: int, data: bytes) -> bool:
        """Envia uma mensagem no barramento CAN."""

    @abstractmethod
    def shutdown(self) -> None:
        """Encerra a conexão com o barramento CAN."""


class MockCANBus(CANBusInterface):
    """Implementação mock do barramento CAN para simulação."""

    def __init__(self) -> None:
        self._connected = False
        self._vehicle_data = VehicleData()
        self._tick = 0

    def initialize(self) -> bool:
        logger.info("[CAN] Inicializando interface CAN Bus (mock)...")
        self._connected = True
        logger.info("[CAN] Interface CAN Bus conectada com sucesso.")
        return True

    def read_vehicle_data(self) -> VehicleData:
        if not self._connected:
            logger.warning("[CAN] Tentativa de leitura sem conexão ativa.")
            return VehicleData()

        self._tick += 1
        self._simulate_vehicle_dynamics()

        logger.debug(
            "[CAN] Dados lidos: velocidade=%.1f km/h, RPM=%d, "
            "combustível=%.1f%%, temp_motor=%.1f°C",
            self._vehicle_data.speed_kmh,
            self._vehicle_data.rpm,
            self._vehicle_data.fuel_level_percent,
            self._vehicle_data.engine_temp_celsius,
        )
        return self._vehicle_data

    def send_message(self, arbitration_id: int, data: bytes) -> bool:
        if not self._connected:
            logger.error("[CAN] Impossível enviar: barramento desconectado.")
            return False

        logger.info(
            "[CAN] Mensagem enviada - ID: 0x%03X, Dados: %s",
            arbitration_id,
            data.hex(),
        )
        return True

    def shutdown(self) -> None:
        logger.info("[CAN] Encerrando interface CAN Bus...")
        self._connected = False

    def _simulate_vehicle_dynamics(self) -> None:
        """Simula variações realistas nos dados do veículo."""
        data = self._vehicle_data

        speed_delta = random.uniform(-5, 5)
        data.speed_kmh = max(0, min(220, data.speed_kmh + speed_delta))

        data.rpm = int(800 + (data.speed_kmh / 220) * 6200)

        if self._tick % 10 == 0:
            data.fuel_level_percent = max(
                0, data.fuel_level_percent - random.uniform(0.1, 0.3)
            )

        data.engine_temp_celsius = 85 + random.uniform(-5, 10)

        if self._tick % 20 == 0:
            all_doors = list(DoorPosition)
            if random.random() < 0.15:
                data.doors_open = [random.choice(all_doors)]
            else:
                data.doors_open = []

        data.parking_brake = data.speed_kmh < 1.0
        data.headlights_on = random.random() < 0.5
