"""Capa de sinónimos: fuentes (diccionarios JSON, WordNet/OMW) y motor."""

from rewrite_engine.synonyms.base import SynonymOption, SynonymSource
from rewrite_engine.synonyms.engine import SynonymEngine

__all__ = ["SynonymOption", "SynonymSource", "SynonymEngine"]
