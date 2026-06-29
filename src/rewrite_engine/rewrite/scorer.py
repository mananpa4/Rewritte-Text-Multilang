"""Puntuación de contexto: validación semántica y legibilidad.

La similitud semántica usa embeddings multilenguaje
(``sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2``) si la
dependencia opcional está instalada; si no, degrada a una similitud léxica
robusta (solapamiento de unigramas + bigramas, estilo Jaccard) que no requiere
modelos. Así el motor valida significado incluso 100% offline y ligero.
"""

from __future__ import annotations

import math

from rewrite_engine.rewrite.textutils import tokenize_words

_EMB_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class ContextScorer:
    """Mide cuánto se conserva el significado y la legibilidad del texto."""

    def __init__(self, use_embeddings: bool | None = None) -> None:
        self._model = None
        if use_embeddings is not False:
            self._model = self._load_model()
        self._wants_embeddings = use_embeddings

    @staticmethod
    def _load_model():
        try:
            from sentence_transformers import SentenceTransformer

            return SentenceTransformer(_EMB_MODEL)
        except Exception:
            return None

    @property
    def uses_embeddings(self) -> bool:
        return self._model is not None

    # -- similitud semántica ------------------------------------------------
    def similarity(self, a: str, b: str) -> float:
        """Similitud semántica 0–1 entre dos textos."""
        if a.strip() == b.strip():
            return 1.0
        if self._model is not None:
            sim = self._embedding_similarity(a, b)
            if sim is not None:
                return sim
        return self._lexical_similarity(a, b)

    def _embedding_similarity(self, a: str, b: str) -> float | None:
        try:
            emb = self._model.encode([a, b], normalize_embeddings=True)
            cos = float((emb[0] * emb[1]).sum())
            # coseno [-1,1] -> [0,1]
            return max(0.0, min(1.0, (cos + 1.0) / 2.0))
        except Exception:
            return None

    @staticmethod
    def _lexical_similarity(a: str, b: str) -> float:
        """Solapamiento de unigramas y bigramas (media), 0–1."""
        wa, wb = tokenize_words(a), tokenize_words(b)
        if not wa and not wb:
            return 1.0
        uni = _jaccard(set(wa), set(wb))
        bi = _jaccard(_bigrams(wa), _bigrams(wb))
        # Pondera más unigramas; los bigramas captan reordenamientos.
        return round(0.6 * uni + 0.4 * bi, 4)

    # -- legibilidad --------------------------------------------------------
    @staticmethod
    def readability(text: str) -> float:
        """Heurística de legibilidad 0–1 (mayor = más legible).

        Penaliza frases largas y palabras largas (proxy multilenguaje del estilo
        Flesch sin depender del idioma).
        """
        words = tokenize_words(text)
        if not words:
            return 0.0
        sentences = max(text.count(".") + text.count("!") + text.count("?"), 1)
        words_per_sentence = len(words) / sentences
        avg_word_len = sum(len(w) for w in words) / len(words)
        # Curva suave: frase ideal ~15 palabras, palabra ideal ~5 letras.
        sent_penalty = _bell(words_per_sentence, center=15, spread=12)
        word_penalty = _bell(avg_word_len, center=5, spread=4)
        return round(0.5 * sent_penalty + 0.5 * word_penalty, 4)


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _bigrams(words: list[str]) -> set:
    return {(words[i], words[i + 1]) for i in range(len(words) - 1)}


def _bell(value: float, *, center: float, spread: float) -> float:
    """Campana gaussiana normalizada a 0–1, máximo en ``center``."""
    return math.exp(-((value - center) ** 2) / (2 * spread**2))
