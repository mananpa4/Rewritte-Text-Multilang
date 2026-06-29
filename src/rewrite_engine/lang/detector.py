"""Detección de idioma.

Usa ``langdetect`` si está disponible (dependencia del núcleo) y degrada a una
heurística por palabras vacías si no lo está. Devuelve siempre un
:class:`LanguageGuess` con idioma + confianza, y permite forzar el idioma.
"""

from __future__ import annotations

from rewrite_engine.core.models import LanguageGuess
from rewrite_engine.lang.metadata import (
    STOPWORD_HINTS,
    normalize_language_code,
    normalize_language_list,
)


class LanguageDetector:
    """Detecta el idioma de un texto y normaliza al conjunto soportado."""

    def __init__(self, supported: tuple[str, ...], default: str = "en") -> None:
        self._supported = normalize_language_list(supported, fallback=(default or "en",))
        normalized_default = normalize_language_code(default, default=self._supported[0])
        self._default = (
            normalized_default
            if normalized_default in self._supported
            else self._supported[0]
        )
        self._impl = self._load_langdetect()

    @staticmethod
    def _load_langdetect():
        try:
            from langdetect import DetectorFactory, detect_langs

            DetectorFactory.seed = 0  # resultados deterministas
            return detect_langs
        except ImportError:
            return None

    def detect(self, text: str, *, force: str | None = None) -> LanguageGuess:
        """Devuelve el idioma detectado (o forzado) con su confianza."""
        if force and force != "auto":
            lang = self._normalize(force)
            return LanguageGuess(language=lang, confidence=1.0, forced=True)

        clean = text.strip()
        if not clean:
            return LanguageGuess(language=self._default, confidence=0.0)

        if self._impl is not None:
            try:
                results = self._impl(clean)
                if results:
                    best = results[0]
                    lang = self._normalize(best.lang)
                    return LanguageGuess(language=lang, confidence=float(best.prob))
            except Exception:
                pass  # cae al heurístico

        return self._heuristic(clean)

    def _heuristic(self, text: str) -> LanguageGuess:
        words = [w.strip(".,!?;:¡¿\"'()[]").lower() for w in text.split()]
        words = [w for w in words if w]
        if not words:
            return LanguageGuess(language=self._default, confidence=0.0)

        scores: dict[str, int] = {}
        for lang, hints in STOPWORD_HINTS.items():
            if lang not in self._supported:
                continue
            scores[lang] = sum(1 for w in words if w in hints)

        if not scores or max(scores.values()) == 0:
            return LanguageGuess(language=self._default, confidence=0.0)

        best_lang = max(scores, key=scores.get)
        confidence = min(0.99, scores[best_lang] / max(len(words), 1) * 3)
        return LanguageGuess(language=best_lang, confidence=round(confidence, 3))

    def _normalize(self, lang: str) -> str:
        base = normalize_language_code(lang, default=self._default)
        if base in self._supported:
            return base
        return self._default
