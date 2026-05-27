"""Testes unitários para o módulo de Integração Veicular."""

from src.hal.can_bus import MockCANBus
from src.middleware.vehicle_manager import VehicleManager


def _create_vehicle_manager() -> VehicleManager:
    can = MockCANBus()
    can.initialize()
    return VehicleManager(can)


class TestVehicleManager:
    def test_read_data_returns_status(self) -> None:
        mgr = _create_vehicle_manager()
        status = mgr.read_data()
        assert status.speed_kmh >= 0
        assert status.fuel_level_percent >= 0
        assert status.engine_temp_celsius > 0

    def test_fuel_bar_renders(self) -> None:
        mgr = _create_vehicle_manager()
        status = mgr.read_data()
        bar = status.fuel_bar
        assert len(bar) == 10
        assert "█" in bar or "░" in bar

    def test_speed_display_format(self) -> None:
        mgr = _create_vehicle_manager()
        status = mgr.read_data()
        assert "km/h" in status.speed_display

    def test_multiple_reads_return_valid_data(self) -> None:
        mgr = _create_vehicle_manager()
        readings = [mgr.read_data() for _ in range(5)]
        for status in readings:
            assert status.speed_kmh >= 0
            assert status.rpm >= 0
            assert 0 <= status.fuel_level_percent <= 100
            assert status.engine_temp_celsius > 0

    def test_alerts_list_type(self) -> None:
        mgr = _create_vehicle_manager()
        status = mgr.read_data()
        assert isinstance(status.alerts, list)
