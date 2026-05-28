/**
 * @file media_manager.hpp
 * @brief Middleware — Gerenciador de mídia (playlist, controle de reprodução).
 */

#pragma once

#include "hal/audio.hpp"
#include <string>
#include <vector>

namespace infotainment::middleware {

enum class PlaybackState { STOPPED, PLAYING, PAUSED };

struct Track {
    std::string title;
    std::string artist;
    std::string album;
    int         duration_seconds;
};

struct MediaStatus {
    PlaybackState state       = PlaybackState::STOPPED;
    int           track_index = 0;
    int           volume      = 10;
    bool          muted       = false;
    Track         current_track;
    int           playlist_size = 0;
};

class MediaManager {
public:
    explicit MediaManager(hal::AudioInterface& audio) : audio_(audio) {
        playlist_ = {
            {"Aquarela",          "Toquinho",       "Grandes Sucessos",      234},
            {"Garota de Ipanema", "Tom Jobim",      "Bossa Nova Essentials", 312},
            {"Mas Que Nada",      "Jorge Ben Jor",  "Samba Esquema Novo",    178},
            {"Chega de Saudade",  "João Gilberto",  "O Amor, o Sorriso...", 248},
            {"País Tropical",     "Jorge Ben Jor",  "Grandes Sucessos",      206},
            {"Construção",        "Chico Buarque",  "Construção",            378},
            {"Wave",              "Tom Jobim",      "Wave",                  195},
            {"Águas de Março",    "Elis Regina",    "Elis & Tom",            210},
        };
        track_index_ = 0;
    }

    void play()  { state_ = PlaybackState::PLAYING; }
    void pause() { state_ = PlaybackState::PAUSED; }
    void stop()  { state_ = PlaybackState::STOPPED; }

    void next_track() {
        track_index_ = (track_index_ + 1) % static_cast<int>(playlist_.size());
    }

    void previous_track() {
        track_index_ = (track_index_ - 1 + static_cast<int>(playlist_.size()))
                      % static_cast<int>(playlist_.size());
    }

    void volume_up()   { audio_.set_volume(audio_.get_volume() + 1); }
    void volume_down() { audio_.set_volume(audio_.get_volume() - 1); }

    void toggle_mute() { audio_.set_mute(!audio_.is_muted()); }

    MediaStatus get_status() const {
        return {
            state_,
            track_index_,
            audio_.get_volume(),
            audio_.is_muted(),
            playlist_[track_index_],
            static_cast<int>(playlist_.size()),
        };
    }

private:
    hal::AudioInterface&  audio_;
    std::vector<Track>    playlist_;
    int                   track_index_ = 0;
    PlaybackState         state_       = PlaybackState::STOPPED;
};

} // namespace infotainment::middleware
