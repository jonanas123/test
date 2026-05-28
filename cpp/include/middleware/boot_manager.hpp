/**
 * @file boot_manager.hpp
 * @brief Middleware — Gerenciador da sequência de boot do sistema.
 */

#pragma once

#include "hal/can_bus.hpp"
#include "hal/bluetooth.hpp"
#include "hal/audio.hpp"
#include "hal/hvac.hpp"
#include "hal/wifi.hpp"

#include <chrono>
#include <map>
#include <string>

namespace infotainment::middleware {

struct BootReport {
    std::map<std::string, std::string> subsystems;
    double boot_time_seconds = 0.0;
    bool   all_ok            = true;
};

class BootManager {
public:
    BootManager(hal::CANBusInterface& can,
                hal::BluetoothInterface& bt,
                hal::AudioInterface& audio,
                hal::HVACInterface& hvac,
                hal::WiFiInterface& wifi)
        : can_(can), bt_(bt), audio_(audio), hvac_(hvac), wifi_(wifi) {}

    BootReport run_boot_sequence() {
        auto start = std::chrono::steady_clock::now();
        BootReport report;

        report.subsystems["CAN Bus"]   = can_.initialize()   ? "OK" : "Falha";
        report.subsystems["Bluetooth"] = bt_.initialize()    ? "OK" : "Falha";
        report.subsystems["Áudio"]     = audio_.initialize() ? "OK" : "Falha";
        report.subsystems["HVAC"]      = hvac_.initialize()  ? "OK" : "Falha";
        report.subsystems["Wi-Fi"]     = wifi_.initialize()  ? "OK" : "Falha";

        auto end = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsed = end - start;
        report.boot_time_seconds = elapsed.count();

        for (auto& [name, status] : report.subsystems) {
            if (status != "OK") { report.all_ok = false; break; }
        }

        return report;
    }

private:
    hal::CANBusInterface&   can_;
    hal::BluetoothInterface& bt_;
    hal::AudioInterface&    audio_;
    hal::HVACInterface&     hvac_;
    hal::WiFiInterface&     wifi_;
};

} // namespace infotainment::middleware
