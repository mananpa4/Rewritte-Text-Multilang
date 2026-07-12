"""Capa de transformación opcional (el "gancho" para enchufar un LLM).

El motor offline usa :class:`NullTransformer` por defecto (mismo comportamiento
para los 12 idiomas). :class:`T5ParaphraserTransformer` añade una etapa de
parafraseo neuronal opt-in con un modelo T5 ligero de HuggingFace — sólo para
inglés (requiere el extra ``[ai-paraphrase]``; degrada con gracia si falta).
:class:`TranslationBridgeTransformer` envuelve cualquier transformer
inglés-only (como el T5 anterior) y lo extiende a los 12 idiomas traduciendo
ida y vuelta con MarianMT.
"""

from rewrite_engine.transformers.base import BaseTransformer
from rewrite_engine.transformers.null import NullTransformer
from rewrite_engine.transformers.t5_paraphraser import T5ParaphraserTransformer
from rewrite_engine.transformers.translation_bridge import TranslationBridgeTransformer

__all__ = [
    "BaseTransformer",
    "NullTransformer",
    "T5ParaphraserTransformer",
    "TranslationBridgeTransformer",
]
