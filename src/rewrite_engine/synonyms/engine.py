"""Motor de sinónimos: combina fuentes y filtra por modo.

Orden de preferencia: diccionarios JSON (curados, con metadatos) y luego
WordNet/OMW como respaldo. Aplica el registro de formalidad y el contexto de
industria que pide cada modo de reescritura.
"""

from __future__ import annotations

from rewrite_engine.core.models import Mode
from rewrite_engine.synonyms.base import SynonymOption, SynonymSource

# Cada modo define el contexto de industria y los registros de formalidad
# aceptables/preferidos.
_MODE_PROFILE: dict[Mode, dict] = {
    Mode.NATURAL: {"context": None, "prefer": ("neutral",), "allow": ("neutral", "formal", "informal")},
    Mode.FORMAL: {"context": None, "prefer": ("formal",), "allow": ("formal", "neutral")},
    Mode.INFORMAL: {"context": None, "prefer": ("informal",), "allow": ("informal", "neutral")},
    Mode.PROFESSIONAL: {"context": "professional", "prefer": ("formal", "neutral"), "allow": ("formal", "neutral")},
    Mode.SEO: {"context": "seo", "prefer": ("neutral",), "allow": ("neutral", "formal", "informal")},
    Mode.MARKETPLACE: {"context": "marketplace", "prefer": ("neutral", "informal"), "allow": ("neutral", "informal", "formal")},
    Mode.TECHNICAL: {"context": "technical", "prefer": ("formal", "neutral"), "allow": ("formal", "neutral")},
    Mode.SIMPLE: {"context": None, "prefer": ("neutral", "informal"), "allow": ("neutral", "informal")},
    Mode.EXPANDED: {"context": None, "prefer": ("neutral",), "allow": ("neutral", "formal", "informal")},
    Mode.SUMMARIZED: {"context": None, "prefer": ("neutral",), "allow": ("neutral", "formal", "informal")},
    Mode.GRAMMAR_ONLY: {"context": None, "prefer": (), "allow": ()},  # no sustituye léxico
    Mode.CREATIVE: {"context": None, "prefer": ("neutral", "informal", "formal"), "allow": ("neutral", "informal", "formal")},
}


class SynonymEngine:
    """Devuelve opciones de sinónimo viables para una palabra dado un modo."""

    def __init__(self, sources: list[SynonymSource]) -> None:
        self._sources = sources

    @property
    def has_lexical_source(self) -> bool:
        return any(s.available for s in self._sources)

    def options(
        self,
        lemma: str,
        lang: str,
        *,
        pos: str = "",
        mode: Mode = Mode.NATURAL,
        avoid_words: frozenset[str] = frozenset(),
    ) -> list[SynonymOption]:
        """Opciones filtradas y ordenadas por idoneidad para el modo."""
        profile = _MODE_PROFILE.get(mode, _MODE_PROFILE[Mode.NATURAL])
        if not profile["allow"]:  # p.ej. grammar_only: no se sustituyen palabras
            return []

        context = profile["context"]
        allow = profile["allow"]
        prefer = profile["prefer"]

        merged: dict[str, SynonymOption] = {}
        for source in self._sources:
            if not source.available:
                continue
            for opt in source.synonyms(lemma, lang, pos):
                if opt.antonym:
                    continue
                key = opt.text.lower()
                if key == lemma.lower() or key in avoid_words:
                    continue
                # Filtro de contexto: descarta si el modo está vetado.
                if context and context in opt.avoid_contexts:
                    continue
                # Filtro de formalidad (solo si la opción declara una y no encaja).
                if opt.formality and opt.formality not in allow and opt.source == "dict":
                    continue
                # Conserva la mejor versión por texto (diccionario > wordnet).
                if key not in merged or (opt.source == "dict" and merged[key].source != "dict"):
                    merged[key] = opt

        options = list(merged.values())

        def rank(opt: SynonymOption) -> tuple:
            ctx_match = 1 if (context and context in opt.contexts) else 0
            formality_match = 1 if opt.formality in prefer else 0
            dict_first = 1 if opt.source == "dict" else 0
            return (dict_first, ctx_match, formality_match, opt.frequency)

        options.sort(key=rank, reverse=True)
        return options
