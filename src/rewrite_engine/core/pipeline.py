"""Configuración de etapas del motor según el modo y los recursos disponibles.

Mantiene explícito qué pasos se ejecutan en una reescritura. La lógica vive en
el ``RewriteEngine``; esto sólo decide la secuencia (mismo espíritu que
humanizer-workbench/core/pipeline.py).
"""

from __future__ import annotations

from dataclasses import dataclass

from rewrite_engine.core.models import Mode


@dataclass(frozen=True)
class Pipeline:
    """Etapas activas para una reescritura concreta."""

    lexical_rewrite: bool   # sustitución por sinónimos
    transformer_refine: bool  # refinado por IA (si hay backend disponible)
    grammar_fix: bool       # corrección gramatical (si hay LanguageTool)

    @classmethod
    def build(
        cls,
        mode: Mode,
        *,
        has_transformer: bool,
        has_grammar: bool,
    ) -> "Pipeline":
        return cls(
            lexical_rewrite=mode != Mode.GRAMMAR_ONLY,
            transformer_refine=has_transformer,
            grammar_fix=has_grammar,
        )

    @property
    def stage_names(self) -> tuple[str, ...]:
        names = []
        if self.lexical_rewrite:
            names.append("lexical_rewrite")
        if self.transformer_refine:
            names.append("transformer_refine")
        if self.grammar_fix:
            names.append("grammar_fix")
        return tuple(names)
