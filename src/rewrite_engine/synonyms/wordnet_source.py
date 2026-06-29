"""Fuente de sinónimos basada en WordNet / Open Multilingual Wordnet (OMW).

Reimplementa la consulta a NLTK WordNet (API pública estándar). El uso de
WordNet multilenguaje vía OMW cubre es/en/pt/fr/it y más. Degrada con gracia si
NLTK o los corpora no están instalados.

La frecuencia se estima con ``wordfreq`` cuando está disponible para preferir
sinónimos más comunes (más naturales).
"""

from __future__ import annotations

from rewrite_engine.lang.metadata import WORDNET_LANGS
from rewrite_engine.synonyms.base import SynonymOption, SynonymSource

# UPOS -> constante POS de WordNet.
_UPOS_TO_WN = {
    "NOUN": "n",
    "PROPN": "n",
    "VERB": "v",
    "ADJ": "a",
    "ADV": "r",
}


class WordNetSource(SynonymSource):
    """Sinónimos desde NLTK WordNet + OMW."""

    def __init__(self, enabled: bool = True) -> None:
        self._wn = self._load(enabled)
        self._wordfreq = self._load_wordfreq()

    @staticmethod
    def _load(enabled: bool):
        if not enabled:
            return None
        try:
            from nltk.corpus import wordnet as wn

            # Fuerza la carga de los corpora; si faltan, intenta descargarlos.
            try:
                wn.synsets("test")
            except LookupError:
                import nltk

                nltk.download("wordnet", quiet=True)
                nltk.download("omw-1.4", quiet=True)
                wn.synsets("test")
            return wn
        except Exception:
            return None

    @staticmethod
    def _load_wordfreq():
        try:
            from wordfreq import zipf_frequency

            return zipf_frequency
        except ImportError:
            return None

    @property
    def available(self) -> bool:
        return self._wn is not None

    def _freq(self, word: str, lang: str) -> float:
        if self._wordfreq is None:
            return 0.5
        try:
            # Zipf 0–8 -> normalizado 0–1 (≈ dividir por 8).
            return max(0.0, min(1.0, self._wordfreq(word, lang) / 8.0))
        except Exception:
            return 0.5

    def synonyms(self, lemma: str, lang: str, pos: str = "") -> list[SynonymOption]:
        if self._wn is None:
            return []
        wn_lang = WORDNET_LANGS.get(lang)
        if wn_lang is None:
            return []

        pos_filter = _UPOS_TO_WN.get(pos.upper()) if pos else None
        seen: set[str] = set()
        options: list[SynonymOption] = []
        try:
            synsets = self._wn.synsets(lemma, lang=wn_lang)
        except Exception:
            return []

        # Sólo los primeros synsets: los más frecuentes/relevantes. Escanear
        # todos introduce sentidos marginales y ruido (mala WSD). Sin POS para
        # desambiguar somos aún más conservadores (sólo los 2 primeros sentidos).
        limit = 4 if pos_filter else 2
        for syn in synsets[:limit]:
            if pos_filter and syn.pos() not in (pos_filter, "s" if pos_filter == "a" else pos_filter):
                continue
            try:
                names = syn.lemma_names(wn_lang)
            except Exception:
                names = []
            for name in names:
                text = name.replace("_", " ").strip()
                key = text.lower()
                if not text or key == lemma.lower() or key in seen:
                    continue
                if len(text.split()) > 1:  # solo unigramas para reemplazo seguro
                    continue
                seen.add(key)
                options.append(
                    SynonymOption(
                        text=text,
                        formality="neutral",
                        frequency=self._freq(text, lang),
                        source="wordnet",
                    )
                )
        return options
