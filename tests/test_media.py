"""Testes unitários para o módulo de Mídia."""

from src.hal.audio_hal import MockAudio
from src.middleware.media_manager import MediaManager, PlaybackState


def _create_media_manager() -> MediaManager:
    audio = MockAudio()
    audio.initialize()
    return MediaManager(audio)


class TestMediaManager:
    def test_initial_state_stopped(self) -> None:
        media = _create_media_manager()
        status = media.get_status()
        assert status.state == PlaybackState.STOPPED

    def test_play_starts_playback(self) -> None:
        media = _create_media_manager()
        track = media.play()
        assert track is not None
        assert media.get_status().state == PlaybackState.PLAYING

    def test_pause_pauses_playback(self) -> None:
        media = _create_media_manager()
        media.play()
        media.pause()
        assert media.get_status().state == PlaybackState.PAUSED

    def test_stop_stops_playback(self) -> None:
        media = _create_media_manager()
        media.play()
        media.stop()
        assert media.get_status().state == PlaybackState.STOPPED

    def test_next_track_advances(self) -> None:
        media = _create_media_manager()
        media.play()
        first_track = media.get_status().current_track
        media.next_track()
        second_track = media.get_status().current_track
        assert first_track != second_track

    def test_previous_track_goes_back(self) -> None:
        media = _create_media_manager()
        media.play()
        media.next_track()
        second = media.get_status().current_track
        media.previous_track()
        back = media.get_status().current_track
        assert back != second

    def test_volume_up(self) -> None:
        media = _create_media_manager()
        initial_vol = media.get_status().volume
        new_vol = media.volume_up()
        assert new_vol == initial_vol + 1

    def test_volume_down(self) -> None:
        media = _create_media_manager()
        initial_vol = media.get_status().volume
        new_vol = media.volume_down()
        assert new_vol == initial_vol - 1

    def test_toggle_mute(self) -> None:
        media = _create_media_manager()
        media.toggle_mute()
        assert media.get_status().muted is True
        media.toggle_mute()
        assert media.get_status().muted is False

    def test_playlist_not_empty(self) -> None:
        media = _create_media_manager()
        assert media.get_status().playlist_size > 0
