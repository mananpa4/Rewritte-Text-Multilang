"""Tests de las guardas de seguridad compartidas (`transformers/_guards.py`).

Usadas tanto por ``T5ParaphraserTransformer`` como por
``TranslationBridgeTransformer`` — probadas una sola vez aquí en vez de
duplicarlas por transformer.
"""

from __future__ import annotations

from rewrite_engine.transformers._guards import has_degenerate_repetition, is_safe_candidate


def test_guarda_tokens_protegidos():
    """La guarda descarta candidatos que no preservan los tokens protegidos."""
    original = "Visita PROTECTEDTOKEN0X ahora."
    candidate_sin_token = "Visita ahora mismo."  # perdió el token protegido
    assert is_safe_candidate(original, candidate_sin_token) is False

    candidate_con_token = "Ahora visita PROTECTEDTOKEN0X."
    assert is_safe_candidate(original, candidate_con_token) is True


def test_guarda_longitud():
    """La guarda descarta candidatos absurdamente cortos o largos."""
    original = "A reasonably normal sentence with several words in it."
    too_short = "Ok."
    too_long = original * 5
    assert is_safe_candidate(original, too_short) is False
    assert is_safe_candidate(original, too_long) is False
    assert is_safe_candidate(original, "A fairly similar sentence indeed.") is True


def test_guarda_repeticion_degenerada():
    """Regresión: caso real observado donde un T5 pequeño invierte el sentido
    repitiendo una cláusula en bucle (sujeto/objeto intercambiados)."""
    original = "The quick brown fox jumps over the lazy dog."
    degenerate = (
        "The lazy dog jumps over the quick brown fox, "
        "which jumps over the quick brown fox."
    )
    assert has_degenerate_repetition(degenerate) is True
    assert is_safe_candidate(original, degenerate) is False

    clean = "Our team is dedicated to delivering high quality results for every client."
    assert has_degenerate_repetition(clean) is False


def test_candidato_vacio_rechazado():
    assert is_safe_candidate("Algo de texto.", "") is False
    assert is_safe_candidate("Algo de texto.", "   ") is False
