"""Fuente de sinónimos basada en diccionarios JSON editables.

Carga ``data/dictionaries/{lang}/{industry}.json``. Cada archivo es una lista de
entradas con el formato del prompt (líneas 485-511):

    {
      "word": "comprar", "lemma": "comprar", "pos": "verb", "language": "es",
      "synonyms": [
        {"text": "adquirir", "formality": "formal", "frequency": 0.82,
         "contexts": ["marketplace", "legal"], "avoidContexts": ["informal"]}
      ],
      "antonyms": ["vender"],
      "examples": ["..."]
    }

El índice se construye por lema (minúsculas) para búsqueda O(1).
"""

from __future__ import annotations

import json
from pathlib import Path

from rewrite_engine.synonyms.base import SynonymOption, SynonymSource


class DictSource(SynonymSource):
    """Diccionarios JSON locales por idioma e industria."""

    def __init__(self, data_dir: Path, industries: tuple[str, ...] = ()) -> None:
        self._dir = Path(data_dir) / "dictionaries"
        # Si se especifican industrias, sólo se cargan general + esas. Si no, se
        # cargan TODOS los .json del idioma (general + cualquier industria);
        # el filtrado por contexto del SynonymEngine decide su uso.
        self._industries = tuple(industries)
        # índice[lang][lemma] -> list[SynonymOption]
        self._index: dict[str, dict[str, list[SynonymOption]]] = {}
        self._loaded: set[str] = set()

    @property
    def available(self) -> bool:
        return self._dir.exists()

    def _ensure_loaded(self, lang: str) -> None:
        if lang in self._loaded:
            return
        self._loaded.add(lang)
        lang_dir = self._dir / lang
        index: dict[str, list[SynonymOption]] = {}
        if lang_dir.exists():
            if self._industries:
                paths = [lang_dir / "general.json"]
                paths += [lang_dir / f"{ind}.json" for ind in self._industries]
            else:
                # Todos los .json del idioma (general primero por prioridad).
                others = sorted(p for p in lang_dir.glob("*.json") if p.stem != "general")
                paths = [lang_dir / "general.json", *others]
            for path in paths:
                if path.exists():
                    self._load_file(path, index)
        self._index[lang] = index

    @staticmethod
    def _load_file(path: Path, index: dict[str, list[SynonymOption]]) -> None:
        try:
            entries = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(entries, list):
            return
        for entry in entries:
            lemma = str(entry.get("lemma") or entry.get("word") or "").lower().strip()
            if not lemma:
                continue
            options = index.setdefault(lemma, [])
            for syn in entry.get("synonyms", []):
                if isinstance(syn, str):
                    options.append(SynonymOption(text=syn, source="dict"))
                    continue
                text = str(syn.get("text", "")).strip()
                if not text:
                    continue
                options.append(
                    SynonymOption(
                        text=text,
                        formality=str(syn.get("formality", "neutral")),
                        frequency=float(syn.get("frequency", 0.5)),
                        contexts=tuple(syn.get("contexts", ())),
                        avoid_contexts=tuple(syn.get("avoidContexts", ())),
                        source="dict",
                    )
                )
            # antónimos: útiles para no usarlos como sinónimo por error
            for ant in entry.get("antonyms", []):
                if isinstance(ant, str) and ant.strip():
                    options.append(
                        SynonymOption(text=ant.strip(), source="dict", antonym=True)
                    )

    def synonyms(self, lemma: str, lang: str, pos: str = "") -> list[SynonymOption]:
        self._ensure_loaded(lang)
        return list(self._index.get(lang, {}).get(lemma.lower().strip(), []))
