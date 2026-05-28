"""Testes unitários para o módulo de Climatização (HVAC)."""

from src.hal.hvac_hal import MAX_TEMP_CELSIUS, MIN_TEMP_CELSIUS, MockHVAC
from src.middleware.hvac_manager import HVACManager


def _create_hvac_manager() -> HVACManager:
    hvac = MockHVAC()
    hvac.initialize()
    return HVACManager(hvac)


class TestHVACManager:
    def test_initial_state_powered_on(self) -> None:
        mgr = _create_hvac_manager()
        status = mgr.get_status()
        assert status.power_on is True

    def test_increase_temperature(self) -> None:
        mgr = _create_hvac_manager()
        initial = mgr.get_status().target_temp
        new_temp = mgr.increase_temperature()
        assert new_temp == initial + 0.5

    def test_decrease_temperature(self) -> None:
        mgr = _create_hvac_manager()
        initial = mgr.get_status().target_temp
        new_temp = mgr.decrease_temperature()
        assert new_temp == initial - 0.5

    def test_temperature_max_clamp(self) -> None:
        mgr = _create_hvac_manager()
        mgr.set_temperature(MAX_TEMP_CELSIUS)
        result = mgr.increase_temperature()
        assert result == MAX_TEMP_CELSIUS

    def test_temperature_min_clamp(self) -> None:
        mgr = _create_hvac_manager()
        mgr.set_temperature(MIN_TEMP_CELSIUS)
        result = mgr.decrease_temperature()
        assert result == MIN_TEMP_CELSIUS

    def test_increase_fan(self) -> None:
        mgr = _create_hvac_manager()
        initial = mgr.get_status().fan_speed
        new_speed = mgr.increase_fan()
        assert new_speed == initial + 1

    def test_decrease_fan(self) -> None:
        mgr = _create_hvac_manager()
        initial = mgr.get_status().fan_speed
        new_speed = mgr.decrease_fan()
        assert new_speed == initial - 1

    def test_toggle_ac(self) -> None:
        mgr = _create_hvac_manager()
        initial = mgr.get_status().ac_on
        mgr.toggle_ac()
        assert mgr.get_status().ac_on != initial

    def test_toggle_power(self) -> None:
        mgr = _create_hvac_manager()
        initial = mgr.get_status().power_on
        mgr.toggle_power()
        assert mgr.get_status().power_on != initial
