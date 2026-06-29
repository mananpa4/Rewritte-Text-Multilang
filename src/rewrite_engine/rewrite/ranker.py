"""Ranking de salidas: elige la mejor variante y ordena las alternativas.

Cada variante se evalúa por (a) conservación de significado —como puerta—,
(b) legibilidad, (c) reducción de "AI-likeness" y (d) un nivel de cambio
cercano al objetivo (ni nulo ni excesivo). Devuelve las variantes que superan
la puerta semántica, ordenadas de mejor a peor.
"""

from __future__ import annotations

from dataclasses import dataclass

from rewrite_engine.core.models import ChangedWord
from rewrite_engine.rewrite.ai_scorer import AIScorer
from rewrite_engine.rewrite.scorer import ContextScorer


@dataclass
class Ranked:
    text: str
    changes: list[ChangedWord]
    protected: list[str]
    similarity: float
    readability: float
    ai_score: float
    total: float


class OutputRanker:
    """Ordena variantes de reescritura por calidad global."""

    def __init__(self, scorer: ContextScorer, ai_scorer: AIScorer) -> None:
        self._scorer = scorer
        self._ai = ai_scorer

    def rank(
        self,
        original: str,
        variants: list[tuple[str, list[ChangedWord], list[str]]],
        *,
        lang: str,
        target_ratio: float,
        similarity_floor: float,
    ) -> list[Ranked]:
        original_ai = self._ai.score(original, lang)
        original_words = max(len(original.split()), 1)

        ranked: list[Ranked] = []
        seen: set[str] = set()
        for text, changes, protected in variants:
            key = text.strip()
            if key in seen:
                continue
            seen.add(key)

            similarity = self._scorer.similarity(original, text)
            # Puerta semántica: descarta variantes que cambian el significado.
            if key != original.strip() and similarity < similarity_floor:
                continue

            readability = self._scorer.readability(text)
            ai_score = self._ai.score(text, lang)
            ai_reduction = max(0.0, (original_ai - ai_score) / 100.0)

            ratio = len(changes) / original_words
            # Recompensa acercarse al objetivo de cambio (campana triangular).
            denom = max(target_ratio, 0.1)
            changedness = max(0.0, 1.0 - abs(ratio - target_ratio) / denom)

            total = (
                0.45 * readability
                + 0.30 * ai_reduction
                + 0.20 * changedness
                + 0.05 * similarity  # desempate: prefiere conservar significado
            )
            ranked.append(
                Ranked(
                    text=text,
                    changes=changes,
                    protected=protected,
                    similarity=round(similarity, 4),
                    readability=round(readability, 4),
                    ai_score=ai_score,
                    total=round(total, 5),
                )
            )

        ranked.sort(key=lambda r: r.total, reverse=True)
        return ranked
