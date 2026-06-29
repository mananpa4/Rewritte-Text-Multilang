"""Modelos de datos del núcleo.

Estas dataclasses forman el contrato entre las capas del motor. Mantenerlas en
un único módulo evita imports circulares y hace explícito el flujo de datos
(mismo patrón que humanizer-workbench/core/models.py).

Se usan dataclasses planas (no pydantic) para que el núcleo sea importable y
testeable sin dependencias del servidor; la capa API expone su propio schema.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Mode(StrEnum):
    """Modos de reescritura.

    Cada modo ajusta la selección de sinónimos (formalidad/contexto) y las
    reglas de reescritura por oración. Los marcados como "mejor con LLM"
    funcionan offline pero con resultados más limitados.
    """

    NATURAL = "natural"
    FORMAL = "formal"
    INFORMAL = "informal"
    PROFESSIONAL = "professional"
    SEO = "seo"
    MARKETPLACE = "marketplace"
    TECHNICAL = "technical"
    SIMPLE = "simple"
    EXPANDED = "expanded"        # mejor con LLM
    SUMMARIZED = "summarized"    # mejor con LLM
    GRAMMAR_ONLY = "grammar_only"
    CREATIVE = "creative"        # mejor con LLM

    @classmethod
    def coerce(cls, value: "Mode | str | None") -> "Mode":
        """Acepta un Mode, una cadena o None y devuelve siempre un Mode válido."""
        if isinstance(value, cls):
            return value
        if value is None:
            return cls.NATURAL
        try:
            return cls(str(value).strip().lower())
        except ValueError:
            return cls.NATURAL


# Modos que el motor offline no implementa plenamente (necesitan un LLM para
# dar buenos resultados). Se ejecutan igualmente pero emiten un warning.
LLM_PREFERRED_MODES: frozenset[Mode] = frozenset(
    {Mode.EXPANDED, Mode.SUMMARIZED, Mode.CREATIVE}
)


@dataclass(frozen=True)
class LanguageGuess:
    """Resultado del detector de idioma."""

    language: str            # código ISO-639-1: "es", "en", "pt"...
    confidence: float        # 0.0–1.0
    forced: bool = False     # True si el idioma fue impuesto por el usuario


@dataclass
class ProtectedTerm:
    """Una entidad protegida sustituida temporalmente por un token seguro."""

    token: str               # p.ej. "__PROTECTED_001__"
    original: str            # el texto exacto a restaurar
    kind: str                # "url" | "email" | "price" | "brand" | "html" ...


@dataclass
class Candidate:
    """Una sustitución candidata para una palabra."""

    original: str
    replacement: str
    pos: str = ""            # categoría gramatical (UPOS o "")
    score: float = 0.0       # puntuación combinada del ContextScorer
    source: str = ""         # "dict" | "wordnet" | ...


@dataclass
class ChangedWord:
    """Una palabra efectivamente modificada en la salida."""

    original: str
    replacement: str
    position: int            # índice de la palabra dentro del texto


@dataclass
class SentenceResult:
    """Resultado de reescribir una oración."""

    original: str
    rewritten: str
    changes: list[ChangedWord] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.original.strip() != self.rewritten.strip()


@dataclass
class RewriteRequest:
    """Petición de reescritura (espejo del schema del prompt, líneas 412-435).

    Atributos:
        text: texto original.
        language: "auto" para detectar, o un código ISO ("es", "en"...).
        mode: modo de reescritura (ver :class:`Mode`).
        strength: 0.1 mínimo … 0.9 muy creativo. Controla cuántas palabras se
            cambian y con qué agresividad.
        preserve_keywords: palabras/frases que nunca deben cambiarse.
        avoid_words: palabras que no deben aparecer en la salida.
        return_alternatives: nº de variantes alternativas a devolver.
        locale: variante regional, p.ej. "es-MX", "en-US".
    """

    text: str
    language: str = "auto"
    mode: Mode | str = Mode.NATURAL
    strength: float = 0.35
    preserve_keywords: list[str] = field(default_factory=list)
    avoid_words: list[str] = field(default_factory=list)
    return_alternatives: int = 0
    locale: str | None = None

    def normalized_mode(self) -> Mode:
        return Mode.coerce(self.mode)

    def clamped_strength(self) -> float:
        return max(0.0, min(1.0, float(self.strength)))


@dataclass
class RewriteResult:
    """Resultado de una reescritura (espejo del schema del prompt)."""

    original: str
    rewritten: str
    language: str
    alternatives: list[str] = field(default_factory=list)
    similarity_score: float = 1.0        # 0–1, semántica original vs reescrito
    readability_score: float = 0.0       # 0–1, heurística de legibilidad
    changed_words: list[ChangedWord] = field(default_factory=list)
    protected_terms: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    mode: Mode = Mode.NATURAL

    @property
    def changed_ratio(self) -> float:
        """Fracción de palabras modificadas respecto al original."""
        total = max(len(self.original.split()), 1)
        return len(self.changed_words) / total

    def to_dict(self) -> dict:
        """Forma JSON-serializable con las claves camelCase del prompt."""
        return {
            "original": self.original,
            "rewritten": self.rewritten,
            "alternatives": list(self.alternatives),
            "language": self.language,
            "mode": str(self.mode),
            "similarityScore": round(self.similarity_score, 4),
            "readabilityScore": round(self.readability_score, 4),
            "changedWords": [
                {"original": c.original, "replacement": c.replacement, "position": c.position}
                for c in self.changed_words
            ],
            "protectedTerms": list(self.protected_terms),
            "warnings": list(self.warnings),
        }
