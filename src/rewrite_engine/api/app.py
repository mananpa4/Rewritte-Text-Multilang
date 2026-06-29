"""Servicio HTTP del motor de reescritura (FastAPI).

Expone ``POST /api/rewrite`` con el schema exacto del prompt (camelCase) y un
``GET /health``. Requiere el extra ``[api]``.

    uvicorn rewrite_engine.api.app:app --reload
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel, Field

from rewrite_engine.core.engine import RewriteEngine
from rewrite_engine.core.models import Mode, RewriteRequest

app = FastAPI(
    title="rewrite-engine",
    version="0.1.0",
    description="Reescritura inteligente, natural y multilenguaje (motor híbrido offline).",
)


@lru_cache(maxsize=1)
def get_engine() -> RewriteEngine:
    """Motor compartido (carga modelos/diccionarios una sola vez)."""
    return RewriteEngine()


class RewriteIn(BaseModel):
    """Cuerpo de la petición (schema del prompt, líneas 412-423)."""

    text: str
    language: str = "auto"
    mode: str = "natural"
    strength: float = 0.35
    preserveKeywords: list[str] = Field(default_factory=list)
    avoidWords: list[str] = Field(default_factory=list)
    returnAlternatives: int = 0
    locale: str | None = None


class ChangedWordOut(BaseModel):
    original: str
    replacement: str
    position: int


class RewriteOut(BaseModel):
    """Respuesta (schema del prompt, líneas 424-435)."""

    original: str
    rewritten: str
    alternatives: list[str]
    language: str
    mode: str
    similarityScore: float
    readabilityScore: float
    changedWords: list[ChangedWordOut]
    protectedTerms: list[str]
    warnings: list[str]


@app.get("/health")
def health() -> dict:
    engine = get_engine()
    return {
        "status": "ok",
        "version": "0.1.0",
        "embeddings": engine._scorer.uses_embeddings,
        "wordnet": engine._synonyms.has_lexical_source,
        "languages": list(engine._cfg.languages),
        "modes": [m.value for m in Mode],
    }


@app.post("/api/rewrite", response_model=RewriteOut)
def rewrite(body: RewriteIn) -> RewriteOut:
    engine = get_engine()
    result = engine.rewrite(
        RewriteRequest(
            text=body.text,
            language=body.language,
            mode=body.mode,
            strength=body.strength,
            preserve_keywords=body.preserveKeywords,
            avoid_words=body.avoidWords,
            return_alternatives=body.returnAlternatives,
            locale=body.locale,
        )
    )
    return RewriteOut(**result.to_dict())
