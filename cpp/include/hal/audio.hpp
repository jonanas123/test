/**
 * @file audio.hpp
 * @brief HAL — Abstração do sistema de áudio.
 */

#pragma once

#include <algorithm>

namespace infotainment::hal {

class AudioInterface {
public:
    virtual ~AudioInterface() = default;
    virtual bool initialize()             = 0;
    virtual void shutdown()               = 0;
    virtual void set_volume(int level)    = 0;
    virtual int  get_volume() const       = 0;
    virtual void set_mute(bool muted)     = 0;
    virtual bool is_muted() const         = 0;
};

class MockAudio final : public AudioInterface {
public:
    bool initialize() override { volume_ = 10; muted_ = false; return true; }
    void shutdown()   override { volume_ = 0; }

    void set_volume(int level) override {
        volume_ = std::clamp(level, 0, 30);
    }

    int  get_volume() const override { return volume_; }
    void set_mute(bool m)   override { muted_ = m; }
    bool is_muted()  const  override { return muted_; }

private:
    int  volume_ = 10;
    bool muted_  = false;
};

} // namespace infotainment::hal
