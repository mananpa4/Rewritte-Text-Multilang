"""Resumen extractivo offline y multilenguaje.

Selecciona las oraciones más informativas puntuándolas por la frecuencia de sus
palabras de contenido (TF normalizado) más un pequeño bono por posición. No
inventa texto: conserva oraciones originales en su orden. Es determinista.

Se usa en el modo ``summarized`` (y desde el checkbox "Resumir" de la app).
"""

from __future__ import annotations

import math
from collections import Counter

import regex as re

from rewrite_engine.lang.metadata import FUNCTION_WORDS

_SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+")
_WORD_RE = re.compile(r"\p{L}[\p{L}\p{M}'’\-]*")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text.strip()) if s.strip()]


def summarize(text: str, *, lang: str = "en", ratio: float = 0.5) -> str:
    """Devuelve un resumen extractivo de ``text``.

    ``ratio`` es la fracción de oraciones a conservar (0–1). Siempre conserva al
    menos una. Con 0–2 oraciones devuelve el texto tal cual (no hay nada que
    resumir).
    """
    sentences = _sentences(text)
    if len(sentences) <= 2:
        return text

    ratio = max(0.1, min(0.9, ratio))
    keep = max(1, round(len(sentences) * ratio))
    if keep >= len(sentences):
        return text

    stop = FUNCTION_WORDS.get(lang, frozenset())

    # Frecuencia de palabras de contenido en todo el documento.
    freq: Counter[str] = Counter()
    for sentence in sentences:
        for word in _WORD_RE.findall(sentence.lower()):
            if len(word) >= 4 and word not in stop:
                freq[word] += 1
    if not freq:
        return text
    top = max(freq.values())

    scored: list[tuple[float, int, str]] = []
    for idx, sentence in enumerate(sentences):
        words = [w for w in (t.lower() for t in _WORD_RE.findall(sentence)) if len(w) >= 4]
        if not words:
            score = 0.0
        else:
            score = sum(freq.get(w, 0) / top for w in words) / math.sqrt(len(words))
        # Pequeño bono a la primera oración (suele fijar el tema).
        if idx == 0:
            score *= 1.15
        scored.append((score, idx, sentence))

    # Elige las 'keep' mejores y las devuelve en su orden original.
    best = sorted(scored, key=lambda t: (t[0], -t[1]), reverse=True)[:keep]
    chosen = sorted(best, key=lambda t: t[1])
    return " ".join(sentence for _score, _idx, sentence in chosen)
