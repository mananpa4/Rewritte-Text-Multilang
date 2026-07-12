"""Tests del transformer opcional de IA (T5 paráfrasis, opt-in, sólo inglés).

Las guardas de seguridad compartidas se prueban en ``test_transformer_guards.py``.
La mayoría de estos tests son rápidos y no requieren descargar ningún modelo:
verifican la degradación elegante cuando ``transformers``/``torch`` no están
disponibles. El único test que carga un modelo real está marcado
``integration`` (se salta si falta la dependencia o si no hay red) y no se
ejecuta en la suite rápida (`pytest -m "not integration"`).
"""

from __future__ import annotations

import sys

import pytest

from rewrite_engine.core.engine import RewriteEngine
from rewrite_engine.core.models import Mode
from rewrite_engine.transformers.null import NullTransformer
from rewrite_engine.transformers.t5_paraphraser import T5ParaphraserTransformer


def test_degrada_sin_transformers_ni_torch(monkeypatch):
    """Sin las dependencias pesadas, available=False y refine es un no-op."""
    monkeypatch.setitem(sys.modules, "transformers", None)
    monkeypatch.setitem(sys.modules, "torch", None)

    transformer = T5ParaphraserTransformer()

    assert transformer.available is False
    assert transformer.load_error  # motivo capturado para mostrar al usuario
    # refine() no debe fallar ni intentar generar: devuelve el texto tal cual.
    text = "This is a test sentence."
    assert transformer.refine(text, language="en", mode=Mode.NATURAL) == text


def test_solo_aplica_a_ingles_cuando_no_hay_modelo_cargado(monkeypatch):
    """Aunque se pida otro idioma, sin modelo disponible es no-op seguro."""
    monkeypatch.setitem(sys.modules, "transformers", None)
    transformer = T5ParaphraserTransformer()
    text = "Este texto está en español."
    assert transformer.refine(text, language="es", mode=Mode.NATURAL) == text


def test_engine_hot_swap_transformer(monkeypatch):
    """set_transformer() cambia el backend sin recrear el motor."""
    from rewrite_engine.core.config import EngineConfig

    engine = RewriteEngine(
        config=EngineConfig(use_embeddings=False, use_spacy=False, use_grammar=False)
    )
    assert isinstance(engine.transformer, NullTransformer)

    monkeypatch.setitem(sys.modules, "transformers", None)
    ai = T5ParaphraserTransformer()  # available=False en este entorno de test
    engine.set_transformer(ai)
    assert engine.transformer is ai

    engine.set_transformer(None)
    assert isinstance(engine.transformer, NullTransformer)


@pytest.mark.integration
def test_paraphrase_real_ingles():
    """Carga el modelo real y parafrasea (requiere red + [ai-paraphrase])."""
    pytest.importorskip("transformers")
    pytest.importorskip("torch")

    transformer = T5ParaphraserTransformer()
    if not transformer.available:
        pytest.skip(f"Modelo no disponible: {transformer.load_error}")

    text = "The weather is very nice today."
    result = transformer.refine(text, language="en", mode=Mode.NATURAL)
    assert isinstance(result, str) and result.strip()

    # En otro idioma, sigue siendo no-op aunque el modelo esté cargado.
    es_text = "El clima está muy agradable hoy."
    assert transformer.refine(es_text, language="es", mode=Mode.NATURAL) == es_text
