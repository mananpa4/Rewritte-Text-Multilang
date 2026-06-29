"""Constantes lingüísticas compartidas por la capa de reescritura."""

from __future__ import annotations

from rewrite_engine.lang.metadata import FUNCTION_WORDS, INTENSIFIERS

# UPOS que nunca se reemplazan (función gramatical o entidad).
NON_REPLACEABLE_POS: frozenset[str] = frozenset(
    {"PROPN", "DET", "ADP", "PRON", "CCONJ", "SCONJ", "AUX", "PART", "NUM", "SYM", "PUNCT", "X"}
)

# Longitud mínima de palabra a considerar para reemplazo.
MIN_WORD_LEN = 3
