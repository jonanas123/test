"""
Middleware - Gerenciador de Inicialização (Boot).

Responsável pela sequência de boot do sistema, verificação de
subsistemas e exibição da tela de boas-vindas.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SubsystemStatus(Enum):
    PENDING = "Pendente"
    OK = "OK"
    FAILED = "Falha"


@dataclass
class BootReport:
    """Relatório de inicialização do sistema."""
    subsystems: dict[str, SubsystemStatus] = field(default_factory=dict)
    boot_time_seconds: float = 0.0
    all_ok: bool = False


class BootManager:
    """Gerencia a sequência de inicialização do sistema."""

    WELCOME_ART = r"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        ██╗███╗   ██╗███████╗ ██████╗                     ║
    ║        ██║████╗  ██║██╔════╝██╔═══██╗                    ║
    ║        ██║██╔██╗ ██║█████╗  ██║   ██║                    ║
    ║        ██║██║╚██╗██║██╔══╝  ██║   ██║                    ║
    ║        ██║██║ ╚████║██║     ╚██████╔╝                    ║
    ║        ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝                    ║
    ║                                                          ║
    ║        CENTRAL MULTIMÍDIA AUTOMOTIVA v1.0                ║
    ║        Automotive Infotainment System                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """

    def __init__(
        self,
        can_bus_hal: "CANBusInterface",
        bluetooth_hal: "BluetoothInterface",
        audio_hal: "AudioInterface",
        hvac_hal: "HVACInterface",
        wifi_hal: "WiFiInterface",
    ) -> None:
        self._can = can_bus_hal
        self._bt = bluetooth_hal
        self._audio = audio_hal
        self._hvac = hvac_hal
        self._wifi = wifi_hal
        self._boot_report = BootReport()

    def show_welcome(self) -> str:
        """Retorna a arte ASCII de boas-vindas."""
        logger.info("[BOOT] Exibindo tela de boas-vindas.")
        return self.WELCOME_ART

    def run_boot_sequence(self) -> BootReport:
        """Executa a sequência completa de inicialização."""
        start = time.monotonic()
        logger.info("[BOOT] Iniciando sequência de boot...")

        subsystems: list[tuple[str, object]] = [
            ("CAN Bus", self._can),
            ("Bluetooth", self._bt),
            ("Áudio", self._audio),
            ("HVAC", self._hvac),
            ("Wi-Fi", self._wifi),
        ]

        for name, hal in subsystems:
            status = self._initialize_subsystem(name, hal)
            self._boot_report.subsystems[name] = status

        elapsed = time.monotonic() - start
        self._boot_report.boot_time_seconds = round(elapsed, 3)
        self._boot_report.all_ok = all(
            s == SubsystemStatus.OK
            for s in self._boot_report.subsystems.values()
        )

        if self._boot_report.all_ok:
            logger.info(
                "[BOOT] Inicialização concluída com sucesso em %.3fs.",
                elapsed,
            )
        else:
            failed = [
                name for name, s in self._boot_report.subsystems.items()
                if s == SubsystemStatus.FAILED
            ]
            logger.warning(
                "[BOOT] Inicialização concluída com falhas: %s",
                ", ".join(failed),
            )

        return self._boot_report

    def get_boot_report(self) -> BootReport:
        """Retorna o relatório de boot mais recente."""
        return self._boot_report

    @staticmethod
    def _initialize_subsystem(name: str, hal: object) -> SubsystemStatus:
        """Inicializa um subsistema individual."""
        logger.info("[BOOT] Verificando subsistema: %s...", name)
        try:
            if hasattr(hal, "initialize"):
                result = hal.initialize()  # type: ignore[union-attr]
                if result:
                    logger.info("[BOOT] %s: OK", name)
                    return SubsystemStatus.OK
                logger.error("[BOOT] %s: inicialização retornou falha.", name)
                return SubsystemStatus.FAILED
            logger.warning("[BOOT] %s: sem método initialize().", name)
            return SubsystemStatus.FAILED
        except Exception:
            logger.exception("[BOOT] %s: exceção durante inicialização.", name)
            return SubsystemStatus.FAILED
