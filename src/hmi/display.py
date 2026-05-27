"""
HMI - Módulo de Display.

Responsável por renderizar a interface da central multimídia no terminal,
incluindo painéis de status, menus e alertas.
"""

import os
from datetime import datetime

from src.hal.bluetooth_hal import BluetoothState
from src.hal.wifi_hal import WiFiState
from src.middleware.connectivity_manager import ConnectivityStatus
from src.middleware.hvac_manager import ClimateStatus
from src.middleware.media_manager import MediaStatus, PlaybackState
from src.middleware.vehicle_manager import VehicleAlert, VehicleStatus

TERMINAL_WIDTH = 62
SEPARATOR = "═" * TERMINAL_WIDTH
THIN_SEP = "─" * TERMINAL_WIDTH


def clear_screen() -> None:
    """Limpa o terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def _center(text: str, width: int = TERMINAL_WIDTH) -> str:
    return text.center(width)


def _box(title: str, lines: list[str]) -> str:
    """Cria uma caixa com título e linhas de conteúdo."""
    output = [f"╔{'═' * (TERMINAL_WIDTH - 2)}╗"]
    output.append(f"║{_center(f' {title} ', TERMINAL_WIDTH - 2)}║")
    output.append(f"╠{'═' * (TERMINAL_WIDTH - 2)}╣")
    for line in lines:
        padded = f" {line}".ljust(TERMINAL_WIDTH - 3)
        output.append(f"║{padded}║")
    output.append(f"╚{'═' * (TERMINAL_WIDTH - 2)}╝")
    return "\n".join(output)


def render_header() -> str:
    """Renderiza o cabeçalho da central multimídia."""
    now = datetime.now().strftime("%H:%M:%S")
    date = datetime.now().strftime("%d/%m/%Y")
    return _box("CENTRAL MULTIMÍDIA AUTOMOTIVA", [
        f"   Data: {date}          Hora: {now}",
    ])


def render_vehicle_panel(status: VehicleStatus) -> str:
    """Renderiza o painel de dados do veículo."""
    doors_str = ", ".join(status.doors_open) if status.doors_open else "Todas fechadas"
    brake_str = "ATIVADO" if status.parking_brake else "Desativado"
    lights_str = "ACESOS" if status.headlights_on else "Apagados"

    lines = [
        f"   Velocidade:   {status.speed_display:>12}   RPM: {status.rpm:>5}",
        f"   Combustível:  [{status.fuel_bar}] {status.fuel_level_percent:.1f}%",
        f"   Temp. Motor:  {status.engine_temp_celsius:.1f}°C",
        f"   Portas:       {doors_str}",
        f"   Freio de mão: {brake_str}   Faróis: {lights_str}",
    ]
    return _box("VEÍCULO", lines)


def render_media_panel(status: MediaStatus) -> str:
    """Renderiza o painel do player de mídia."""
    if status.current_track:
        track = status.current_track
        title = f"{track.title} - {track.artist}"
        album = track.album
        minutes = track.duration_seconds // 60
        seconds = track.duration_seconds % 60
        duration = f"{minutes}:{seconds:02d}"
    else:
        title = "Nenhuma faixa selecionada"
        album = ""
        duration = "--:--"

    state_icon = {
        PlaybackState.PLAYING: "▶ Reproduzindo",
        PlaybackState.PAUSED: "⏸ Pausado",
        PlaybackState.STOPPED: "⏹ Parado",
    }

    vol_bar_filled = int(status.volume / 30 * 15)
    vol_bar = "█" * vol_bar_filled + "░" * (15 - vol_bar_filled)
    mute_str = " [MUDO]" if status.muted else ""

    lines = [
        f"   {state_icon.get(status.state, '?')}",
        f"   {title}",
        f"   {album}   [{duration}]" if album else f"   [{duration}]",
        f"   Faixa {status.track_index + 1}/{status.playlist_size}",
        f"   Volume: [{vol_bar}] {status.volume}/30{mute_str}",
    ]
    return _box("MÍDIA", lines)


def render_hvac_panel(status: ClimateStatus) -> str:
    """Renderiza o painel de climatização."""
    power_str = "LIGADO" if status.power_on else "DESLIGADO"
    ac_str = "LIGADO" if status.ac_on else "DESLIGADO"
    fan_bar = "●" * status.fan_speed + "○" * (status.max_fan - status.fan_speed)

    lines = [
        f"   Sistema: {power_str}       A/C: {ac_str}",
        f"   Temperatura:  Alvo={status.target_temp:.1f}°C  Atual={status.current_temp:.1f}°C",
        f"   Ventilador:   [{fan_bar}] {status.fan_speed}/{status.max_fan}",
    ]
    return _box("CLIMATIZAÇÃO", lines)


def render_connectivity_panel(status: ConnectivityStatus) -> str:
    """Renderiza o painel de conectividade."""
    bt_icon = {
        BluetoothState.CONNECTED: "🔗",
        BluetoothState.DISCOVERING: "🔍",
        BluetoothState.PAIRING: "⏳",
        BluetoothState.OFF: "⭘",
        BluetoothState.ERROR: "⚠",
    }
    wifi_icon = {
        WiFiState.CONNECTED: "📶",
        WiFiState.SCANNING: "🔍",
        WiFiState.CONNECTING: "⏳",
        WiFiState.OFF: "⭘",
        WiFiState.ERROR: "⚠",
    }

    bt_dev = (
        status.bluetooth_device.name
        if status.bluetooth_device
        else "Nenhum"
    )
    wifi_net = (
        f"{status.wifi_network.ssid} ({status.wifi_network.signal_strength}%)"
        if status.wifi_network
        else "Nenhuma"
    )

    lines = [
        f"   Bluetooth {bt_icon.get(status.bluetooth_state, '?')} "
        f"{status.bluetooth_state.value}  -  {bt_dev}",
        f"   Wi-Fi     {wifi_icon.get(status.wifi_state, '?')} "
        f"{status.wifi_state.value}  -  {wifi_net}",
    ]
    return _box("CONECTIVIDADE", lines)


def render_alerts(alerts: list[VehicleAlert]) -> str:
    """Renderiza alertas do veículo."""
    if not alerts:
        return ""

    icons = {"INFO": "ℹ", "WARNING": "⚠", "CRITICAL": "🚨"}
    lines = [
        f"   {icons.get(a.level, '?')} [{a.level}] {a.message}"
        for a in alerts
    ]
    return _box("ALERTAS", lines)


def render_main_menu() -> str:
    """Renderiza o menu principal de navegação."""
    lines = [
        "   [1] Mídia          [2] Climatização    [3] Conectividade",
        "   [4] Veículo        [5] Atualizar Tela  [0] Desligar",
    ]
    return _box("MENU PRINCIPAL", lines)


def render_media_menu() -> str:
    """Renderiza o submenu de mídia."""
    lines = [
        "   [1] ▶ Play/Pause      [2] ⏹ Parar",
        "   [3] ⏭ Próxima         [4] ⏮ Anterior",
        "   [5] 🔊 Volume +       [6] 🔉 Volume -",
        "   [7] 🔇 Mudo           [0] ← Voltar",
    ]
    return _box("MENU - MÍDIA", lines)


def render_hvac_menu() -> str:
    """Renderiza o submenu de climatização."""
    lines = [
        "   [1] 🔼 Temperatura +  [2] 🔽 Temperatura -",
        "   [3] 💨 Ventilador +   [4] 💨 Ventilador -",
        "   [5] ❄ Liga/Desliga AC [6] ⚡ Liga/Desliga HVAC",
        "   [0] ← Voltar",
    ]
    return _box("MENU - CLIMATIZAÇÃO", lines)


def render_connectivity_menu() -> str:
    """Renderiza o submenu de conectividade."""
    lines = [
        "   [1] 🔍 Escanear Bluetooth  [2] 🔗 Parear Bluetooth",
        "   [3] ❌ Desconectar BT       [4] 🔍 Escanear Wi-Fi",
        "   [5] 📶 Conectar Wi-Fi       [6] ❌ Desconectar Wi-Fi",
        "   [0] ← Voltar",
    ]
    return _box("MENU - CONECTIVIDADE", lines)


def render_vehicle_menu() -> str:
    """Renderiza o submenu de dados veiculares."""
    lines = [
        "   [1] 🔄 Atualizar dados do veículo",
        "   [0] ← Voltar",
    ]
    return _box("MENU - VEÍCULO", lines)


def render_device_list(devices: list[dict[str, str]], title: str) -> str:
    """Renderiza uma lista de dispositivos/redes encontrados."""
    if not devices:
        return _box(title, ["   Nenhum dispositivo encontrado."])

    lines = [
        f"   [{i + 1}] {d.get('name', 'Desconhecido')}  -  {d.get('detail', '')}"
        for i, d in enumerate(devices)
    ]
    lines.append("   [0] Cancelar")
    return _box(title, lines)


def render_boot_progress(subsystem: str, status: str) -> str:
    """Renderiza uma linha de progresso do boot."""
    icon = "✓" if status == "OK" else "✗" if status == "Falha" else "…"
    return f"   [{icon}] {subsystem}: {status}"
