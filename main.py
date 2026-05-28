#!/usr/bin/env python3
"""
Central Multimídia Automotiva - Ponto de Entrada.

Este módulo inicializa todas as camadas do sistema (HAL, Middleware, HMI)
e executa o loop principal da interface interativa no terminal.
"""

import logging
import sys
import time

# --- HAL (Camada de Abstração de Hardware) ---
from src.hal.audio_hal import MockAudio
from src.hal.bluetooth_hal import MockBluetooth
from src.hal.can_bus import MockCANBus
from src.hal.hvac_hal import MockHVAC
from src.hal.wifi_hal import MockWiFi

# --- Middleware (Camada de Lógica de Negócios) ---
from src.middleware.boot_manager import BootManager
from src.middleware.connectivity_manager import ConnectivityManager
from src.middleware.hvac_manager import HVACManager
from src.middleware.media_manager import MediaManager
from src.middleware.vehicle_manager import VehicleManager

# --- HMI (Camada de Interface) ---
from src.hmi.display import (
    C,
    clear_screen,
    render_alerts,
    render_boot_progress,
    render_connectivity_menu,
    render_connectivity_panel,
    render_device_list,
    render_header,
    render_hvac_menu,
    render_hvac_panel,
    render_main_menu,
    render_media_menu,
    render_media_panel,
    render_vehicle_menu,
    render_vehicle_panel,
)
from src.hmi.input_handler import InputHandler

# Configuração de logging — somente arquivo (sem poluir o terminal)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("infotainment.log")],
)
logger = logging.getLogger(__name__)


