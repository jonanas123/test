/**
 * @file connectivity_manager.hpp
 * @brief Middleware — Gerenciador unificado de Bluetooth e Wi-Fi.
 */

#pragma once

#include "hal/bluetooth.hpp"
#include "hal/wifi.hpp"

namespace infotainment::middleware {

struct ConnectivityStatus {
    hal::BluetoothState  bt_state    = hal::BluetoothState::OFF;
    hal::BluetoothDevice bt_device;
    hal::WiFiState       wifi_state  = hal::WiFiState::OFF;
    hal::WiFiNetwork     wifi_network;
};

class ConnectivityManager {
public:
    ConnectivityManager(hal::BluetoothInterface& bt, hal::WiFiInterface& wifi)
        : bt_(bt), wifi_(wifi) {}

    auto scan_bluetooth()  { return bt_.scan(); }
    bool pair_bluetooth(const std::string& addr)  { return bt_.pair(addr); }
    void disconnect_bluetooth() { bt_.disconnect(); }

    auto scan_wifi()       { return wifi_.scan(); }
    bool connect_wifi(const std::string& ssid, const std::string& pass = "") {
        return wifi_.connect(ssid, pass);
    }
    void disconnect_wifi() { wifi_.disconnect(); }

    ConnectivityStatus get_status() const {
        return {
            bt_.get_state(),
            bt_.get_connected(),
            wifi_.get_state(),
            wifi_.get_connected(),
        };
    }

private:
    hal::BluetoothInterface& bt_;
    hal::WiFiInterface&      wifi_;
};

} // namespace infotainment::middleware
