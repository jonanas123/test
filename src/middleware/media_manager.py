"""
Middleware - Gerenciador de Mídia.

Controla a reprodução de mídia (play, pause, skip),
gerenciamento de playlist e controle de volume.
"""

import logging
from dataclasses import dataclass
from enum import Enum

from src.hal.audio_hal import AudioInterface, MAX_VOLUME

logger = logging.getLogger(__name__)


class PlaybackState(Enum):
    STOPPED = "Parado"
    PLAYING = "Reproduzindo"
    PAUSED = "Pausado"


@dataclass
class Track:
    """Representa uma faixa de mídia."""
    title: str
    artist: str
    duration_seconds: int
    album: str = ""


@dataclass
class MediaStatus:
    """Estado atual do player de mídia."""
    state: PlaybackState = PlaybackState.STOPPED
    current_track: Track | None = None
    track_index: int = 0
    volume: int = 10
    muted: bool = False
    playlist_size: int = 0


class MediaManager:
    """Gerencia a reprodução de mídia e controle de volume."""

    DEFAULT_PLAYLIST = [
        Track("Aquarela", "Toquinho", 234, "Toquinho - Grandes Sucessos"),
        Track("Garota de Ipanema", "Tom Jobim", 312, "Bossa Nova Essentials"),
        Track("Evidências", "Chitãozinho & Xororó", 275, "Raízes Sertanejas"),
        Track("Bohemian Rhapsody", "Queen", 354, "A Night at the Opera"),
        Track("Blinding Lights", "The Weeknd", 200, "After Hours"),
        Track("Trem-Bala", "Ana Vilela", 232, "Ana Vilela"),
        Track("Ai Se Eu Te Pego", "Michel Teló", 178, "Na Balada"),
        Track("Smells Like Teen Spirit", "Nirvana", 301, "Nevermind"),
    ]

    def __init__(self, audio_hal: AudioInterface) -> None:
        self._audio = audio_hal
        self._state = PlaybackState.STOPPED
        self._playlist: list[Track] = list(self.DEFAULT_PLAYLIST)
        self._track_index = 0

    def get_status(self) -> MediaStatus:
        """Retorna o estado atual do player."""
        current = (
            self._playlist[self._track_index]
            if self._playlist
            else None
        )
        return MediaStatus(
            state=self._state,
            current_track=current,
            track_index=self._track_index,
            volume=self._audio.get_volume(),
            muted=self._audio.is_muted(),
            playlist_size=len(self._playlist),
        )

    def play(self) -> Track | None:
        """Inicia ou retoma a reprodução."""
        if not self._playlist:
            logger.warning("[MEDIA] Playlist vazia, impossível reproduzir.")
            return None

        track = self._playlist[self._track_index]
        self._state = PlaybackState.PLAYING
        logger.info(
            "[MEDIA] ▶ Reproduzindo: '%s' - %s",
            track.title,
            track.artist,
        )
        return track

    def pause(self) -> None:
        """Pausa a reprodução atual."""
        if self._state == PlaybackState.PLAYING:
            self._state = PlaybackState.PAUSED
            logger.info("[MEDIA] ⏸ Pausado.")

    def stop(self) -> None:
        """Para a reprodução."""
        self._state = PlaybackState.STOPPED
        logger.info("[MEDIA] ⏹ Parado.")

    def next_track(self) -> Track | None:
        """Avança para a próxima faixa."""
        if not self._playlist:
            return None

        self._track_index = (self._track_index + 1) % len(self._playlist)
        track = self._playlist[self._track_index]
        self._state = PlaybackState.PLAYING
        logger.info(
            "[MEDIA] ⏭ Próxima: '%s' - %s",
            track.title,
            track.artist,
        )
        return track

    def previous_track(self) -> Track | None:
        """Volta para a faixa anterior."""
        if not self._playlist:
            return None

        self._track_index = (self._track_index - 1) % len(self._playlist)
        track = self._playlist[self._track_index]
        self._state = PlaybackState.PLAYING
        logger.info(
            "[MEDIA] ⏮ Anterior: '%s' - %s",
            track.title,
            track.artist,
        )
        return track

    def volume_up(self, step: int = 1) -> int:
        """Aumenta o volume."""
        current = self._audio.get_volume()
        new_vol = self._audio.set_volume(current + step)
        logger.info("[MEDIA] 🔊 Volume: %d/%d", new_vol, MAX_VOLUME)
        return new_vol

    def volume_down(self, step: int = 1) -> int:
        """Diminui o volume."""
        current = self._audio.get_volume()
        new_vol = self._audio.set_volume(current - step)
        logger.info("[MEDIA] 🔉 Volume: %d/%d", new_vol, MAX_VOLUME)
        return new_vol

    def toggle_mute(self) -> bool:
        """Alterna silêncio."""
        if self._audio.is_muted():
            self._audio.unmute()
        else:
            self._audio.mute()
        return self._audio.is_muted()

    def set_volume(self, level: int) -> int:
        """Define o volume diretamente."""
        return self._audio.set_volume(level)
