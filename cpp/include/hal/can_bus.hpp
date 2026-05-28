/**
 * @file can_bus.hpp
 * @brief HAL — Abstração da interface CAN Bus para dados veiculares.
 *
 * Define a interface abstrata e a implementação mock para simulação
 * de leitura de dados do veículo via rede CAN.
 */

#pragma once

#include <string>
#include <vector>
#include <random>
#include <algorithm>
#include <cmath>

namespace infotainment::hal {

/// Dados crus lidos do barramento CAN
struct VehicleData {
    double speed_kmh        = 0.0;
    int    rpm              = 800;
    double fuel_percent     = 100.0;
    double engine_temp_c    = 90.0;
    bool   door_driver      = false;
    bool   door_passenger   = false;
    bool   door_rear_left   = false;
    bool   door_rear_right  = false;
    bool   parking_brake    = true;
    bool   headlights       = false;
};

/// Interface abstrata do barramento CAN (DIP — SOLID)
class CANBusInterface {
public:
    virtual ~CANBusInterface() = default;
    virtual bool         initialize() = 0;
    virtual void         shutdown()   = 0;
    virtual VehicleData  read()       = 0;
};

/// Implementação mock com dados simulados
class MockCANBus final : public CANBusInterface {
public:
    bool initialize() override {
        gen_.seed(std::random_device{}());
        return true;
    }

    void shutdown() override { /* noop */ }

    VehicleData read() override {
        std::uniform_real_distribution<> speed_delta(-4.0, 10.0);
        std::uniform_real_distribution<> rpm_jitter(-100.0, 100.0);
        std::uniform_real_distribution<> fuel_drain(0.0, 0.05);
        std::uniform_real_distribution<> temp_var(85.0, 100.0);
        std::uniform_real_distribution<> door_chance(0.0, 1.0);

        data_.speed_kmh = std::clamp(data_.speed_kmh + speed_delta(gen_), 0.0, 220.0);
        data_.rpm       = std::clamp(static_cast<int>(800 + data_.speed_kmh * 30 + rpm_jitter(gen_)), 600, 7000);
        data_.fuel_percent = std::max(0.0, data_.fuel_percent - fuel_drain(gen_));
        data_.engine_temp_c = temp_var(gen_);

        data_.door_driver    = door_chance(gen_) < 0.03;
        data_.door_passenger = door_chance(gen_) < 0.02;
        data_.parking_brake  = data_.speed_kmh < 5.0;
        data_.headlights     = data_.speed_kmh > 0.0;

        return data_;
    }

private:
    VehicleData         data_;
    std::mt19937        gen_;
};

} // namespace infotainment::hal
