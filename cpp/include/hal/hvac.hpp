/**
 * @file hvac.hpp
 * @brief HAL — Abstração do sistema HVAC (climatização).
 */

#pragma once

#include <algorithm>

namespace infotainment::hal {

struct HVACState {
    bool   power_on     = true;
    bool   ac_on        = true;
    double target_temp  = 22.0;
    double current_temp = 25.0;
    int    fan_speed    = 2;
};

class HVACInterface {
public:
    virtual ~HVACInterface() = default;
    virtual bool      initialize()                 = 0;
    virtual void      shutdown()                   = 0;
    virtual void      set_target_temp(double temp) = 0;
    virtual void      set_fan_speed(int speed)     = 0;
    virtual void      set_ac(bool on)              = 0;
    virtual void      set_power(bool on)           = 0;
    virtual HVACState get_state() const            = 0;
};

class MockHVAC final : public HVACInterface {
public:
    bool initialize() override { return true; }
    void shutdown()   override { state_.power_on = false; state_.fan_speed = 0; }

    void set_target_temp(double temp) override {
        state_.target_temp = std::clamp(temp, 16.0, 30.0);
    }

    void set_fan_speed(int speed) override {
        state_.fan_speed = std::clamp(speed, 0, 5);
    }

    void set_ac(bool on)    override { state_.ac_on = on; }
    void set_power(bool on) override { state_.power_on = on; }
    HVACState get_state() const override { return state_; }

private:
    HVACState state_;
};

} // namespace infotainment::hal
