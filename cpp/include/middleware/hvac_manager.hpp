/**
 * @file hvac_manager.hpp
 * @brief Middleware — Gerenciador de climatização (HVAC).
 */

#pragma once

#include "hal/hvac.hpp"

namespace infotainment::middleware {

struct ClimateStatus {
    bool   power_on     = true;
    bool   ac_on        = true;
    double target_temp  = 22.0;
    double current_temp = 25.0;
    int    fan_speed    = 2;
    int    max_fan      = 5;
};

class HVACManager {
public:
    explicit HVACManager(hal::HVACInterface& hvac) : hvac_(hvac) {}

    void increase_temperature() {
        auto s = hvac_.get_state();
        hvac_.set_target_temp(s.target_temp + 0.5);
    }

    void decrease_temperature() {
        auto s = hvac_.get_state();
        hvac_.set_target_temp(s.target_temp - 0.5);
    }

    void increase_fan() {
        auto s = hvac_.get_state();
        hvac_.set_fan_speed(s.fan_speed + 1);
    }

    void decrease_fan() {
        auto s = hvac_.get_state();
        hvac_.set_fan_speed(s.fan_speed - 1);
    }

    void toggle_ac() {
        auto s = hvac_.get_state();
        hvac_.set_ac(!s.ac_on);
    }

    void toggle_power() {
        auto s = hvac_.get_state();
        hvac_.set_power(!s.power_on);
    }

    ClimateStatus get_status() const {
        auto s = hvac_.get_state();
        return {s.power_on, s.ac_on, s.target_temp, s.current_temp, s.fan_speed, 5};
    }

private:
    hal::HVACInterface& hvac_;
};

} // namespace infotainment::middleware
