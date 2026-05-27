"""Testes unitários para o módulo de Conectividade."""

from src.hal.bluetooth_hal import BluetoothState, MockBluetooth
from src.hal.wifi_hal import MockWiFi, WiFiState
from src.middleware.connectivity_manager import ConnectivityManager


def _create_connectivity_manager() -> ConnectivityManager:
    bt = MockBluetooth()
    wifi = MockWiFi()
    bt.initialize()
    wifi.initialize()
    return ConnectivityManager(bt, wifi)


class TestConnectivityManager:
    def test_initial_status(self) -> None:
        mgr = _create_connectivity_manager()
        status = mgr.get_status()
        assert status.bluetooth_state == BluetoothState.DISCOVERING
        assert status.wifi_state == WiFiState.SCANNING

    def test_scan_bluetooth_returns_devices(self) -> None:
        mgr = _create_connectivity_manager()
        devices = mgr.scan_bluetooth()
        assert len(devices) > 0

    def test_pair_bluetooth(self) -> None:
        mgr = _create_connectivity_manager()
        devices = mgr.scan_bluetooth()
        assert len(devices) > 0
        success = mgr.pair_bluetooth(devices[0].address)
        assert success is True

    def test_disconnect_bluetooth(self) -> None:
        mgr = _create_connectivity_manager()
        devices = mgr.scan_bluetooth()
        mgr.pair_bluetooth(devices[0].address)
        mgr.disconnect_bluetooth()
        status = mgr.get_status()
        assert status.bluetooth_device is None

    def test_scan_wifi_returns_networks(self) -> None:
        mgr = _create_connectivity_manager()
        networks = mgr.scan_wifi()
        assert len(networks) > 0

    def test_connect_wifi(self) -> None:
        mgr = _create_connectivity_manager()
        networks = mgr.scan_wifi()
        success = mgr.connect_wifi(networks[0].ssid)
        assert success is True
        status = mgr.get_status()
        assert status.wifi_state == WiFiState.CONNECTED

    def test_disconnect_wifi(self) -> None:
        mgr = _create_connectivity_manager()
        networks = mgr.scan_wifi()
        mgr.connect_wifi(networks[0].ssid)
        mgr.disconnect_wifi()
        status = mgr.get_status()
        assert status.wifi_network is None
