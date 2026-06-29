"""rewrite_engine — Reescritura inteligente, natural y multilenguaje.

Motor híbrido offline (diccionarios + WordNet/OMW + NLP) con interfaz lista
para enchufar un LLM. El punto de entrada principal es :class:`RewriteEngine`.

    from rewrite_engine import RewriteEngine, RewriteRequest

    engine = RewriteEngine()
    result = engine.rewrite(RewriteRequest(text="...", language="auto", mode="natural"))
    print(result.rewritten)
"""

from rewrite_engine.core.engine import RewriteEngine
from rewrite_engine.core.models import (
    Candidate,
    ChangedWord,
    LanguageGuess,
    Mode,
    ProtectedTerm,
    RewriteRequest,
    RewriteResult,
    SentenceResult,
)

__version__ = "0.1.0"

__all__ = [
    "RewriteEngine",
    "RewriteRequest",
    "RewriteResult",
    "Mode",
    "Candidate",
    "ChangedWord",
    "LanguageGuess",
    "ProtectedTerm",
    "SentenceResult",
    "__version__",
]
