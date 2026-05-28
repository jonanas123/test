"""Testes unitários para o módulo de Boot."""

from src.hal.audio_hal import MockAudio
from src.hal.bluetooth_hal import MockBluetooth
from src.hal.can_bus import MockCANBus
from src.hal.hvac_hal import MockHVAC
from src.hal.wifi_hal import MockWiFi
from src.middleware.boot_manager import BootManager, SubsystemStatus


def _create_boot_manager() -> BootManager:
    return BootManager(
        MockCANBus(), MockBluetooth(), MockAudio(), MockHVAC(), MockWiFi(),
    )


class TestBootManager:
    def test_welcome_art_not_empty(self) -> None:
        boot = _create_boot_manager()
        art = boot.show_welcome()
        assert len(art) > 0
        assert "CENTRAL MULTIMÍDIA" in art

    def test_boot_sequence_all_ok(self) -> None:
        boot = _create_boot_manager()
        report = boot.run_boot_sequence()
        assert report.all_ok is True
        assert len(report.subsystems) == 5
        assert all(
            s == SubsystemStatus.OK for s in report.subsystems.values()
        )

    def test_boot_time_recorded(self) -> None:
        boot = _create_boot_manager()
        report = boot.run_boot_sequence()
        assert report.boot_time_seconds >= 0
