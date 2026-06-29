"""Reescritura a nivel de oración.

Recorre los fragmentos (spans) de una oración y sustituye una fracción de las
palabras elegibles, repartida de forma uniforme y *determinista* (sin azar, para
que los tests sean reproducibles). Preserva mayúsculas y todo el espaciado y la
puntuación originales, e ignora por completo los tokens protegidos.
"""

from __future__ import annotations

from rewrite_engine.core.models import ChangedWord, Mode
from rewrite_engine.lang.tokenizer import TokenizerLemmatizer
from rewrite_engine.rewrite.candidates import CandidateGenerator
from rewrite_engine.rewrite.textutils import match_case


class SentenceRewriter:
    """Reescribe oraciones reemplazando palabras por sinónimos idóneos."""

    def __init__(
        self,
        tokenizer: TokenizerLemmatizer,
        candidates: CandidateGenerator,
        max_change_ratio: float = 0.5,
    ) -> None:
        self._tok = tokenizer
        self._cand = candidates
        self._max_ratio = max_change_ratio

    def rewrite(
        self,
        sentence: str,
        *,
        lang: str,
        mode: Mode = Mode.NATURAL,
        strength: float = 0.35,
        preserve: frozenset[str] = frozenset(),
        avoid_words: frozenset[str] = frozenset(),
        word_offset: int = 0,
    ) -> tuple[str, list[ChangedWord]]:
        """Devuelve (oración_reescrita, cambios).

        ``word_offset`` es el índice global de la primera palabra de la oración,
        para que las posiciones de ChangedWord sean coherentes en todo el texto.
        """
        if mode == Mode.GRAMMAR_ONLY or strength <= 0:
            return sentence, []

        spans = self._tok.spans(sentence, lang=lang)
        pos_tags = self._tok.pos_of(sentence, lang)
        creative = mode == Mode.CREATIVE

        # Fracción objetivo de palabras a cambiar (mayor strength → más cambios).
        target = min(self._max_ratio, max(0.0, strength))

        changes: list[ChangedWord] = []
        accumulator = 0.0
        word_index = word_offset
        seen_word = False

        for span in spans:
            if span.kind != "word":
                continue
            current_word_index = word_index
            word_index += 1
            word = span.text
            sentence_initial = not seen_word
            seen_word = True

            pos = pos_tags.get(word, "")
            if not self._cand.is_eligible(
                word, lang=lang, pos=pos, preserve=preserve,
                sentence_initial=sentence_initial,
            ):
                continue

            # Reparto uniforme del presupuesto (dithering determinista).
            accumulator += target
            if accumulator < 1.0:
                continue

            cand_list = self._cand.candidates(
                word, lang=lang, pos=pos, mode=mode,
                avoid_words=avoid_words, creative=creative,
            )
            if not cand_list:
                continue

            replacement = match_case(word, cand_list[0].replacement)
            if replacement == word:
                continue

            span.text = replacement
            accumulator -= 1.0
            changes.append(
                ChangedWord(
                    original=word,
                    replacement=replacement,
                    position=current_word_index,
                )
            )

        rewritten = "".join(s.text for s in spans)
        return rewritten, changes

    @staticmethod
    def count_words(sentence: str, tokenizer: TokenizerLemmatizer, lang: str | None = None) -> int:
        return sum(1 for s in tokenizer.spans(sentence, lang=lang) if s.kind == "word")
