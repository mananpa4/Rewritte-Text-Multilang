"""Corrección gramatical opcional.

Usa ``language-tool-python`` si está instalado (puede requerir Java o usar la API
pública). Si no, es un no-op: el motor funciona igual sin él. Nunca toca los
tokens protegidos (LanguageTool corrige sobre el texto ya enmascarado).
"""

from __future__ import annotations

# Mapea ISO-639-1 a los códigos de LanguageTool más comunes.
_LT_LANG = {
    "es": "es",
    "en": "en-US",
    "pt": "pt-PT",
    "fr": "fr",
    "it": "it",
    "de": "de-DE",
}


class GrammarChecker:
    """Pulido gramatical que degrada a no-op si LanguageTool no está."""

    def __init__(self, enabled: bool | None = None) -> None:
        self._enabled = enabled
        self._tools: dict[str, object] = {}
        self._mod = None
        if enabled is not False:
            self._mod = self._load()

    @staticmethod
    def _load():
        try:
            import language_tool_python

            return language_tool_python
        except ImportError:
            return None

    @property
    def available(self) -> bool:
        return self._mod is not None

    def _tool(self, lang: str):
        if self._mod is None:
            return None
        code = _LT_LANG.get(lang)
        if code is None:
            return None
        if lang not in self._tools:
            try:
                self._tools[lang] = self._mod.LanguageTool(code)
            except Exception:
                self._tools[lang] = None
        return self._tools[lang]

    def correct(self, text: str, lang: str) -> str:
        """Devuelve el texto corregido, o sin cambios si no hay corrector."""
        tool = self._tool(lang)
        if tool is None:
            return text
        try:
            return tool.correct(text)
        except Exception:
            return text
