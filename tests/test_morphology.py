"""Tests de concordancia morfológica (`lang/morphology.py`).

Los tests de reglas puras son rápidos (no requieren spaCy: construyen
``MorphFeatures`` a mano). Los tests de integración verifican el
comportamiento end-to-end con spaCy real y están marcados ``integration``
(se saltan si falta el modelo del idioma).
"""

from __future__ import annotations

import pytest

from rewrite_engine.lang.morphology import MorphFeatures, reinflect


# -- reglas puras: adjetivos (género + número) ---------------------------


def test_adjetivo_genero_femenino_es():
    assert reinflect("bonita", "hermoso", "ADJ", MorphFeatures(gender="Fem"), "es") == "hermosa"


def test_adjetivo_genero_masculino_es():
    assert reinflect("bonito", "hermosa", "ADJ", MorphFeatures(gender="Masc"), "es") == "hermoso"


def test_adjetivo_plural_es():
    assert reinflect("", "económico", "ADJ", MorphFeatures(number="Plur"), "es") == "económicos"
    assert reinflect("", "fácil", "ADJ", MorphFeatures(number="Plur"), "es") == "fáciles"


def test_adjetivo_genero_y_plural_combinados_es():
    features = MorphFeatures(gender="Fem", number="Plur")
    assert reinflect("bonitas", "hermoso", "ADJ", features, "es") == "hermosas"


def test_adjetivo_no_cambia_terminaciones_invariantes_es():
    # "grande" no varía por género (misma forma masc/fem).
    assert reinflect("grande", "grande", "ADJ", MorphFeatures(gender="Fem"), "es") == "grande"


def test_adjetivo_femenino_it():
    assert reinflect("bella", "ottimo", "ADJ", MorphFeatures(gender="Fem"), "it") == "ottima"


def test_adjetivo_femenino_fr():
    assert reinflect("grande", "important", "ADJ", MorphFeatures(gender="Fem"), "fr") == "importante"


def test_adjetivo_plural_it():
    assert reinflect("", "rapido", "ADJ", MorphFeatures(number="Plur"), "it") == "rapidi"
    assert reinflect("", "veloce", "ADJ", MorphFeatures(number="Plur"), "it") == "veloci"


def test_adjetivo_plural_fr():
    assert reinflect("", "rapide", "ADJ", MorphFeatures(number="Plur"), "fr") == "rapides"


# -- reglas puras: sustantivos (SÓLO número, nunca género) ----------------


def test_sustantivo_no_cambia_genero():
    """Regresión: 'ayuda'(fem) -> 'apoyo'(masc) NO debe forzarse a 'apoya'.

    El género de un sustantivo es una propiedad léxica fija, no algo que deba
    concordar con nada; dos sustantivos sinónimos pueden tener géneros
    distintos legítimamente.
    """
    result = reinflect("ayuda", "apoyo", "NOUN", MorphFeatures(gender="Fem", number="Sing"), "es")
    assert result == "apoyo"


def test_sustantivo_si_cambia_numero():
    assert reinflect("errores", "fallo", "NOUN", MorphFeatures(number="Plur"), "es") == "fallos"


# -- reglas puras: verbos (sólo presente indicativo 3ª persona) -----------


def test_verbo_presente_3sg_es():
    features = MorphFeatures(tense="Pres", mood="Ind", person="3", number="Sing")
    assert reinflect("transforma", "cambiar", "VERB", features, "es") == "cambia"


def test_verbo_presente_3pl_es():
    features = MorphFeatures(tense="Pres", mood="Ind", person="3", number="Plur")
    assert reinflect("", "mejorar", "VERB", features, "es") == "mejoran"


def test_verbo_presente_3sg_fr():
    features = MorphFeatures(tense="Pres", mood="Ind", person="3", number="Sing")
    assert reinflect("", "améliorer", "VERB", features, "fr") == "améliore"


