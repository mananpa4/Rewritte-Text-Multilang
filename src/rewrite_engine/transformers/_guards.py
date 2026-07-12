"""Guardas de seguridad compartidas por los transformers neuronales opcionales.

Cualquier backend generativo (T5, el puente de traducción, futuros) puede
producir un resultado peor que no cambiar nada: perder un token protegido,
truncar/alucinar longitud, o repetir una cláusula en bucle. Estas funciones son
la última línea de defensa antes de aceptar un candidato — están separadas de
cada transformer concreto para no duplicar la lógica.

Este módulo también resuelve, como *side effect* al importarse, un problema de
entorno ajeno a estos transformers (ver ``_disable_broken_torchvision``). Todo
transformer neuronal de este paquete importa algo de aquí, así que la defensa
siempre corre antes de que nadie importe ``transformers`` — sin depender del
orden en que ``rewrite_engine.transformers.__init__`` liste sus imports.
"""

from __future__ import annotations

import sys

import regex as re

_PROTECTED_RE = re.compile(r"PROTECTEDTOKEN\d+X")


def _disable_broken_torchvision() -> None:
    """Evita un crash de import ajeno a los transformers de texto de este paquete.

    Si ``torchvision`` está instalada pero es incompatible con la versión de
    ``torch`` presente (típico cuando conviven varios entornos en la misma
    máquina), ``transformers`` puede reventar con un ``RuntimeError`` de
    operadores C++ no registrados al intentar cargar su soporte de visión (que
    ninguno de nuestros transformers de texto usa).

    ``transformers`` decide si torchvision está disponible una sola vez, al
    importarse por primera vez (``is_torchvision_available()`` cachea un
    booleano de módulo) — por eso esta comprobación debe correr **antes** de
    que nada importe ``transformers``. Nunca reduce funcionalidad: sólo evita
    un fallo de arranque espurio ajeno a estos transformers.
    """
    if "torchvision" in sys.modules:
        return  # ya se resolvió (con éxito o bloqueada) en este proceso
    try:
        import torchvision  # noqa: F401  (dispara el posible RuntimeError)
    except Exception:
        sys.modules["torchvision"] = None


_disable_broken_torchvision()


def is_safe_candidate(original: str, candidate: str) -> bool:
    """Guardas mínimas antes de aceptar la salida de un modelo generativo.

    1. Los tokens protegidos deben sobrevivir exactamente igual: un modelo
       generativo puede omitirlos o corromperlos al no entender su semántica.
    2. La longitud no debe dispararse ni desplomarse (guarda anti alucinación /
       anti-truncamiento).
    3. Sin repetición degenerada (guarda anti "loop": un fallo real y
       observado en modelos T5 pequeños es repetir una cláusula, p.ej.
       "el perro salta sobre el zorro, que salta sobre el zorro").
    """
    if not candidate.strip():
        return False
    if sorted(_PROTECTED_RE.findall(original)) != sorted(_PROTECTED_RE.findall(candidate)):
        return False
    orig_len = len(original)
    if orig_len == 0:
        return True
    ratio = len(candidate) / orig_len
    if not (0.4 <= ratio <= 2.5):
        return False
    return not has_degenerate_repetition(candidate)


def has_degenerate_repetition(text: str) -> bool:
    """True si el texto repite bigramas hasta el punto de sonar en bucle."""
    words = text.lower().split()
    if len(words) < 6:
        return False
    bigrams = list(zip(words, words[1:]))
    distinct_ratio = len(set(bigrams)) / len(bigrams)
    return distinct_ratio < 0.75
