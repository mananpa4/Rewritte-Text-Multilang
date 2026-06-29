"""Interfaz de transformación opcional.

Define el contrato que cualquier backend de IA debe cumplir para integrarse en
el motor. El núcleo depende de esta abstracción, no de una implementación
concreta (mismo principio que humanizer-workbench/transformers/base.py).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from rewrite_engine.core.models import Mode


class BaseTransformer(ABC):
    """Transforma una oración ya reescrita de forma offline en una versión más
    natural usando un modelo (LLM, paraphraser neuronal, etc.).

    Implementaciones futuras: ``AnthropicTransformer``, ``HFParaphraser``.
    """

    @property
    @abstractmethod
    def available(self) -> bool:
        """True si el backend está listo para usarse (modelo cargado, API key...)."""
        raise NotImplementedError

    @abstractmethod
    def refine(self, text: str, *, language: str, mode: Mode) -> str:
        """Devuelve una versión refinada de ``text`` en el idioma dado.

        Debe preservar el significado y NO tocar los tokens ``__PROTECTED_NNN__``.
        Si no puede mejorar el texto, debe devolverlo sin cambios.
        """
        raise NotImplementedError
