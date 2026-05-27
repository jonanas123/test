"""
HAL - Abstração do módulo Wi-Fi.

Define a interface para gerenciamento de conexões Wi-Fi
e fornece uma implementação mock.
"""

import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class WiFiState(Enum):
    OFF = "Desligado"
    SCANNING = "Procurando redes"
    CONNECTING = "Conectando"
    CONNECTED = "Conectado"
    ERROR = "Erro"


@dataclass
class WiFiNetwork:
    """Representa uma rede Wi-Fi detectada."""
    ssid: str
    signal_strength: int  # 0-100%
    secured: bool = True


class WiFiInterface(ABC):
    """Interface abstrata para o módulo Wi-Fi."""

    @abstractmethod
    def initialize(self) -> bool:
        """Inicializa o módulo Wi-Fi."""

    @abstractmethod
    def get_state(self) -> WiFiState:
        """Retorna o estado atual do Wi-Fi."""

    @abstractmethod
    def scan_networks(self) -> list[WiFiNetwork]:
        """Busca redes Wi-Fi disponíveis."""

    @abstractmethod
    def connect(self, ssid: str, password: str) -> bool:
        """Conecta a uma rede Wi-Fi."""

    @abstractmethod
    def disconnect(self) -> None:
        """Desconecta da rede atual."""

    @abstractmethod
    def get_connected_network(self) -> WiFiNetwork | None:
        """Retorna a rede conectada ou None."""

    @abstractmethod
    def shutdown(self) -> None:
        """Desliga o módulo Wi-Fi."""


class MockWiFi(WiFiInterface):
    """Implementação mock do módulo Wi-Fi."""

    MOCK_NETWORKS = [
        WiFiNetwork("Casa_5G", random.randint(60, 95), True),
        WiFiNetwork("Vizinho_Net", random.randint(20, 50), True),
        WiFiNetwork("Cafe_Free", random.randint(30, 70), False),
        WiFiNetwork("Oficina_WiFi", random.randint(40, 80), True),
    ]

    def __init__(self) -> None:
        self._state = WiFiState.OFF
        self._connected_network: WiFiNetwork | None = None

    def initialize(self) -> bool:
        logger.info("[WIFI] Inicializando módulo Wi-Fi (mock)...")
        self._state = WiFiState.SCANNING
        logger.info("[WIFI] Módulo Wi-Fi inicializado.")
        return True

    def get_state(self) -> WiFiState:
        return self._state

    def scan_networks(self) -> list[WiFiNetwork]:
        if self._state == WiFiState.OFF:
            logger.warning("[WIFI] Wi-Fi desligado, não é possível escanear.")
            return []

        self._state = WiFiState.SCANNING
        for net in self.MOCK_NETWORKS:
            net.signal_strength = random.randint(20, 95)

        count = random.randint(2, len(self.MOCK_NETWORKS))
        networks = random.sample(self.MOCK_NETWORKS, count)
        networks.sort(key=lambda n: n.signal_strength, reverse=True)

        logger.info("[WIFI] Escaneamento concluído: %d redes encontradas.", count)
        return networks

    def connect(self, ssid: str, password: str) -> bool:
        network = next(
            (n for n in self.MOCK_NETWORKS if n.ssid == ssid), None
        )
        if network is None:
            logger.error("[WIFI] Rede '%s' não encontrada.", ssid)
            self._state = WiFiState.ERROR
            return False

        self._state = WiFiState.CONNECTING
        logger.info("[WIFI] Conectando à rede '%s'...", ssid)

        self._connected_network = network
        self._state = WiFiState.CONNECTED
        logger.info("[WIFI] Conectado à rede '%s' (sinal: %d%%).", ssid, network.signal_strength)
        return True

    def disconnect(self) -> None:
        if self._connected_network:
            logger.info("[WIFI] Desconectando de '%s'...", self._connected_network.ssid)
            self._connected_network = None
        self._state = WiFiState.SCANNING

    def get_connected_network(self) -> WiFiNetwork | None:
        return self._connected_network

    def shutdown(self) -> None:
        self.disconnect()
        self._state = WiFiState.OFF
        logger.info("[WIFI] Módulo Wi-Fi desligado.")
