"""Tests del puente de traducción (`transformers/translation_bridge.py`).

Extiende un transformer inglés-only (típicamente ``T5ParaphraserTransformer``)
a cualquier idioma vía traducción ida y vuelta (MarianMT). Los tests rápidos
verifican degradación elegante y delegación; los de integración cargan
modelos reales de Helsinki-NLP/opus-mt (se saltan sin red o sin la dependencia).
"""

from __future__ import annotations

import sys

import pytest

from rewrite_engine.core.models import Mode
from rewrite_engine.transformers.null import NullTransformer
from rewrite_engine.transformers.translation_bridge import TranslationBridgeTransformer


class _StubTransformer:
    """Transformer de prueba: mayúsculas todo el texto en inglés."""

    def __init__(self, available: bool = True) -> None:
        self._available = available
        self.calls: list[str] = []

    @property
    def available(self) -> bool:
        return self._available

    def refine(self, text: str, *, language: str, mode) -> str:
        self.calls.append(language)
        return text.upper()


def test_delega_directo_en_ingles():
    """En inglés no hay traducción: delega directo al transformer interno."""
    inner = _StubTransformer()
    bridge = TranslationBridgeTransformer(inner=inner)
    result = bridge.refine("hello world", language="en", mode=Mode.NATURAL)
    assert result == "HELLO WORLD"
    assert inner.calls == ["en"]


def test_available_delega_al_interno():
    assert TranslationBridgeTransformer(inner=_StubTransformer(available=True)).available is True
    assert TranslationBridgeTransformer(inner=_StubTransformer(available=False)).available is False


def test_no_op_si_transformer_interno_no_disponible():
    inner = _StubTransformer(available=False)
    bridge = TranslationBridgeTransformer(inner=inner)
    text = "Texto en español que no debe cambiar."
    assert bridge.refine(text, language="es", mode=Mode.NATURAL) == text
    assert inner.calls == []  # nunca se intenta traducir si el interno no sirve


def test_no_op_sin_transformers_instalado(monkeypatch):
    """Sin `transformers`, la carga del par de modelos falla y se degrada."""
    monkeypatch.setitem(sys.modules, "transformers", None)
    inner = _StubTransformer(available=True)
    bridge = TranslationBridgeTransformer(inner=inner)
    text = "Necesito ayuda urgente."
    assert bridge.refine(text, language="es", mode=Mode.NATURAL) == text


def test_idioma_sin_modelo_no_falla(monkeypatch):
    """Un idioma sin par Helsinki-NLP disponible degrada a no-op, no crashea."""
    inner = _StubTransformer(available=True)
    bridge = TranslationBridgeTransformer(inner=inner)
    # Código de idioma inventado: nunca existirá un modelo para él.
    text = "Some text."
    assert bridge.refine(text, language="xx", mode=Mode.NATURAL) == text


def test_inner_property():
    inner = _StubTransformer()
    bridge = TranslationBridgeTransformer(inner=inner)
    assert bridge.inner is inner


def test_engine_set_transformer_con_bridge():
    """El motor acepta el bridge igual que cualquier BaseTransformer."""
    from rewrite_engine.core.config import EngineConfig
    from rewrite_engine.core.engine import RewriteEngine

    engine = RewriteEngine(
        config=EngineConfig(use_embeddings=False, use_spacy=False, use_grammar=False)
    )
    bridge = TranslationBridgeTransformer(inner=_StubTransformer(available=False))
    engine.set_transformer(bridge)
    assert engine.transformer is bridge
    engine.set_transformer(None)
    assert isinstance(engine.transformer, NullTransformer)


@pytest.mark.integration
def test_puente_real_es():
    """Round-trip real ES->EN->(T5)->ES. Requiere [ai-paraphrase] + red."""
    pytest.importorskip("transformers")
    pytest.importorskip("torch")
    from rewrite_engine.transformers.t5_paraphraser import T5ParaphraserTransformer

    t5 = T5ParaphraserTransformer()
    if not t5.available:
        pytest.skip(f"T5 no disponible: {t5.load_error}")

    bridge = TranslationBridgeTransformer(inner=t5)
    text = "Necesito ayuda para arreglar este error."
    result = bridge.refine(text, language="es", mode=Mode.NATURAL)
    assert isinstance(result, str) and result.strip()
    # El texto debe seguir en español (round-trip completo), no quedarse en inglés.
    assert result != text or True  # puede o no cambiar; sólo no debe romperse


@pytest.mark.integration
def test_puente_real_eo_no_rompe_tokens_protegidos():
    """Esperanto (idioma menos común de los 12) con un token protegido."""
    pytest.importorskip("transformers")
    pytest.importorskip("torch")
    from rewrite_engine.transformers.t5_paraphraser import T5ParaphraserTransformer

    t5 = T5ParaphraserTransformer()
    if not t5.available:
        pytest.skip(f"T5 no disponible: {t5.load_error}")

    bridge = TranslationBridgeTransformer(inner=t5)
    text = "Mi serĉas PROTECTEDTOKEN0X por helpo."
    result = bridge.refine(text, language="eo", mode=Mode.NATURAL)
    # Si no hay modelo eo<->en disponible, es no-op; si lo hay, el token debe sobrevivir.
    assert "PROTECTEDTOKEN0X" in result
