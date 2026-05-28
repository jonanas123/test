"""
HMI - Módulo de Captura de Entrada.

Responsável por capturar e validar entradas do usuário
no terminal, roteando comandos para o sistema.
"""

import logging

logger = logging.getLogger(__name__)


class InputHandler:
    """Captura e valida entradas do usuário via terminal."""

    @staticmethod
    def get_menu_choice(prompt: str = "Escolha uma opção: ", valid: set[str] | None = None) -> str:
        """Captura a escolha de menu do usuário."""
        try:
            choice = input(f"\n  {prompt}").strip()
        except (EOFError, KeyboardInterrupt):
            return "0"

        if valid and choice not in valid:
            logger.warning("[INPUT] Opção inválida: '%s'", choice)
            print("  ⚠ Opção inválida. Tente novamente.")
            return ""

        return choice

    @staticmethod
    def get_text_input(prompt: str = "Digite: ") -> str:
        """Captura entrada de texto livre do usuário."""
        try:
            return input(f"\n  {prompt}").strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    @staticmethod
    def get_numeric_input(prompt: str = "Digite um número: ") -> int | None:
        """Captura entrada numérica do usuário."""
        try:
            text = input(f"\n  {prompt}").strip()
            return int(text)
        except (EOFError, KeyboardInterrupt):
            return None
        except ValueError:
            print("  ⚠ Entrada inválida. Digite um número.")
            return None

    @staticmethod
    def confirm(prompt: str = "Confirmar? (s/n): ") -> bool:
        """Solicita confirmação do usuário."""
        try:
            choice = input(f"\n  {prompt}").strip().lower()
            return choice in ("s", "sim", "y", "yes")
        except (EOFError, KeyboardInterrupt):
            return False
