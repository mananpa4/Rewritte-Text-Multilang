"""Interfaz común de fuentes de sinónimos."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SynonymOption:
    """Un sinónimo candidato con sus metadatos.

    formality ∈ {"formal", "neutral", "informal"}.
    frequency: 0–1 (mayor = más común).
    contexts / avoid_contexts: industrias o registros donde encaja o no.
    """

    text: str
    formality: str = "neutral"
    frequency: float = 0.5
    contexts: tuple[str, ...] = ()
    avoid_contexts: tuple[str, ...] = ()
    source: str = ""
    antonym: bool = False


@dataclass
class SourceResult:
    options: list[SynonymOption] = field(default_factory=list)


class SynonymSource(ABC):
    """Fuente de sinónimos para (lema, idioma, POS)."""

    @property
    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def synonyms(self, lemma: str, lang: str, pos: str = "") -> list[SynonymOption]:
        raise NotImplementedError