class InfotainmentSystem:
    """Classe principal que orquestra todos os módulos do sistema."""

    def __init__(self) -> None:
        # Instanciar HAL (mocks)
        self._can_hal = MockCANBus()
        self._bt_hal = MockBluetooth()
        self._audio_hal = MockAudio()
        self._hvac_hal = MockHVAC()
        self._wifi_hal = MockWiFi()

        # Instanciar Middleware (injeção de dependência)
        self._boot = BootManager(
            self._can_hal, self._bt_hal, self._audio_hal,
            self._hvac_hal, self._wifi_hal,
        )
        self._connectivity = ConnectivityManager(self._bt_hal, self._wifi_hal)
        self._media = MediaManager(self._audio_hal)
        self._hvac = HVACManager(self._hvac_hal)
        self._vehicle = VehicleManager(self._can_hal)

        # HMI
        self._input = InputHandler()
        self._running = False

    # ── Boot ─────────────────────────────────────────────────

    def boot(self) -> bool:
        """Executa a sequência de inicialização do sistema."""
        clear_screen()

        # Logo animada
        boot_art = (
            f"\n"
            f"  {C.BRIGHT_CYAN}{C.BOLD}"
            f"     ╔══════════════════════════════════════════╗\n"
            f"  {C.BRIGHT_CYAN}"
            f"     ║    CENTRAL MULTIMÍDIA AUTOMOTIVA        ║\n"
            f"  {C.CYAN}"
            f"     ║           Infotainment v1.0             ║\n"
            f"  {C.CYAN}"
            f"     ╚══════════════════════════════════════════╝{C.RESET}\n"
        )
        print(boot_art)
        time.sleep(0.8)

        print(f"  {C.DIM}{'─' * 50}{C.RESET}")
        print(f"  {C.BRIGHT_WHITE}{C.BOLD} Inicializando subsistemas...{C.RESET}\n")
        report = self._boot.run_boot_sequence()

        for name, status in report.subsystems.items():
            line = render_boot_progress(name, status.value)
            print(line)
            time.sleep(0.3)

        print(f"\n  {C.DIM}{'─' * 50}{C.RESET}")
        print(f"  {C.BRIGHT_GREEN}✓ Boot completo em {report.boot_time_seconds:.3f}s{C.RESET}")

        if not report.all_ok:
            print(f"\n  {C.BRIGHT_YELLOW}⚠ Alguns subsistemas falharam.{C.RESET}")

        print(f"\n  {C.DIM}Pressione ENTER para continuar...{C.RESET}")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass

        return report.all_ok

    # ── Loop Principal ───────────────────────────────────────

    def run(self) -> None:
        """Loop principal da central multimídia."""
        if not self.boot():
            logger.warning("Boot incompleto, continuando com funcionalidade parcial.")

        self._running = True
        logger.info("Sistema de infotainment iniciado.")

        while self._running:
            try:
                self._render_main_screen()
                choice = self._input.get_menu_choice(
                    valid={"0", "1", "2", "3", "4", "5"},
                )
                self._handle_main_menu(choice)
            except KeyboardInterrupt:
                self._shutdown()

    def _render_main_screen(self) -> None:
        """Renderiza a tela principal com todos os painéis."""
        clear_screen()

        vehicle_status = self._vehicle.read_data()
        media_status = self._media.get_status()
        hvac_status = self._hvac.get_status()
        conn_status = self._connectivity.get_status()

        print(render_header())
        print(render_vehicle_panel(vehicle_status))
        print(render_media_panel(media_status))
        print(render_hvac_panel(hvac_status))
        print(render_connectivity_panel(conn_status))

        alerts_text = render_alerts(vehicle_status.alerts)
        if alerts_text:
            print(alerts_text)

        print(render_main_menu())

    def _handle_main_menu(self, choice: str) -> None:
        """Roteia a escolha do menu principal."""
        handlers = {
            "1": self._media_submenu,
            "2": self._hvac_submenu,
            "3": self._connectivity_submenu,
            "4": self._vehicle_submenu,
            "5": lambda: None,  # Atualizar tela (re-render)
            "0": self._shutdown,
        }
        handler = handlers.get(choice)
        if handler:
            handler()

    # ── Submenu Mídia ────────────────────────────────────────

    def _media_submenu(self) -> None:
        """Submenu de controle de mídia."""
        while True:
            clear_screen()
            print(render_header())
            print(render_media_panel(self._media.get_status()))
            print(render_media_menu())

            choice = self._input.get_menu_choice(
                valid={"0", "1", "2", "3", "4", "5", "6", "7"},
            )

            if choice == "0":
                return
            elif choice == "1":
                status = self._media.get_status()
                if status.state.name == "PLAYING":
                    self._media.pause()
                else:
                    self._media.play()
            elif choice == "2":
                self._media.stop()
            elif choice == "3":
                self._media.next_track()
            elif choice == "4":
                self._media.previous_track()
            elif choice == "5":
                self._media.volume_up()
            elif choice == "6":
                self._media.volume_down()
            elif choice == "7":
                self._media.toggle_mute()

    # ── Submenu Climatização ─────────────────────────────────

    def _hvac_submenu(self) -> None:
        """Submenu de controle de climatização."""
        while True:
            clear_screen()
            print(render_header())
            print(render_hvac_panel(self._hvac.get_status()))
            print(render_hvac_menu())

            choice = self._input.get_menu_choice(
                valid={"0", "1", "2", "3", "4", "5", "6"},
            )

            if choice == "0":
                return
            elif choice == "1":
                self._hvac.increase_temperature()
            elif choice == "2":
                self._hvac.decrease_temperature()
            elif choice == "3":
                self._hvac.increase_fan()
            elif choice == "4":
                self._hvac.decrease_fan()
            elif choice == "5":
                self._hvac.toggle_ac()
            elif choice == "6":
                self._hvac.toggle_power()

    # ── Submenu Conectividade ────────────────────────────────

    def _connectivity_submenu(self) -> None:
        """Submenu de conectividade Bluetooth e Wi-Fi."""
        while True:
            clear_screen()
            print(render_header())
            print(render_connectivity_panel(self._connectivity.get_status()))
            print(render_connectivity_menu())

            choice = self._input.get_menu_choice(
                valid={"0", "1", "2", "3", "4", "5", "6"},
            )

            if choice == "0":
                return
            elif choice == "1":
                self._scan_bluetooth()
            elif choice == "2":
                self._pair_bluetooth()
            elif choice == "3":
                self._connectivity.disconnect_bluetooth()
                print(f"  {C.BRIGHT_GREEN}✓ Bluetooth desconectado.{C.RESET}")
                time.sleep(1)
            elif choice == "4":
                self._scan_wifi()
            elif choice == "5":
                self._connect_wifi()
            elif choice == "6":
                self._connectivity.disconnect_wifi()
                print(f"  {C.BRIGHT_GREEN}✓ Wi-Fi desconectado.{C.RESET}")
                time.sleep(1)

    def _scan_bluetooth(self) -> None:
        """Executa escaneamento Bluetooth e exibe resultados."""
        print(f"\n  {C.BRIGHT_CYAN}Escaneando dispositivos Bluetooth...{C.RESET}")
        devices = self._connectivity.scan_bluetooth()
        device_list = [
            {"name": d.name, "detail": d.address}
            for d in devices
        ]
        print(render_device_list(device_list, "DISPOSITIVOS BLUETOOTH"))
        input("\n  Pressione ENTER para continuar...")

    def _pair_bluetooth(self) -> None:
        """Fluxo de pareamento Bluetooth."""
        print(f"\n  {C.BRIGHT_CYAN}Escaneando dispositivos...{C.RESET}")
        devices = self._connectivity.scan_bluetooth()

        if not devices:
            print(f"  {C.DIM}Nenhum dispositivo encontrado.{C.RESET}")
            time.sleep(1)
            return

        device_list = [
            {"name": d.name, "detail": d.address}
            for d in devices
        ]
        print(render_device_list(device_list, "SELECIONE UM DISPOSITIVO"))

        idx = self._input.get_numeric_input("Número do dispositivo: ")
        if idx is None or idx == 0 or idx > len(devices):
            return

        device = devices[idx - 1]
        print(f"\n  {C.BRIGHT_CYAN}Pareando com '{device.name}'...{C.RESET}")
        success = self._connectivity.pair_bluetooth(device.address)

        if success:
            print(f"  {C.BRIGHT_GREEN}✓ Conectado com '{device.name}'!{C.RESET}")
        else:
            print(f"  {C.BRIGHT_RED}✗ Falha ao parear com '{device.name}'.{C.RESET}")
        time.sleep(1.5)

    def _scan_wifi(self) -> None:
        """Executa escaneamento Wi-Fi e exibe resultados."""
        print(f"\n  {C.BRIGHT_CYAN}Escaneando redes Wi-Fi...{C.RESET}")
        networks = self._connectivity.scan_wifi()
        net_list = [
            {"name": n.ssid, "detail": f"Sinal: {n.signal_strength}% {'🔒' if n.secured else '🔓'}"}
            for n in networks
        ]
        print(render_device_list(net_list, "REDES WI-FI DISPONÍVEIS"))
        input("\n  Pressione ENTER para continuar...")

    def _connect_wifi(self) -> None:
        """Fluxo de conexão Wi-Fi."""
        print(f"\n  {C.BRIGHT_CYAN}Escaneando redes...{C.RESET}")
        networks = self._connectivity.scan_wifi()

        if not networks:
            print(f"  {C.DIM}Nenhuma rede encontrada.{C.RESET}")
            time.sleep(1)
            return

        net_list = [
            {"name": n.ssid, "detail": f"Sinal: {n.signal_strength}% {'🔒' if n.secured else '🔓'}"}
            for n in networks
        ]
        print(render_device_list(net_list, "SELECIONE UMA REDE"))

        idx = self._input.get_numeric_input("Número da rede: ")
        if idx is None or idx == 0 or idx > len(networks):
            return

        network = networks[idx - 1]
        password = ""
        if network.secured:
            password = self._input.get_text_input("Senha: ")

        print(f"\n  {C.BRIGHT_CYAN}Conectando à rede '{network.ssid}'...{C.RESET}")
        success = self._connectivity.connect_wifi(network.ssid, password)

        if success:
            print(f"  {C.BRIGHT_GREEN}✓ Conectado à rede '{network.ssid}'!{C.RESET}")
        else:
            print(f"  {C.BRIGHT_RED}✗ Falha ao conectar à rede '{network.ssid}'.{C.RESET}")
        time.sleep(1.5)

    # ── Submenu Veículo ──────────────────────────────────────

    def _vehicle_submenu(self) -> None:
        """Submenu de dados veiculares."""
        while True:
            clear_screen()
            print(render_header())

            vehicle_status = self._vehicle.read_data()
            print(render_vehicle_panel(vehicle_status))

            alerts_text = render_alerts(vehicle_status.alerts)
            if alerts_text:
                print(alerts_text)

            print(render_vehicle_menu())

            choice = self._input.get_menu_choice(valid={"0", "1"})
            if choice == "0":
                return

    # ── Shutdown ─────────────────────────────────────────────

    def _shutdown(self) -> None:
        """Desliga o sistema de forma segura."""
        clear_screen()
        print(f"\n  {C.BRIGHT_YELLOW}{C.BOLD}Desligando a Central Multimídia...{C.RESET}\n")

        subsystems = [
            ("Mídia", self._media.stop),
            ("HVAC", self._hvac_hal.shutdown),
            ("Bluetooth", self._bt_hal.shutdown),
            ("Wi-Fi", self._wifi_hal.shutdown),
            ("CAN Bus", self._can_hal.shutdown),
            ("Áudio", self._audio_hal.shutdown),
        ]

        for name, shutdown_fn in subsystems:
            print(f"  {C.DIM}[...]{C.RESET} Desligando {C.WHITE}{name}{C.RESET}...")
            shutdown_fn()
            time.sleep(0.2)
            # Re-print com check
            print(f"\033[1A  {C.BRIGHT_GREEN}[✓]{C.RESET}   Desligado  {C.WHITE}{name}{C.RESET}   ")

        print(f"\n  {C.CYAN}╔══════════════════════════════════════════════════════════╗{C.RESET}")
        print(f"  {C.CYAN}║{C.BRIGHT_WHITE}{C.BOLD}         SISTEMA DESLIGADO COM SEGURANÇA              {C.RESET}{C.CYAN}║{C.RESET}")
        print(f"  {C.CYAN}║{C.DIM}              Até a próxima viagem!                    {C.RESET}{C.CYAN}║{C.RESET}")
        print(f"  {C.CYAN}╚══════════════════════════════════════════════════════════╝{C.RESET}\n")

        self._running = False
        logger.info("Sistema de infotainment desligado.")


def main() -> None:
    """Ponto de entrada da aplicação."""
    system = InfotainmentSystem()
    try:
        system.run()
    except Exception:
        logger.exception("Erro fatal no sistema de infotainment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
