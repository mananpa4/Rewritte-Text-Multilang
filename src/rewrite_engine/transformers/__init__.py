"""Capa de transformación opcional (el "gancho" para enchufar un LLM).

El motor offline usa :class:`NullTransformer` por defecto. Para añadir IA más
adelante basta con implementar :class:`BaseTransformer` (p.ej. un wrapper de la
API de Anthropic o de un modelo HuggingFace) y pasarlo al ``RewriteEngine`` —
sin tocar el núcleo.
"""

from rewrite_engine.transformers.base import BaseTransformer
from rewrite_engine.transformers.null import NullTransformer

__all__ = ["BaseTransformer", "NullTransformer"]
