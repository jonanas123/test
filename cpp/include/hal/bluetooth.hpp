/**
 * @file bluetooth.hpp
 * @brief HAL — Abstração da interface Bluetooth.
 */

#pragma once

#include <string>
#include <vector>

namespace infotainment::hal {

enum class BluetoothState { OFF, DISCOVERING, PAIRING, CONNECTED, ERROR };

struct BluetoothDevice {
    std::string name;
    std::string address;
    int         rssi = -50;
};

class BluetoothInterface {
public:
    virtual ~BluetoothInterface() = default;
    virtual bool initialize() = 0;
    virtual void shutdown()   = 0;
    virtual std::vector<BluetoothDevice> scan()                   = 0;
    virtual bool                         pair(const std::string& addr) = 0;
    virtual void                         disconnect()             = 0;
    virtual BluetoothState               get_state() const        = 0;
    virtual BluetoothDevice              get_connected() const    = 0;
};

class MockBluetooth final : public BluetoothInterface {
public:
    bool initialize() override { state_ = BluetoothState::OFF; return true; }
    void shutdown()   override { state_ = BluetoothState::OFF; connected_ = {}; }

    std::vector<BluetoothDevice> scan() override {
        state_ = BluetoothState::DISCOVERING;
        return {
            {"iPhone de João",  "AA:BB:CC:DD:EE:01", -45},
            {"Galaxy S24",      "AA:BB:CC:DD:EE:02", -55},
            {"AirPods Pro",     "AA:BB:CC:DD:EE:03", -30},
            {"JBL Charge 5",    "AA:BB:CC:DD:EE:04", -60},
        };
    }

    bool pair(const std::string& addr) override {
        state_ = BluetoothState::PAIRING;
        connected_ = {"Dispositivo", addr, -40};
        state_ = BluetoothState::CONNECTED;
        return true;
    }

    void disconnect() override { state_ = BluetoothState::OFF; connected_ = {}; }
    BluetoothState  get_state()     const override { return state_; }
    BluetoothDevice get_connected() const override { return connected_; }

private:
    BluetoothState  state_ = BluetoothState::OFF;
    BluetoothDevice connected_;
};

} // namespace infotainment::hal
