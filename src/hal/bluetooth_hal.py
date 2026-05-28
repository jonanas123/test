"""
HAL - Abstração do módulo Bluetooth.

Define a interface para gerenciamento de conexões Bluetooth
e fornece uma implementação mock.
"""

import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BluetoothState(Enum):
    OFF = "Desligado"
    DISCOVERING = "Procurando dispositivos"
    PAIRING = "Pareando"
    CONNECTED = "Conectado"
    ERROR = "Erro"


@dataclass
class BluetoothDevice:
    """Representa um dispositivo Bluetooth detectado ou pareado."""
    name: str
    address: str
    paired: bool = False
    connected: bool = False


class BluetoothInterface(ABC):
    """Interface abstrata para o módulo Bluetooth."""

    @abstractmethod
    def initialize(self) -> bool:
        """Inicializa o módulo Bluetooth."""

    @abstractmethod
    def get_state(self) -> BluetoothState:
        """Retorna o estado atual do Bluetooth."""

    @abstractmethod
    def scan_devices(self) -> list[BluetoothDevice]:
        """Busca dispositivos Bluetooth próximos."""

    @abstractmethod
    def pair_device(self, address: str) -> bool:
        """Pareia com um dispositivo Bluetooth."""

    @abstractmethod
    def disconnect(self) -> None:
        """Desconecta o dispositivo atual."""

    @abstractmethod
    def shutdown(self) -> None:
        """Desliga o módulo Bluetooth."""


class MockBluetooth(BluetoothInterface):
    """Implementação mock do módulo Bluetooth."""

    MOCK_DEVICES = [
        BluetoothDevice("iPhone de João", "AA:BB:CC:DD:EE:01"),
        BluetoothDevice("Galaxy S24", "AA:BB:CC:DD:EE:02"),
        BluetoothDevice("Fone JBL Tune", "AA:BB:CC:DD:EE:03"),
        BluetoothDevice("AirPods Pro", "AA:BB:CC:DD:EE:04"),
    ]

    def __init__(self) -> None:
        self._state = BluetoothState.OFF
        self._paired_device: BluetoothDevice | None = None

    def initialize(self) -> bool:
        logger.info("[BT] Inicializando módulo Bluetooth (mock)...")
        self._state = BluetoothState.DISCOVERING
        logger.info("[BT] Módulo Bluetooth inicializado.")
        return True

    def get_state(self) -> BluetoothState:
        return self._state

    def scan_devices(self) -> list[BluetoothDevice]:
        if self._state == BluetoothState.OFF:
            logger.warning("[BT] Bluetooth desligado, não é possível escanear.")
            return []

        self._state = BluetoothState.DISCOVERING
        count = random.randint(2, len(self.MOCK_DEVICES))
        devices = random.sample(self.MOCK_DEVICES, count)

        logger.info("[BT] Escaneamento concluído: %d dispositivos encontrados.", count)
        return devices

    def pair_device(self, address: str) -> bool:
        device = next(
            (d for d in self.MOCK_DEVICES if d.address == address), None
        )
        if device is None:
            logger.error("[BT] Dispositivo %s não encontrado.", address)
            self._state = BluetoothState.ERROR
            return False

        self._state = BluetoothState.PAIRING
        logger.info("[BT] Pareando com '%s' (%s)...", device.name, address)

        device.paired = True
        device.connected = True
        self._paired_device = device
        self._state = BluetoothState.CONNECTED

        logger.info("[BT] Pareado e conectado com '%s'.", device.name)
        return True

    def disconnect(self) -> None:
        if self._paired_device:
            logger.info("[BT] Desconectando '%s'...", self._paired_device.name)
            self._paired_device.connected = False
            self._paired_device = None
        self._state = BluetoothState.DISCOVERING

    def shutdown(self) -> None:
        self.disconnect()
        self._state = BluetoothState.OFF
        logger.info("[BT] Módulo Bluetooth desligado.")
