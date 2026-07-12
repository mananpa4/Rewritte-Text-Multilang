"""Tokenización y lematización.

Diseñado para ser *sin pérdida*: el texto se descompone en fragmentos
(palabra / token-protegido / resto) que, concatenados, reconstruyen el original
exacto. Esto permite reemplazar palabras conservando espacios y puntuación.

Lematización con spaCy si está disponible (mejor POS/NER), si no con simplemma,
y si tampoco, con la propia palabra en minúsculas. Todo degrada con gracia.
"""

from __future__ import annotations

from dataclasses import dataclass

import regex as re

from rewrite_engine.lang.esperanto import lemmatize_eo
from rewrite_engine.lang.metadata import (
    SEGMENTED_SCRIPT_LANGS,
    SPACY_MODELS,
    normalize_language_code,
)
from rewrite_engine.lang.morphology import MorphFeatures

# Fragmentos significativos: token protegido (atómico) o palabra (con acentos,
# apóstrofos y guiones internos). El resto (espacios, puntuación) son "huecos".
_CHUNK = re.compile(r"PROTECTEDTOKEN\d+X|\p{L}[\p{L}\p{M}'’\-]*")

# Para idiomas sin espacios claros, separamos primero las corridas de escritura
# CJK/Thai y luego las partimos en clusters Unicode. Es conservador pero sin
# pérdida; segmentadores reales pueden enchufarse más adelante.
_SEGMENTED_CHUNK = re.compile(
    r"PROTECTEDTOKEN\d+X|\p{Han}+|[\p{Hiragana}\p{Katakana}ー]+|\p{Thai}+|"
    r"\p{L}[\p{L}\p{M}'’\-]*"
)
_SCRIPT_RUN = re.compile(r"^(?:\p{Han}+|[\p{Hiragana}\p{Katakana}ー]+|\p{Thai}+)$")
_GRAPHEME = re.compile(r"\X")

# Separador de oraciones: corta tras . ! ? … capturando el espacio siguiente.
_SENT_SPLIT = re.compile(r"(?<=[.!?…])(\s+)")


@dataclass
class Span:
    """Un fragmento del texto. ``kind`` ∈ {"word", "prot", "other"}."""

    text: str
    kind: str


class TokenizerLemmatizer:
    """Tokeniza sin pérdida y lematiza por idioma."""

    def __init__(self, use_spacy: bool | None = None) -> None:
        self._want_spacy = use_spacy
        self._simplemma = self._load_simplemma()
        self._spacy_nlp: dict[str, object] = {}
        self._spacy_mod = self._load_spacy() if use_spacy is not False else None

    # -- carga perezosa de backends opcionales ------------------------------
    @staticmethod
    def _load_simplemma():
        try:
            import simplemma

            return simplemma
        except ImportError:
            return None

    @staticmethod
    def _load_spacy():
        try:
            import spacy

            return spacy
        except ImportError:
            return None

    def _nlp(self, lang: str):
        if self._spacy_mod is None:
            return None
        if lang in self._spacy_nlp:
            return self._spacy_nlp[lang]
        model = SPACY_MODELS.get(lang)
        nlp = None
        if model:
            try:
                nlp = self._spacy_mod.load(model, disable=["ner", "parser"])
            except Exception:
                nlp = None
        self._spacy_nlp[lang] = nlp
        return nlp

    # -- API ----------------------------------------------------------------
    def split_sentences(self, text: str) -> list[str]:
        """Divide en [oración, separador, oración, separador, ...] sin pérdida.

        Concatenar la lista reconstruye el texto original exacto. Los índices
        pares son oraciones; los impares, separadores de espacio.
        """
        parts = _SENT_SPLIT.split(text)
        # Normaliza a una lista alternada que empieza y acaba en "oración".
        return parts

    def spans(self, sentence: str, lang: str | None = None) -> list[Span]:
        """Descompone una oración en Spans sin pérdida."""
        result: list[Span] = []
        last = 0
        chunk_re = _SEGMENTED_CHUNK if self._uses_script_segmentation(lang) else _CHUNK
        for m in chunk_re.finditer(sentence):
            if m.start() > last:
                result.append(Span(sentence[last:m.start()], "other"))
            chunk = m.group()
            kind = "prot" if chunk.startswith("PROTECTEDTOKEN") else "word"
            if kind == "word" and _SCRIPT_RUN.fullmatch(chunk):
                result.extend(Span(part, "word") for part in self._segment_script_run(chunk))
            else:
                result.append(Span(chunk, kind))
            last = m.end()
        if last < len(sentence):
            result.append(Span(sentence[last:], "other"))
        return result

    @staticmethod
    def _uses_script_segmentation(lang: str | None) -> bool:
        return normalize_language_code(lang, default="") in SEGMENTED_SCRIPT_LANGS

    @staticmethod
    def _segment_script_run(text: str) -> list[str]:
        parts = _GRAPHEME.findall(text)
        return parts or [text]

    def lemmatize(self, word: str, lang: str) -> str:
        """Lema en minúsculas (o la palabra en minúsculas si no hay backend)."""
        lower = word.lower()
        if lang == "eo":
            # Esperanto es súper regular: lematizador por reglas propio
            # (simplemma/spaCy no lo cubren).
            return lemmatize_eo(lower)
        if self._simplemma is not None:
            try:
                return self._simplemma.lemmatize(lower, lang=lang)
            except Exception:
                return lower
        return lower

    def pos_of(self, sentence: str, lang: str) -> dict[str, str]:
        """Mapa palabra→UPOS usando spaCy si está; si no, vacío.

        Devuelve sólo la primera aparición de cada forma; suficiente para el
        filtrado heurístico (no reemplazar nombres propios, etc.).
        """
        return {word: info[0] for word, info in self.analyze(sentence, lang).items()}

    def analyze(self, sentence: str, lang: str) -> dict[str, tuple[str, MorphFeatures]]:
        """Mapa palabra→(UPOS, rasgos morfológicos) usando spaCy si está.

        Un único parseo de spaCy alimenta tanto el filtrado por POS
        (``CandidateGenerator``) como la concordancia morfológica del
        reemplazo (``lang/morphology.py``). Sin spaCy, devuelve vacío: el
        motor sigue funcionando, sólo sin esas dos mejoras.
        """
        nlp = self._nlp(lang)
        if nlp is None:
            return {}
        try:
            doc = nlp(sentence)
        except Exception:
            return {}
        info: dict[str, tuple[str, MorphFeatures]] = {}
        for tok in doc:
            info.setdefault(tok.text, (tok.pos_, MorphFeatures.from_dict(tok.morph.to_dict())))
        return info
