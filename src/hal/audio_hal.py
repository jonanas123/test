"""
HAL - Abstração do sistema de áudio.

Define a interface para controle de saída de áudio e
fornece uma implementação mock.
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

MIN_VOLUME = 0
MAX_VOLUME = 30


class AudioInterface(ABC):
    """Interface abstrata para o sistema de áudio."""

    @abstractmethod
    def initialize(self) -> bool:
        """Inicializa o sistema de áudio."""

    @abstractmethod
    def set_volume(self, level: int) -> int:
        """Define o volume (0-30). Retorna o volume efetivo."""

    @abstractmethod
    def get_volume(self) -> int:
        """Retorna o volume atual."""

    @abstractmethod
    def mute(self) -> None:
        """Silencia a saída de áudio."""

    @abstractmethod
    def unmute(self) -> None:
        """Restaura o volume anterior."""

    @abstractmethod
    def is_muted(self) -> bool:
        """Verifica se o áudio está silenciado."""

    @abstractmethod
    def shutdown(self) -> None:
        """Desliga o sistema de áudio."""


class MockAudio(AudioInterface):
    """Implementação mock do sistema de áudio."""

    def __init__(self) -> None:
        self._volume = 10
        self._muted = False
        self._volume_before_mute = 10
        self._initialized = False

    def initialize(self) -> bool:
        logger.info("[AUDIO] Inicializando sistema de áudio (mock)...")
        self._initialized = True
        logger.info("[AUDIO] Sistema de áudio inicializado. Volume: %d", self._volume)
        return True

    def set_volume(self, level: int) -> int:
        clamped = max(MIN_VOLUME, min(MAX_VOLUME, level))
        self._volume = clamped
        self._muted = False
        logger.info("[AUDIO] Volume ajustado para %d/%d.", clamped, MAX_VOLUME)
        return clamped

    def get_volume(self) -> int:
        return 0 if self._muted else self._volume

    def mute(self) -> None:
        if not self._muted:
            self._volume_before_mute = self._volume
            self._muted = True
            logger.info("[AUDIO] Áudio silenciado.")

    def unmute(self) -> None:
        if self._muted:
            self._muted = False
            logger.info("[AUDIO] Áudio restaurado. Volume: %d", self._volume)

    def is_muted(self) -> bool:
        return self._muted

    def shutdown(self) -> None:
        logger.info("[AUDIO] Sistema de áudio desligado.")
        self._initialized = False