def test_verbo_fuera_de_alcance_seguro_no_se_toca():
    """Fuera de presente-indicativo-3ª (pasado, subjuntivo, 1ª/2ª persona):
    se deja el reemplazo tal cual en vez de arriesgar una conjugación
    incorrecta (verbos irregulares con cambio de raíz, p.ej. poder->puede)."""
    past = MorphFeatures(tense="Past", mood="Ind", person="3", number="Sing")
    assert reinflect("mejoró", "optimizar", "VERB", past, "es") == "optimizar"

    first_person = MorphFeatures(tense="Pres", mood="Ind", person="1", number="Sing")
    assert reinflect("mejoro", "optimizar", "VERB", first_person, "es") == "optimizar"


def test_verbo_reemplazo_no_reconocible_no_se_toca():
    """Si el reemplazo no termina en una terminación de infinitivo reconocida
    (p.ej. ya viene de WordNet en otra forma), no se fuerza nada."""
    features = MorphFeatures(tense="Pres", mood="Ind", person="3", number="Sing")
    assert reinflect("", "algo_raro", "VERB", features, "es") == "algo_raro"


# -- inglés: sin género; plural + conjugación mínima ----------------------


def test_ingles_plural_sustantivo():
    assert reinflect("problems", "issue", "NOUN", MorphFeatures(number="Plur"), "en") == "issues"
    assert reinflect("boxes", "case", "NOUN", MorphFeatures(number="Plur"), "en") == "cases"


def test_ingles_verbo_pasado():
    assert reinflect("fixed", "resolve", "VERB", MorphFeatures(tense="Past"), "en") == "resolved"
    assert reinflect("used", "employ", "VERB", MorphFeatures(tense="Past"), "en") == "employed"


def test_ingles_verbo_presente_3sg():
    features = MorphFeatures(tense="Pres", person="3", number="Sing")
    assert reinflect("fixes", "resolve", "VERB", features, "en") == "resolves"
    assert reinflect("watches", "observe", "VERB", features, "en") == "observes"


# -- alemán: extracción sí, reflexión no (declinación demasiado compleja) --


def test_aleman_no_reflexiona():
    features = MorphFeatures(gender="Fem", number="Plur")
    assert reinflect("gute", "ausgezeichnet", "ADJ", features, "de") == "ausgezeichnet"


# -- casos base ------------------------------------------------------------


def test_sin_rasgos_no_hace_nada():
    assert reinflect("word", "replacement", "ADJ", MorphFeatures(), "es") == "replacement"


def test_reemplazo_vacio_no_falla():
    assert reinflect("word", "", "ADJ", MorphFeatures(gender="Fem"), "es") == ""


# -- integración: motor real con spaCy (requiere [spacy] + modelos) -------


@pytest.mark.integration
def test_concordancia_real_es():
    pytest.importorskip("spacy")
    from rewrite_engine import RewriteEngine, RewriteRequest
    from rewrite_engine.core.config import EngineConfig

    engine = RewriteEngine(
        config=EngineConfig(use_embeddings=False, use_spacy=True, use_grammar=False)
    )
    if not engine._tokenizer._nlp("es"):
        pytest.skip("Modelo es_core_news_sm no instalado")

    r = engine.rewrite(
        RewriteRequest(text="La casa es muy bonita y grande.", language="es", strength=0.9)
    )
    assert "hermosa" in r.rewritten  # no "hermoso" (regresión de género)

    r2 = engine.rewrite(
        RewriteRequest(
            text="Este error se transforma en un problema serio.", language="es", strength=0.9
        )
    )
    assert "cambia" in r2.rewritten  # conjugado, no el infinitivo "cambiar"

    r3 = engine.rewrite(
        RewriteRequest(text="Ella necesita ayuda urgente.", language="es", mode="formal", strength=0.9)
    )
    assert "apoya" not in r3.rewritten.split()  # regresión: no verbizar el sustantivo


@pytest.mark.integration
def test_concordancia_real_en():
    pytest.importorskip("spacy")
    from rewrite_engine import RewriteEngine, RewriteRequest
    from rewrite_engine.core.config import EngineConfig

    engine = RewriteEngine(
        config=EngineConfig(use_embeddings=False, use_spacy=True, use_grammar=False)
    )
    if not engine._tokenizer._nlp("en"):
        pytest.skip("Modelo en_core_web_sm no instalado")

    r = engine.rewrite(
        RewriteRequest(text="The problems are important.", language="en", strength=0.9)
    )
    assert isinstance(r.rewritten, str) and r.rewritten
