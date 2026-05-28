/**
 * @file vehicle_manager.hpp
 * @brief Middleware — Gerenciador de dados veiculares e alertas.
 */

#pragma once

#include "hal/can_bus.hpp"
#include <string>
#include <vector>

namespace infotainment::middleware {

struct VehicleAlert {
    std::string level;   // "INFO", "WARNING", "CRITICAL"
    std::string message;
};

struct VehicleStatus {
    double                   speed_kmh       = 0.0;
    int                      rpm             = 0;
    double                   fuel_percent    = 100.0;
    double                   engine_temp_c   = 90.0;
    std::vector<std::string> doors_open;
    bool                     parking_brake   = true;
    bool                     headlights      = false;
    std::vector<VehicleAlert> alerts;
};

class VehicleManager {
public:
    static constexpr double SPEED_LIMIT    = 120.0;
    static constexpr double FUEL_LOW       = 15.0;
    static constexpr double TEMP_HIGH      = 110.0;

    explicit VehicleManager(hal::CANBusInterface& can) : can_(can) {}

    VehicleStatus read_data() {
        auto raw = can_.read();
        VehicleStatus status;
        status.speed_kmh     = raw.speed_kmh;
        status.rpm           = raw.rpm;
        status.fuel_percent  = raw.fuel_percent;
        status.engine_temp_c = raw.engine_temp_c;
        status.parking_brake = raw.parking_brake;
        status.headlights    = raw.headlights;

        if (raw.door_driver)     status.doors_open.push_back("Motorista");
        if (raw.door_passenger)  status.doors_open.push_back("Passageiro");
        if (raw.door_rear_left)  status.doors_open.push_back("Traseira Esq.");
        if (raw.door_rear_right) status.doors_open.push_back("Traseira Dir.");

        generate_alerts(status);
        return status;
    }

private:
    void generate_alerts(VehicleStatus& s) {
        if (s.speed_kmh > SPEED_LIMIT)
            s.alerts.push_back({"WARNING", "Velocidade acima de 120 km/h!"});
        if (s.fuel_percent < FUEL_LOW)
            s.alerts.push_back({"CRITICAL", "Combustível abaixo de 15%!"});
        if (s.engine_temp_c > TEMP_HIGH)
            s.alerts.push_back({"CRITICAL", "Temperatura do motor elevada!"});
        if (!s.doors_open.empty())
            s.alerts.push_back({"WARNING", "Porta(s) aberta(s)!"});
    }

    hal::CANBusInterface& can_;
};

} // namespace infotainment::middleware
