"""
Middleware - Gerenciador de Conectividade.

Gerencia os módulos Bluetooth e Wi-Fi, oferecendo uma interface
unificada para pareamento, conexão e monitoramento de status.
"""

import logging
from dataclasses import dataclass

from src.hal.bluetooth_hal import BluetoothDevice, BluetoothInterface, BluetoothState
from src.hal.wifi_hal import WiFiInterface, WiFiNetwork, WiFiState

logger = logging.getLogger(__name__)


@dataclass
class ConnectivityStatus:
    """Status consolidado de conectividade."""
    bluetooth_state: BluetoothState = BluetoothState.OFF
    bluetooth_device: BluetoothDevice | None = None
    wifi_state: WiFiState = WiFiState.OFF
    wifi_network: WiFiNetwork | None = None


class ConnectivityManager:
    """Gerencia Bluetooth e Wi-Fi de forma unificada."""

    def __init__(
        self,
        bluetooth_hal: BluetoothInterface,
        wifi_hal: WiFiInterface,
    ) -> None:
        self._bt = bluetooth_hal
        self._wifi = wifi_hal
        self._bt_paired_device: BluetoothDevice | None = None

    def get_status(self) -> ConnectivityStatus:
        """Retorna o status consolidado de conectividade."""
        return ConnectivityStatus(
            bluetooth_state=self._bt.get_state(),
            bluetooth_device=self._bt_paired_device,
            wifi_state=self._wifi.get_state(),
            wifi_network=self._wifi.get_connected_network(),
        )

    # --- Bluetooth ---

    def scan_bluetooth(self) -> list[BluetoothDevice]:
        """Busca dispositivos Bluetooth próximos."""
        logger.info("[CONN] Iniciando escaneamento Bluetooth...")
        return self._bt.scan_devices()

    def pair_bluetooth(self, address: str) -> bool:
        """Pareia com um dispositivo Bluetooth."""
        logger.info("[CONN] Solicitando pareamento BT com %s...", address)
        success = self._bt.pair_device(address)
        if success:
            devices = self._bt.scan_devices()
            self._bt_paired_device = next(
                (d for d in devices if d.address == address), None
            )
        return success

    def disconnect_bluetooth(self) -> None:
        """Desconecta o Bluetooth."""
        logger.info("[CONN] Desconectando Bluetooth...")
        self._bt.disconnect()
        self._bt_paired_device = None

    # --- Wi-Fi ---

    def scan_wifi(self) -> list[WiFiNetwork]:
        """Busca redes Wi-Fi disponíveis."""
        logger.info("[CONN] Iniciando escaneamento Wi-Fi...")
        return self._wifi.scan_networks()

    def connect_wifi(self, ssid: str, password: str = "") -> bool:
        """Conecta a uma rede Wi-Fi."""
        logger.info("[CONN] Conectando ao Wi-Fi '%s'...", ssid)
        return self._wifi.connect(ssid, password)

    def disconnect_wifi(self) -> None:
        """Desconecta do Wi-Fi."""
        logger.info("[CONN] Desconectando Wi-Fi...")
        self._wifi.disconnect()
