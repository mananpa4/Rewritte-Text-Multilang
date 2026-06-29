"""Generador de candidatos de sustitución.

Decide qué palabras son elegibles para reescribirse (no función, no entidad, no
protegida, no en preserve/avoid) y produce los candidatos viables ordenados por
idoneidad, aplicando reglas de naturalidad (frecuencia mínima, no antónimos).
"""

from __future__ import annotations

from rewrite_engine.core.models import Candidate, Mode
from rewrite_engine.rewrite.constants import (
    FUNCTION_WORDS,
    INTENSIFIERS,
    MIN_WORD_LEN,
    NON_REPLACEABLE_POS,
)
from rewrite_engine.synonyms.engine import SynonymEngine

# Frecuencia mínima (0–1) para aceptar un sinónimo salvo en modo creativo.
# Evita palabras raras/arcaicas que suenan forzadas.
_MIN_FREQ = 0.12


def _is_derivational(a: str, b: str) -> bool:
    """True si ``a`` y ``b`` parecen formas derivadas o de la misma raíz.

    Captura tanto pares prefijo (product/production, cura/curar) como pares que
    comparten una raíz larga (prodotto/produzione, optimizar/optimización), que
    casi nunca son buenos sinónimos y suenan forzados.
    """
    if a == b:
        return True
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    if len(short) >= 3 and long.startswith(short) and len(long) - len(short) <= 4:
        return True
    # Raíz compartida larga (≥4 letras). Sólo se aplica a candidatos de WordNet
    # (los de diccionario están exentos), donde compartir raíz casi siempre
    # indica una forma derivada, no un sinónimo (prodotto/produzione).
    cp = _common_prefix_len(a, b)
    if cp >= 4 and abs(len(a) - len(b)) <= 6:
        return True
    return False


def _common_prefix_len(a: str, b: str) -> int:
    n = 0
    for ca, cb in zip(a, b):
        if ca != cb:
            break
        n += 1
    return n


class CandidateGenerator:
    """Produce sustituciones candidatas para palabras elegibles."""

    def __init__(self, synonyms: SynonymEngine, lemmatize) -> None:
        self._syn = synonyms
        self._lemmatize = lemmatize  # callable(word, lang) -> lemma

    def is_eligible(
        self,
        word: str,
        *,
        lang: str,
        pos: str = "",
        preserve: frozenset[str] = frozenset(),
        sentence_initial: bool = False,
    ) -> bool:
        """True si ``word`` puede considerarse para reemplazo."""
        lower = word.lower()
        if len(lower) < MIN_WORD_LEN:
            return False
        if lower in preserve:
            return False
        if pos and pos.upper() in NON_REPLACEABLE_POS:
            return False
        if lower in FUNCTION_WORDS.get(lang, frozenset()):
            return False
        if lower in INTENSIFIERS.get(lang, frozenset()):
            return False
        # Heurística de nombre propio sin POS: capitalizada a mitad de frase.
        if not pos and not sentence_initial and word[:1].isupper():
            return False
        return True

    def candidates(
        self,
        word: str,
        *,
        lang: str,
        pos: str = "",
        mode: Mode = Mode.NATURAL,
        avoid_words: frozenset[str] = frozenset(),
        creative: bool = False,
    ) -> list[Candidate]:
        """Candidatos ordenados (mejor primero) para ``word``."""
        lemma = self._lemmatize(word, lang)
        # Busca por lema Y por la forma de superficie: algunos lematizadores
        # (p.ej. simplemma en sueco: hjälp→hjälpa) devuelven un lema que no
        # coincide con la clave del diccionario; probar la palabra original lo
        # rescata. Se conserva el orden y se evitan duplicados por texto.
        forms = [lemma]
        if word.lower() != lemma:
            forms.append(word.lower())
        options = []
        seen_text: set[str] = set()
        for form in forms:
            for opt in self._syn.options(
                form, lang, pos=pos, mode=mode, avoid_words=avoid_words
            ):
                key = opt.text.lower()
                if key in seen_text:
                    continue
                seen_text.add(key)
                options.append(opt)
        out: list[Candidate] = []
        min_freq = 0.0 if creative else _MIN_FREQ
        for opt in options:
            if opt.text.lower() == word.lower():
                continue
            if opt.frequency < min_freq:
                continue
            # Descarta formas derivadas del mismo lema (p.ej. product/production,
            # cura/curar): una es prefijo de la otra. Casi nunca son buenos
            # sinónimos y suenan forzadas. No aplica a opciones de diccionario,
            # que son curadas.
            if opt.source != "dict" and _is_derivational(word.lower(), opt.text.lower()):
                continue
            out.append(
                Candidate(
                    original=word,
                    replacement=opt.text,
                    pos=pos,
                    score=opt.frequency,
                    source=opt.source,
                )
            )
        return out
