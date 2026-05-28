/**
 * @file main.cpp
 * @brief Ponto de entrada do sistema de infotainment (C++).
 *
 * Inicializa as camadas HAL → Middleware e executa a sequência de boot.
 * A interface HMI é fornecida pelo frontend web (HTML/CSS/JS).
 */

#include "hal/can_bus.hpp"
#include "hal/bluetooth.hpp"
#include "hal/audio.hpp"
#include "hal/hvac.hpp"
#include "hal/wifi.hpp"

#include "middleware/boot_manager.hpp"
#include "middleware/media_manager.hpp"
#include "middleware/hvac_manager.hpp"
#include "middleware/vehicle_manager.hpp"
#include "middleware/connectivity_manager.hpp"

#include <iostream>
#include <iomanip>

int main() {
    using namespace infotainment;

    // ── Instanciar HAL (mocks) ────────────────────────────
    hal::MockCANBus   can;
    hal::MockBluetooth bt;
    hal::MockAudio    audio;
    hal::MockHVAC     hvac;
    hal::MockWiFi     wifi;

    // ── Instanciar Middleware (injeção de dependência) ─────
    middleware::BootManager         boot(can, bt, audio, hvac, wifi);
    middleware::MediaManager        media(audio);
    middleware::HVACManager         climate(hvac);
    middleware::VehicleManager      vehicle(can);
    middleware::ConnectivityManager connectivity(bt, wifi);

    // ── Boot ──────────────────────────────────────────────
    std::cout << "\n"
              << "  ╔══════════════════════════════════════════╗\n"
              << "  ║    CENTRAL MULTIMÍDIA AUTOMOTIVA         ║\n"
              << "  ║           Infotainment v1.0 (C++)        ║\n"
              << "  ╚══════════════════════════════════════════╝\n\n";

    auto report = boot.run_boot_sequence();

    for (const auto& [name, status] : report.subsystems) {
        const char* icon = (status == "OK") ? "✓" : "✗";
        std::cout << "  [" << icon << "] " << name << ": " << status << "\n";
    }

    std::cout << "\n  Boot completo em "
              << std::fixed << std::setprecision(3)
              << report.boot_time_seconds << "s\n";

    // ── Demonstrar funcionalidades ────────────────────────
    std::cout << "\n  --- Mídia ---\n";
    media.play();
    auto ms = media.get_status();
    std::cout << "  ▶ " << ms.current_track.title
              << " - " << ms.current_track.artist << "\n";

    media.next_track();
    ms = media.get_status();
    std::cout << "  ⏭ " << ms.current_track.title
              << " - " << ms.current_track.artist << "\n";

    std::cout << "\n  --- Climatização ---\n";
    auto cs = climate.get_status();
    std::cout << "  Temp: " << cs.target_temp << "°C  Fan: "
              << cs.fan_speed << "/" << cs.max_fan << "\n";

    climate.increase_temperature();
    climate.increase_fan();
    cs = climate.get_status();
    std::cout << "  Temp: " << cs.target_temp << "°C  Fan: "
              << cs.fan_speed << "/" << cs.max_fan << "\n";

    std::cout << "\n  --- Veículo ---\n";
    auto vs = vehicle.read_data();
    std::cout << "  Velocidade: " << std::fixed << std::setprecision(0)
              << vs.speed_kmh << " km/h  RPM: " << vs.rpm << "\n"
              << "  Combustível: " << std::setprecision(1)
              << vs.fuel_percent << "%  Temp: "
              << vs.engine_temp_c << "°C\n";

    if (!vs.alerts.empty()) {
        std::cout << "\n  --- Alertas ---\n";
        for (const auto& a : vs.alerts) {
            std::cout << "  [" << a.level << "] " << a.message << "\n";
        }
    }

    std::cout << "\n  Sistema pronto. Frontend web em web/index.html\n\n";
    return 0;
}
