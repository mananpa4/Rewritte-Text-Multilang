"""Corrector ortográfico offline para la app de escritorio.

Dos motores, para dar cobertura pareja a todos los idiomas del proyecto:

1. ``pyspellchecker`` (mejor: detección + sugerencias por edición) para los
   idiomas que trae: en, es, fr, pt, de, ru, nl (+ ar, eu, lv).
2. Respaldo con ``wordfreq``: una palabra es "desconocida" si su frecuencia es
   cero en el idioma; las sugerencias se sacan por similitud (difflib) contra la
   lista de palabras más frecuentes. Cubre it, pl, uk, sv y el resto que
   ``wordfreq`` soporte.

Así los 11 idiomas naturales tienen corrector. Esperanto (eo) no está en
ninguno de los dos → el corrector queda inactivo (degrada, no falla).
"""

from __future__ import annotations

import difflib

# Idiomas con diccionario propio de pyspellchecker.
_PYSPELL_LANGS = frozenset({"en", "es", "fr", "pt", "de", "ru", "ar", "eu", "lv", "nl"})
# Cuántas palabras frecuentes usar como vocabulario del respaldo wordfreq.
_WF_VOCAB_SIZE = 40000


class SpellService:
    """Corrector con dos motores y degradación elegante."""

    def __init__(self) -> None:
        self._pyspell = self._load_pyspell()
        self._wf = self._load_wordfreq()
        self._checkers: dict[str, object] = {}
        self._wf_vocab: dict[str, list[str]] = {}
        self._wf_vocab_set: dict[str, frozenset[str]] = {}

    # -- carga de motores ---------------------------------------------------
    @staticmethod
    def _load_pyspell():
        try:
            import spellchecker

            return spellchecker
        except ImportError:
            return None

    @staticmethod
    def _load_wordfreq():
        try:
            from wordfreq import available_languages, top_n_list, zipf_frequency

            return {
                "available": set(available_languages()),
                "top_n_list": top_n_list,
                "zipf": zipf_frequency,
            }
        except Exception:
            return None

    @property
    def available(self) -> bool:
        return self._pyspell is not None or self._wf is not None

    def supports(self, lang: str) -> bool:
        if self._pyspell is not None and lang in _PYSPELL_LANGS:
            return True
        return self._wf is not None and lang in self._wf["available"]

    # -- motor 1: pyspellchecker -------------------------------------------
    def _checker(self, lang: str):
        if self._pyspell is None or lang not in _PYSPELL_LANGS:
            return None
        if lang not in self._checkers:
            try:
                self._checkers[lang] = self._pyspell.SpellChecker(language=lang)
            except Exception:
                self._checkers[lang] = None
        return self._checkers[lang]

    # -- motor 2: respaldo con wordfreq ------------------------------------
    def _wf_ready(self, lang: str) -> bool:
        return self._wf is not None and lang in self._wf["available"]

    def _wf_vocabulary(self, lang: str) -> tuple[list[str], frozenset[str]]:
        if lang not in self._wf_vocab:
            try:
                words = self._wf["top_n_list"](lang, _WF_VOCAB_SIZE)
            except Exception:
                words = []
            self._wf_vocab[lang] = words
            self._wf_vocab_set[lang] = frozenset(words)
        return self._wf_vocab[lang], self._wf_vocab_set[lang]

    # -- API ----------------------------------------------------------------
    def unknown(self, words: list[str], lang: str) -> set[str]:
        """Subconjunto de ``words`` (en minúsculas) no reconocidas."""
        checker = self._checker(lang)
        if checker is not None:
            try:
                return set(checker.unknown(words))
            except Exception:
                pass
        if self._wf_ready(lang):
            zipf = self._wf["zipf"]
            _, vocab = self._wf_vocabulary(lang)
            out = set()
            for w in words:
                if w in vocab:
                    continue
                try:
                    if zipf(w, lang) <= 0.0:
                        out.add(w)
                except Exception:
                    pass
            return out
        return set()

    def suggestions(self, word: str, lang: str, limit: int = 7) -> list[str]:
        """Correcciones candidatas para ``word`` (mejor primero)."""
        checker = self._checker(lang)
        if checker is not None:
            try:
                cands = [c for c in (checker.candidates(word) or set()) if c != word]
                cands.sort(key=lambda c: checker.word_usage_frequency(c), reverse=True)
                return cands[:limit]
            except Exception:
                pass
        if self._wf_ready(lang):
            vocab, _ = self._wf_vocabulary(lang)
            # Palabras frecuentes más parecidas ortográficamente.
            return difflib.get_close_matches(word, vocab, n=limit, cutoff=0.72)
        return []
