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

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("infotainment.log"), logging.StreamHandler(sys.stderr)],
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
        print(self._boot.show_welcome())
        time.sleep(1)

        print("\n  Inicializando subsistemas...\n")
        report = self._boot.run_boot_sequence()

        for name, status in report.subsystems.items():
            line = render_boot_progress(name, status.value)
            print(line)
            time.sleep(0.3)

        print(f"\n  Tempo de boot: {report.boot_time_seconds:.3f}s")

        if not report.all_ok:
            print("\n  ⚠ Alguns subsistemas falharam. O sistema pode não funcionar corretamente.")

        print("\n  Pressione ENTER para continuar...")
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
                print("  Bluetooth desconectado.")
                time.sleep(1)
            elif choice == "4":
                self._scan_wifi()
            elif choice == "5":
                self._connect_wifi()
            elif choice == "6":
                self._connectivity.disconnect_wifi()
                print("  Wi-Fi desconectado.")
                time.sleep(1)

    def _scan_bluetooth(self) -> None:
        """Executa escaneamento Bluetooth e exibe resultados."""
        print("\n  Escaneando dispositivos Bluetooth...")
        devices = self._connectivity.scan_bluetooth()
        device_list = [
            {"name": d.name, "detail": d.address}
            for d in devices
        ]
        print(render_device_list(device_list, "DISPOSITIVOS BLUETOOTH"))
        input("\n  Pressione ENTER para continuar...")

    def _pair_bluetooth(self) -> None:
        """Fluxo de pareamento Bluetooth."""
        print("\n  Escaneando dispositivos...")
        devices = self._connectivity.scan_bluetooth()

        if not devices:
            print("  Nenhum dispositivo encontrado.")
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
        print(f"\n  Pareando com '{device.name}'...")
        success = self._connectivity.pair_bluetooth(device.address)

        if success:
            print(f"  ✓ Conectado com '{device.name}'!")
        else:
            print(f"  ✗ Falha ao parear com '{device.name}'.")
        time.sleep(1.5)

    def _scan_wifi(self) -> None:
        """Executa escaneamento Wi-Fi e exibe resultados."""
        print("\n  Escaneando redes Wi-Fi...")
        networks = self._connectivity.scan_wifi()
        net_list = [
            {"name": n.ssid, "detail": f"Sinal: {n.signal_strength}% {'🔒' if n.secured else '🔓'}"}
            for n in networks
        ]
        print(render_device_list(net_list, "REDES WI-FI DISPONÍVEIS"))
        input("\n  Pressione ENTER para continuar...")

    def _connect_wifi(self) -> None:
        """Fluxo de conexão Wi-Fi."""
        print("\n  Escaneando redes...")
        networks = self._connectivity.scan_wifi()

        if not networks:
            print("  Nenhuma rede encontrada.")
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

        print(f"\n  Conectando à rede '{network.ssid}'...")
        success = self._connectivity.connect_wifi(network.ssid, password)

        if success:
            print(f"  ✓ Conectado à rede '{network.ssid}'!")
        else:
            print(f"  ✗ Falha ao conectar à rede '{network.ssid}'.")
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
        print("\n  Desligando a Central Multimídia...")

        subsystems = [
            ("Mídia", self._media.stop),
            ("HVAC", self._hvac_hal.shutdown),
            ("Bluetooth", self._bt_hal.shutdown),
            ("Wi-Fi", self._wifi_hal.shutdown),
            ("CAN Bus", self._can_hal.shutdown),
            ("Áudio", self._audio_hal.shutdown),
        ]

        for name, shutdown_fn in subsystems:
            print(f"  Desligando {name}...")
            shutdown_fn()
            time.sleep(0.2)

        print("\n  ╔══════════════════════════════════════════════════════════╗")
        print("  ║           SISTEMA DESLIGADO COM SEGURANÇA               ║")
        print("  ║               Até a próxima viagem!                     ║")
        print("  ╚══════════════════════════════════════════════════════════╝\n")

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
