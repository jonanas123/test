/**
 * @file wifi.hpp
 * @brief HAL — Abstração da interface Wi-Fi.
 */

#pragma once

#include <string>
#include <vector>

namespace infotainment::hal {

enum class WiFiState { OFF, SCANNING, CONNECTING, CONNECTED, ERROR };

struct WiFiNetwork {
    std::string ssid;
    int         signal_strength = 0;
    bool        secured         = false;
};

class WiFiInterface {
public:
    virtual ~WiFiInterface() = default;
    virtual bool initialize() = 0;
    virtual void shutdown()   = 0;
    virtual std::vector<WiFiNetwork> scan()                                          = 0;
    virtual bool                     connect(const std::string& ssid, const std::string& pass) = 0;
    virtual void                     disconnect()                                    = 0;
    virtual WiFiState                get_state() const                               = 0;
    virtual WiFiNetwork              get_connected() const                           = 0;
};

class MockWiFi final : public WiFiInterface {
public:
    bool initialize() override { state_ = WiFiState::OFF; return true; }
    void shutdown()   override { state_ = WiFiState::OFF; connected_ = {}; }

    std::vector<WiFiNetwork> scan() override {
        state_ = WiFiState::SCANNING;
        return {
            {"Home_5G",      92, true},
            {"Cafe_WiFi",    65, false},
            {"Vizinho_Net",  34, true},
            {"IoT_Network",  78, true},
        };
    }

    bool connect(const std::string& ssid, const std::string& /*pass*/) override {
        state_ = WiFiState::CONNECTING;
        connected_ = {ssid, 85, true};
        state_ = WiFiState::CONNECTED;
        return true;
    }

    void disconnect() override { state_ = WiFiState::OFF; connected_ = {}; }
    WiFiState   get_state()     const override { return state_; }
    WiFiNetwork get_connected() const override { return connected_; }

private:
    WiFiState   state_ = WiFiState::OFF;
    WiFiNetwork connected_;
};

} // namespace infotainment::hal
