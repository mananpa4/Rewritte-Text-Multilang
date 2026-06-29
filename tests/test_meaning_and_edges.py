"""Tests de significado, diccionarios y casos límite (prompt: tests 5,14-18,20)."""

import pytest

from rewrite_engine import RewriteEngine, RewriteRequest
from rewrite_engine.core.config import EngineConfig


def test_mantiene_significado(rewrite):
    """Test 5: la similitud reportada se mantiene alta."""
    r = rewrite("Necesito ayuda para arreglar este error en mi web.", language="es", strength=0.4)
    assert r.similarity_score >= 0.5  # léxica; con embeddings sería mayor


def test_frase_tecnica_sensible_medica(rewrite):
    """Test 14: un claim médico no se reescribe; sólo se avisa."""
    r = rewrite("Este suplemento cura enfermedades.", language="es", strength=0.7)
    assert r.rewritten == r.original
    assert any("médic" in w.lower() for w in r.warnings)


def test_diccionario_personalizado(rewrite):
    """Test 15: los sinónimos de diccionario se aplican."""
    r = rewrite("Quiero comprar algo bueno.", language="es", mode="formal", strength=0.8)
    # 'bueno' -> excelente/estupendo/notable (diccionario)
    assert any(w in r.rewritten for w in ("excelente", "notable", "estupendo"))


def test_baja_similitud_se_rechaza(engine, monkeypatch):
    """Test 16: si la similitud cae bajo el umbral, se devuelve el original."""
    # Forzamos una similitud catastrófica para activar la puerta semántica.
    monkeypatch.setattr(engine._scorer, "similarity", lambda a, b: 0.0)
    r = engine.rewrite(
        RewriteRequest(text="Este producto es bueno y barato.", language="es", strength=0.8)
    )
    assert r.rewritten == r.original
    assert any("descartada" in w.lower() for w in r.warnings)


def test_texto_corto_sin_errores(rewrite):
    """Test 17: textos muy cortos no provocan errores."""
    for txt in ("", "Hola.", "ok", "Sí."):
        r = rewrite(txt, language="es", strength=0.5)
        assert isinstance(r.rewritten, str)


def test_texto_largo_se_divide_por_oraciones(rewrite):
    """Test 18: texto multi-oración; posiciones coherentes y crecientes."""
    texto = (
        "Este producto es bueno y barato. "
        "Necesito ayuda para arreglar el error. "
        "La guía es fácil de usar."
    )
    r = rewrite(texto, language="es", strength=0.6)
    positions = [c.position for c in r.changed_words]
    assert positions == sorted(positions)
    total_words = len(texto.split())
    assert all(0 <= p < total_words for p in positions)


def test_sin_mejora_devuelve_original_con_warning(rewrite):
    """Test 20: si no hay mejora posible, se devuelve el original con aviso."""
    # Texto sin palabras de contenido reemplazables (todo protegido/función).
    r = rewrite("Mananpa Labs y Shomex.", language="es", strength=0.9,
                preserve_keywords=["Mananpa Labs", "Shomex"])
    assert r.rewritten == r.original
    assert any("mejora" in w.lower() for w in r.warnings)


def test_alternativas_distintas(rewrite):
    r = rewrite("Necesito ayuda para arreglar este error en mi web.",
                language="es", mode="formal", strength=0.5, return_alternatives=2)
    assert len(r.alternatives) >= 1
    assert r.rewritten not in r.alternatives
    assert all(a != r.original for a in r.alternatives)


def test_degradacion_sin_dependencias_pesadas():
    """El motor funciona forzando la ausencia de embeddings/spaCy/gramática."""
    config = EngineConfig(use_embeddings=False, use_spacy=False, use_grammar=False)
    engine = RewriteEngine(config=config)
    assert engine._scorer.uses_embeddings is False
    r = engine.rewrite(RewriteRequest(text="Este producto es bueno.", language="es", strength=0.6))
    assert isinstance(r.rewritten, str) and r.rewritten


def test_to_dict_schema():
    """La salida JSON expone las claves camelCase del prompt."""
    config = EngineConfig(use_embeddings=False, use_spacy=False, use_grammar=False)
    engine = RewriteEngine(config=config)
    d = engine.rewrite(
        RewriteRequest(text="Este producto es bueno.", language="es", strength=0.5)
    ).to_dict()
    for key in (
        "original", "rewritten", "alternatives", "language", "similarityScore",
        "readabilityScore", "changedWords", "protectedTerms", "warnings",
    ):
        assert key in d
