"""Utilidades de texto puras (sin estado) reutilizadas por la capa de reescritura."""

from __future__ import annotations

import regex as re

_WORD_RE = re.compile(r"\p{L}[\p{L}\p{M}'’\-]*")


def match_case(original: str, replacement: str) -> str:
    """Aplica el patrón de mayúsculas de ``original`` a ``replacement``.

    - TODO MAYÚSCULAS  -> REEMPLAZO
    - Capitalizado     -> Reemplazo
    - resto            -> reemplazo (tal cual)
    """
    if original.isupper() and len(original) > 1:
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def tokenize_words(text: str) -> list[str]:
    """Lista de palabras (sin puntuación) para métricas léxicas."""
    return [m.group().lower() for m in _WORD_RE.finditer(text)]
