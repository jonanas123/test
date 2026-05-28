"""
HMI - Módulo de Display.

Responsável por renderizar a interface da central multimídia no terminal,
incluindo painéis de status, menus e alertas com cores ANSI.
"""

import os
from datetime import datetime

from src.hal.bluetooth_hal import BluetoothState
from src.hal.wifi_hal import WiFiState
from src.middleware.connectivity_manager import ConnectivityStatus
from src.middleware.hvac_manager import ClimateStatus
from src.middleware.media_manager import MediaStatus, PlaybackState
from src.middleware.vehicle_manager import VehicleAlert, VehicleStatus


# ── Cores ANSI ───────────────────────────────────────────────
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    BRIGHT_GREEN = "\033[92m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_WHITE = "\033[97m"


C = Color

TERMINAL_WIDTH = 64


def clear_screen() -> None:
    """Limpa o terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def _pad_visible(text: str, width: int) -> str:
    """Pad text to width based on visible (non-ANSI) length."""
    import re
    visible = re.sub(r'\033\[[0-9;]*m', '', text)
    padding = width - len(visible)
    if padding > 0:
        return text + " " * padding
    return text


def _box(title: str, lines: list[str], color: str = C.CYAN, title_color: str = C.BRIGHT_CYAN) -> str:
    """Cria uma caixa decorada com título e conteúdo colorido."""
    w = TERMINAL_WIDTH - 2
    output: list[str] = []

    output.append(f"{color}╔{'═' * w}╗{C.RESET}")

    visible_title = f" {title} "
    pad_total = w - len(visible_title)
    pad_left = pad_total // 2
    pad_right = pad_total - pad_left
    output.append(
        f"{color}║{' ' * pad_left}{title_color}{C.BOLD}{visible_title}{C.RESET}"
        f"{' ' * pad_right}{color}║{C.RESET}"
    )

    output.append(f"{color}╠{'─' * w}╣{C.RESET}")

    for line in lines:
        padded = _pad_visible(f" {line}", w - 1)
        output.append(f"{color}║{C.RESET}{padded}{color}║{C.RESET}")

    output.append(f"{color}╚{'═' * w}╝{C.RESET}")
    return "\n".join(output)


def render_header() -> str:
    """Renderiza o cabeçalho da central multimídia."""
    now = datetime.now().strftime("%H:%M:%S")
    date = datetime.now().strftime("%d/%m/%Y")

    logo = (
        f"\n"
        f"  {C.BRIGHT_CYAN}{C.BOLD}"
        f"   ╦╗╔╦╗╔═╗╔═╗   ╔═╗╔═╗╦═╗\n"
        f"  {C.BRIGHT_CYAN}"
        f"   ║║║║║╠╣ ║ ║   ║  ╠═╣╠╦╝\n"
        f"  {C.CYAN}"
        f"   ╩╝╚╩╝╚  ╚═╝   ╚═╝╩ ╩╩╚═{C.RESET}\n"
    )

    bar = _box("CENTRAL MULTIMÍDIA AUTOMOTIVA  v1.0", [
        f"  {C.DIM}Data:{C.RESET} {C.BRIGHT_WHITE}{date}{C.RESET}"
        f"            {C.DIM}Hora:{C.RESET} {C.BRIGHT_WHITE}{now}{C.RESET}",
    ], color=C.BLUE, title_color=C.BRIGHT_CYAN)

    return logo + bar


def render_vehicle_panel(status: VehicleStatus) -> str:
    """Renderiza o painel de dados do veículo."""
    doors_str = ", ".join(status.doors_open) if status.doors_open else f"{C.GREEN}Todas fechadas{C.RESET}"
    if status.doors_open:
        doors_str = f"{C.BRIGHT_YELLOW}{doors_str}{C.RESET}"

    brake_str = f"{C.BRIGHT_YELLOW}ATIVADO{C.RESET}" if status.parking_brake else f"{C.DIM}Desativado{C.RESET}"
    lights_str = f"{C.BRIGHT_GREEN}ACESOS{C.RESET}" if status.headlights_on else f"{C.DIM}Apagados{C.RESET}"

    speed_color = C.BRIGHT_RED if status.speed_kmh > 120 else C.BRIGHT_GREEN
    fuel_color = C.BRIGHT_RED if status.fuel_level_percent < 15 else C.BRIGHT_GREEN
    temp_color = C.BRIGHT_RED if status.engine_temp_celsius > 110 else C.BRIGHT_GREEN

    fuel_filled = int(status.fuel_level_percent / 10)
    fuel_bar = f"{fuel_color}{'█' * fuel_filled}{C.DIM}{'░' * (10 - fuel_filled)}{C.RESET}"

    lines = [
        f"  {C.DIM}Velocidade:{C.RESET}  {speed_color}{status.speed_kmh:>6.0f} km/h{C.RESET}"
        f"     {C.DIM}RPM:{C.RESET} {C.WHITE}{status.rpm:>5}{C.RESET}",
        f"  {C.DIM}Combustível:{C.RESET} [{fuel_bar}] {fuel_color}{status.fuel_level_percent:.1f}%{C.RESET}",
        f"  {C.DIM}Temp. Motor:{C.RESET} {temp_color}{status.engine_temp_celsius:.1f}°C{C.RESET}",
        f"  {C.DIM}Portas:{C.RESET}      {doors_str}",
        f"  {C.DIM}Freio mão:{C.RESET}   {brake_str}"
        f"     {C.DIM}Faróis:{C.RESET} {lights_str}",
    ]
    return _box("🚗  VEÍCULO", lines, color=C.GREEN, title_color=C.BRIGHT_GREEN)


def render_media_panel(status: MediaStatus) -> str:
    """Renderiza o painel do player de mídia."""
    if status.current_track:
        track = status.current_track
        title = f"{C.BRIGHT_WHITE}{track.title}{C.RESET} {C.DIM}-{C.RESET} {C.CYAN}{track.artist}{C.RESET}"
        album = f"{C.DIM}{track.album}{C.RESET}"
        minutes = track.duration_seconds // 60
        seconds = track.duration_seconds % 60
        duration = f"{minutes}:{seconds:02d}"
    else:
        title = f"{C.DIM}Nenhuma faixa selecionada{C.RESET}"
        album = ""
        duration = "--:--"

    state_map = {
        PlaybackState.PLAYING: f"{C.BRIGHT_GREEN}▶ Reproduzindo{C.RESET}",
        PlaybackState.PAUSED: f"{C.BRIGHT_YELLOW}⏸ Pausado{C.RESET}",
        PlaybackState.STOPPED: f"{C.DIM}⏹ Parado{C.RESET}",
    }

    vol_filled = int(status.volume / 30 * 20)
    vol_color = C.BRIGHT_GREEN if status.volume > 0 else C.RED
    vol_bar = f"{vol_color}{'▰' * vol_filled}{C.DIM}{'▱' * (20 - vol_filled)}{C.RESET}"
    mute_str = f" {C.BRIGHT_RED}[MUDO]{C.RESET}" if status.muted else ""

    progress_bar = f"{C.DIM}{'─' * 30}{C.RESET} {C.WHITE}[{duration}]{C.RESET}"

    lines = [
        f"  {state_map.get(status.state, '?')}",
        f"  {title}",
        f"  {album}" if album else "",
        f"  {progress_bar}",
        f"  {C.DIM}Faixa{C.RESET} {C.WHITE}{status.track_index + 1}{C.RESET}{C.DIM}/{status.playlist_size}{C.RESET}",
        f"  {C.DIM}Vol:{C.RESET} {vol_bar} {C.WHITE}{status.volume}{C.RESET}{C.DIM}/30{C.RESET}{mute_str}",
    ]
    lines = [l for l in lines if l]
    return _box("🎵  MÍDIA", lines, color=C.MAGENTA, title_color=C.BRIGHT_MAGENTA)


def render_hvac_panel(status: ClimateStatus) -> str:
    """Renderiza o painel de climatização."""
    power_color = C.BRIGHT_GREEN if status.power_on else C.RED
    power_str = f"{power_color}{'LIGADO' if status.power_on else 'DESLIGADO'}{C.RESET}"
    ac_color = C.BRIGHT_CYAN if status.ac_on else C.RED
    ac_str = f"{ac_color}{'LIGADO' if status.ac_on else 'DESLIGADO'}{C.RESET}"

    fan_bar = (
        f"{C.BRIGHT_CYAN}{'●' * status.fan_speed}{C.RESET}"
        f"{C.DIM}{'○' * (status.max_fan - status.fan_speed)}{C.RESET}"
    )

    temp_diff = abs(status.target_temp - status.current_temp)
    temp_indicator = f"{C.BRIGHT_CYAN}❄{C.RESET}" if status.target_temp < status.current_temp else f"{C.BRIGHT_RED}♨{C.RESET}"

    lines = [
        f"  {C.DIM}Sistema:{C.RESET} {power_str}"
        f"         {C.DIM}A/C:{C.RESET} {ac_str}",
        f"  {C.DIM}Temperatura:{C.RESET} {temp_indicator} "
        f"{C.BRIGHT_WHITE}{status.target_temp:.1f}°C{C.RESET}"
        f" {C.DIM}(atual: {status.current_temp:.1f}°C){C.RESET}",
        f"  {C.DIM}Ventilador:{C.RESET}  [{fan_bar}] "
        f"{C.WHITE}{status.fan_speed}{C.RESET}{C.DIM}/{status.max_fan}{C.RESET}",
    ]
    return _box("❄  CLIMATIZAÇÃO", lines, color=C.CYAN, title_color=C.BRIGHT_CYAN)


def render_connectivity_panel(status: ConnectivityStatus) -> str:
    """Renderiza o painel de conectividade."""
    bt_states = {
        BluetoothState.CONNECTED: (f"{C.BRIGHT_GREEN}Conectado{C.RESET}", "●"),
        BluetoothState.DISCOVERING: (f"{C.BRIGHT_YELLOW}Procurando{C.RESET}", "◌"),
        BluetoothState.PAIRING: (f"{C.BRIGHT_YELLOW}Pareando{C.RESET}", "◎"),
        BluetoothState.OFF: (f"{C.DIM}Desligado{C.RESET}", "○"),
        BluetoothState.ERROR: (f"{C.BRIGHT_RED}Erro{C.RESET}", "✗"),
    }
    wifi_states = {
        WiFiState.CONNECTED: (f"{C.BRIGHT_GREEN}Conectado{C.RESET}", "●"),
        WiFiState.SCANNING: (f"{C.BRIGHT_YELLOW}Procurando{C.RESET}", "◌"),
        WiFiState.CONNECTING: (f"{C.BRIGHT_YELLOW}Conectando{C.RESET}", "◎"),
        WiFiState.OFF: (f"{C.DIM}Desligado{C.RESET}", "○"),
        WiFiState.ERROR: (f"{C.BRIGHT_RED}Erro{C.RESET}", "✗"),
    }

    bt_label, bt_dot = bt_states.get(status.bluetooth_state, (f"{C.DIM}?{C.RESET}", "?"))
    wifi_label, wifi_dot = wifi_states.get(status.wifi_state, (f"{C.DIM}?{C.RESET}", "?"))

    bt_dev = (
        f"{C.BRIGHT_WHITE}{status.bluetooth_device.name}{C.RESET}"
        if status.bluetooth_device
        else f"{C.DIM}---{C.RESET}"
    )

    if status.wifi_network:
        signal = status.wifi_network.signal_strength
        signal_color = C.BRIGHT_GREEN if signal > 60 else C.BRIGHT_YELLOW if signal > 30 else C.BRIGHT_RED
        wifi_net = (
            f"{C.BRIGHT_WHITE}{status.wifi_network.ssid}{C.RESET}"
            f" {signal_color}({signal}%){C.RESET}"
        )
    else:
        wifi_net = f"{C.DIM}---{C.RESET}"

    lines = [
        f"  {C.BLUE}Bluetooth{C.RESET}  {bt_dot} {bt_label}   {bt_dev}",
        f"  {C.BLUE}Wi-Fi{C.RESET}      {wifi_dot} {wifi_label}   {wifi_net}",
    ]
    return _box("📡  CONECTIVIDADE", lines, color=C.BLUE, title_color=C.BRIGHT_CYAN)


def render_alerts(alerts: list[VehicleAlert]) -> str:
    """Renderiza alertas do veículo."""
    if not alerts:
        return ""

    alert_styles = {
        "INFO": (C.BRIGHT_CYAN, "ℹ"),
        "WARNING": (C.BRIGHT_YELLOW, "⚠"),
        "CRITICAL": (C.BRIGHT_RED, "🚨"),
    }
    lines: list[str] = []
    for a in alerts:
        color, icon = alert_styles.get(a.level, (C.WHITE, "?"))
        lines.append(f"  {color}{icon} {a.message}{C.RESET}")
    return _box("⚠  ALERTAS", lines, color=C.YELLOW, title_color=C.BRIGHT_YELLOW)


def render_main_menu() -> str:
    """Renderiza o menu principal de navegação."""
    lines = [
        f"  {C.BRIGHT_WHITE}[1]{C.RESET} {C.MAGENTA}Mídia{C.RESET}"
        f"         {C.BRIGHT_WHITE}[2]{C.RESET} {C.CYAN}Climatização{C.RESET}"
        f"   {C.BRIGHT_WHITE}[3]{C.RESET} {C.BLUE}Conectividade{C.RESET}",
        f"  {C.BRIGHT_WHITE}[4]{C.RESET} {C.GREEN}Veículo{C.RESET}"
        f"       {C.BRIGHT_WHITE}[5]{C.RESET} {C.DIM}Atualizar{C.RESET}"
        f"      {C.BRIGHT_WHITE}[0]{C.RESET} {C.RED}Desligar{C.RESET}",
    ]
    return _box("MENU", lines, color=C.WHITE, title_color=C.BRIGHT_WHITE)


def render_media_menu() -> str:
    """Renderiza o submenu de mídia."""
    lines = [
        f"  {C.BRIGHT_WHITE}[1]{C.RESET} {C.GREEN}▶ Play/Pause{C.RESET}"
        f"       {C.BRIGHT_WHITE}[2]{C.RESET} {C.RED}⏹ Parar{C.RESET}",
        f"  {C.BRIGHT_WHITE}[3]{C.RESET} {C.CYAN}⏭ Próxima{C.RESET}"
        f"          {C.BRIGHT_WHITE}[4]{C.RESET} {C.CYAN}⏮ Anterior{C.RESET}",
        f"  {C.BRIGHT_WHITE}[5]{C.RESET} {C.BRIGHT_GREEN}🔊 Volume +{C.RESET}"
        f"        {C.BRIGHT_WHITE}[6]{C.RESET} {C.BRIGHT_YELLOW}🔉 Volume -{C.RESET}",
        f"  {C.BRIGHT_WHITE}[7]{C.RESET} {C.DIM}🔇 Mudo{C.RESET}"
        f"            {C.BRIGHT_WHITE}[0]{C.RESET} {C.DIM}← Voltar{C.RESET}",
    ]
    return _box("MENU - MÍDIA", lines, color=C.MAGENTA, title_color=C.BRIGHT_MAGENTA)


def render_hvac_menu() -> str:
    """Renderiza o submenu de climatização."""
    lines = [
        f"  {C.BRIGHT_WHITE}[1]{C.RESET} {C.BRIGHT_RED}▲ Temp +{C.RESET}"
        f"           {C.BRIGHT_WHITE}[2]{C.RESET} {C.BRIGHT_CYAN}▼ Temp -{C.RESET}",
        f"  {C.BRIGHT_WHITE}[3]{C.RESET} {C.BRIGHT_GREEN}▲ Ventilador +{C.RESET}"
        f"     {C.BRIGHT_WHITE}[4]{C.RESET} {C.BRIGHT_YELLOW}▼ Ventilador -{C.RESET}",
        f"  {C.BRIGHT_WHITE}[5]{C.RESET} {C.CYAN}❄ Liga/Desliga AC{C.RESET}"
        f"  {C.BRIGHT_WHITE}[6]{C.RESET} {C.YELLOW}⚡ Liga/Desliga{C.RESET}",
        f"  {C.BRIGHT_WHITE}[0]{C.RESET} {C.DIM}← Voltar{C.RESET}",
    ]
    return _box("MENU - CLIMATIZAÇÃO", lines, color=C.CYAN, title_color=C.BRIGHT_CYAN)


def render_connectivity_menu() -> str:
    """Renderiza o submenu de conectividade."""
    lines = [
        f"  {C.BRIGHT_WHITE}[1]{C.RESET} {C.CYAN}Escanear Bluetooth{C.RESET}"
        f"   {C.BRIGHT_WHITE}[2]{C.RESET} {C.GREEN}Parear Bluetooth{C.RESET}",
        f"  {C.BRIGHT_WHITE}[3]{C.RESET} {C.RED}Desconectar BT{C.RESET}"
        f"       {C.BRIGHT_WHITE}[4]{C.RESET} {C.CYAN}Escanear Wi-Fi{C.RESET}",
        f"  {C.BRIGHT_WHITE}[5]{C.RESET} {C.GREEN}Conectar Wi-Fi{C.RESET}"
        f"       {C.BRIGHT_WHITE}[6]{C.RESET} {C.RED}Desconectar Wi-Fi{C.RESET}",
        f"  {C.BRIGHT_WHITE}[0]{C.RESET} {C.DIM}← Voltar{C.RESET}",
    ]
    return _box("MENU - CONECTIVIDADE", lines, color=C.BLUE, title_color=C.BRIGHT_CYAN)


def render_vehicle_menu() -> str:
    """Renderiza o submenu de dados veiculares."""
    lines = [
        f"  {C.BRIGHT_WHITE}[1]{C.RESET} {C.GREEN}Atualizar dados do veículo{C.RESET}",
        f"  {C.BRIGHT_WHITE}[0]{C.RESET} {C.DIM}← Voltar{C.RESET}",
    ]
    return _box("MENU - VEÍCULO", lines, color=C.GREEN, title_color=C.BRIGHT_GREEN)


def render_device_list(devices: list[dict[str, str]], title: str) -> str:
    """Renderiza uma lista de dispositivos/redes encontrados."""
    if not devices:
        return _box(title, [f"  {C.DIM}Nenhum dispositivo encontrado.{C.RESET}"], color=C.YELLOW)

    lines = [
        f"  {C.BRIGHT_WHITE}[{i + 1}]{C.RESET} "
        f"{C.WHITE}{d.get('name', 'Desconhecido')}{C.RESET}"
        f"  {C.DIM}{d.get('detail', '')}{C.RESET}"
        for i, d in enumerate(devices)
    ]
    lines.append(f"  {C.BRIGHT_WHITE}[0]{C.RESET} {C.DIM}Cancelar{C.RESET}")
    return _box(title, lines, color=C.YELLOW, title_color=C.BRIGHT_YELLOW)


def render_boot_progress(subsystem: str, status: str) -> str:
    """Renderiza uma linha de progresso do boot."""
    if status == "OK":
        return f"  {C.BRIGHT_GREEN}[✓]{C.RESET} {C.WHITE}{subsystem}{C.RESET}: {C.GREEN}{status}{C.RESET}"
    elif status == "Falha":
        return f"  {C.BRIGHT_RED}[✗]{C.RESET} {C.WHITE}{subsystem}{C.RESET}: {C.RED}{status}{C.RESET}"
    return f"  {C.BRIGHT_YELLOW}[…]{C.RESET} {C.WHITE}{subsystem}{C.RESET}: {C.YELLOW}{status}{C.RESET}"
