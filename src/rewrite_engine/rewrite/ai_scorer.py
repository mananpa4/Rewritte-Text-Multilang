"""Scorer de "AI-likeness" multilenguaje (0–100, mayor = más artificial/IA).

Adaptado del scorer de 5 componentes de humanizer-workbench (MIT), pero
multilenguaje: las listas de palabras quemadas, intensificadores vacíos y
muletillas se cargan por idioma desde ``data/ai_markers/burned_words.json`` (con
un respaldo mínimo incrustado si el archivo no está).

Componentes (mismos pesos que el original):
  1. densidad de vocabulario IA      → 30
  2. densidad de muletillas           → 25
  3. uniformidad de longitud de frase → 20
  4. patrones estructurales           → 15
  5. aperturas formularias            → 10
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import regex as re

from rewrite_engine.rewrite.textutils import tokenize_words

_SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+")

# Respaldo mínimo si no hay archivo de datos.
_FALLBACK = {
    "universal": ["leverage", "utilize", "robust", "seamless", "holistic", "synergy"],
    "words": {"en": [], "es": []},
    "intensifiers": {"en": ["very", "really"], "es": ["muy", "realmente"]},
    "fillers": {"en": ["in conclusion"], "es": ["en conclusión"]},
}


class AIScorer:
    """Estima cuán "de IA" suena un texto, por idioma."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data = self._load(data_dir)

    @staticmethod
    def _load(data_dir: Path | None) -> dict:
        if data_dir is None:
            return _FALLBACK
        path = Path(data_dir) / "ai_markers" / "burned_words.json"
        if not path.exists():
            return _FALLBACK
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return _FALLBACK

    def _vocab(self, lang: str) -> frozenset[str]:
        universal = self._data.get("universal", [])
        words = self._data.get("words", {}).get(lang, [])
        intens = self._data.get("intensifiers", {}).get(lang, [])
        return frozenset(w.lower() for w in (*universal, *words, *intens))

    def _fillers(self, lang: str) -> tuple[str, ...]:
        return tuple(p.lower() for p in self._data.get("fillers", {}).get(lang, []))

    def score(self, text: str, lang: str) -> float:
        """AI-likeness 0–100 (mayor = más artificial)."""
        comp = self.components(text, lang)
        return round(min(100.0, sum(comp.values())), 1)

    def components(self, text: str, lang: str) -> dict[str, float]:
        words = tokenize_words(text)
        word_count = max(len(words), 1)
        sentences = [s for s in _SENT_SPLIT.split(text.strip()) if len(s.split()) >= 3]

        vocab = self._vocab(lang)
        ai_hits = sum(1 for w in words if w in vocab)
        vocab_score = min(30.0, (ai_hits / word_count) * 300)

        text_lower = text.lower()
        filler_hits = sum(1 for p in self._fillers(lang) if p in text_lower)
        filler_score = min(25.0, filler_hits * 5.0)

        if len(sentences) >= 3:
            variance = _stdev([len(s.split()) for s in sentences])
            uniformity = max(0.0, min(20.0, (10.0 - variance) * 2.0))
        else:
            uniformity = 5.0

        structural = 0.0
        structural += min(8.0, text.count("—") * 2.0)  # em dashes
        list_markers = len(re.findall(r"(?m)^\s*[-*•]\s+", text))
        structural += min(7.0, list_markers * 1.5)
        structural_score = min(15.0, structural)

        openers = self._fillers(lang)
        opener_hits = 0
        for s in sentences[:5]:
            sl = s.lower().strip()
            if any(sl.startswith(o) for o in openers):
                opener_hits += 1
        opener_score = min(10.0, opener_hits * 4.0)

        return {
            "vocabulary": round(vocab_score, 1),
            "fillers": round(filler_score, 1),
            "uniformity": round(uniformity, 1),
            "structural": round(structural_score, 1),
            "openers": round(opener_score, 1),
        }


def _stdev(values: list[int]) -> float:
    if len(values) < 2:
        return 10.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(var)
