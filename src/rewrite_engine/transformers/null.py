"""Transformer identidad: el motor 100% offline por defecto.

No hace ninguna llamada externa; devuelve el texto tal cual. Permite que el
``RewriteEngine`` tenga siempre un transformer válido sin requerir IA.
"""

from __future__ import annotations

from rewrite_engine.core.models import Mode
from rewrite_engine.transformers.base import BaseTransformer


class NullTransformer(BaseTransformer):
    """No-op. Devuelve el texto de entrada sin cambios."""

    @property
    def available(self) -> bool:
        return False

    def refine(self, text: str, *, language: str, mode: Mode) -> str:
        return text
