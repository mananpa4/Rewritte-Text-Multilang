"""Fixtures compartidas.

El motor de los tests se fuerza a modo offline determinista (sin embeddings,
spaCy ni LanguageTool) para que los resultados sean reproducibles aunque esas
dependencias opcionales estén instaladas. WordNet se usa si está disponible.
"""

import pytest

from rewrite_engine import RewriteEngine, RewriteRequest
from rewrite_engine.core.config import EngineConfig


@pytest.fixture(scope="session")
def engine() -> RewriteEngine:
    config = EngineConfig(
        use_embeddings=False,
        use_spacy=False,
        use_grammar=False,
    )
    return RewriteEngine(config=config)


@pytest.fixture
def rewrite(engine):
    def _rewrite(text, **kwargs):
        return engine.rewrite(RewriteRequest(text=text, **kwargs))

    return _rewrite
