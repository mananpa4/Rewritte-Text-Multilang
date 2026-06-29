"""Configuración del motor.

Carga ajustes desde valores por defecto, un YAML opcional y variables de
entorno. Todo es opcional: sin ningún fichero, los defaults bastan.

Umbrales de similitud semántica (del prompt, líneas 649-654):
    normal  >= 0.88
    sensible (legal/médico/técnico) >= 0.93
    creativo >= 0.80
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from rewrite_engine.lang.metadata import (
    DEFAULT_LANGUAGES,
    normalize_language_code,
    normalize_language_list,
)

# Raíz de los datos (diccionarios + listas protegidas). En un wheel instalado
# los datos viven dentro del paquete; en desarrollo (layout src/) viven en la
# raíz del repo. Se detecta cuál existe.
_PKG_DATA = Path(__file__).resolve().parent.parent / "data"   # src/rewrite_engine/data
_REPO_DATA = Path(__file__).resolve().parents[3] / "data"     # <repo>/data
DATA_DIR = _PKG_DATA if _PKG_DATA.exists() else _REPO_DATA

# Umbrales de similitud por categoría de modo.
SIMILARITY_NORMAL = 0.88
SIMILARITY_SENSITIVE = 0.93
SIMILARITY_CREATIVE = 0.80


@dataclass
class EngineConfig:
    """Ajustes del :class:`RewriteEngine`."""

    languages: tuple[str, ...] = DEFAULT_LANGUAGES
    default_language: str = "en"
    data_dir: Path = DATA_DIR

    # Umbrales de validación semántica.
    similarity_normal: float = SIMILARITY_NORMAL
    similarity_sensitive: float = SIMILARITY_SENSITIVE
    similarity_creative: float = SIMILARITY_CREATIVE

    # Activación de componentes opcionales (None = autodetectar disponibilidad).
    use_embeddings: bool | None = None
    use_spacy: bool | None = None
    use_grammar: bool | None = None
    use_wordnet: bool | None = None

    # Máximo de palabras a modificar por oración, como fracción (lo modula strength).
    max_change_ratio: float = 0.5

    # Industrias cuyos diccionarios especializados se cargan además de general.json.
    industries: tuple[str, ...] = ()

    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._normalize_language_settings()

    @classmethod
    def load(cls, path: str | os.PathLike | None = None) -> "EngineConfig":
        """Construye la config combinando defaults + YAML opcional + entorno."""
        cfg = cls()

        candidate = path or os.environ.get("REWRITE_ENGINE_CONFIG")
        if candidate:
            cfg._apply_yaml(Path(candidate))

        cfg._apply_env()
        cfg._normalize_language_settings()
        return cfg

    def _apply_yaml(self, path: Path) -> None:
        if not path.exists():
            return
        try:
            import yaml  # dependencia del núcleo
        except ImportError:  # pragma: no cover - yaml es core, pero por robustez
            return
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for key, value in data.items():
            if key == "languages" and isinstance(value, list):
                self.languages = tuple(str(v) for v in value)
            elif key == "industries" and isinstance(value, list):
                self.industries = tuple(str(v) for v in value)
            elif key == "data_dir":
                self.data_dir = Path(value)
            elif hasattr(self, key):
                setattr(self, key, value)
            else:
                self.extra[key] = value

    def _apply_env(self) -> None:
        # Permite forzar/desactivar componentes vía entorno: REWRITE_ENGINE_USE_EMBEDDINGS=0
        for attr, env in (
            ("use_embeddings", "REWRITE_ENGINE_USE_EMBEDDINGS"),
            ("use_spacy", "REWRITE_ENGINE_USE_SPACY"),
            ("use_grammar", "REWRITE_ENGINE_USE_GRAMMAR"),
            ("use_wordnet", "REWRITE_ENGINE_USE_WORDNET"),
        ):
            raw = os.environ.get(env)
            if raw is not None:
                setattr(self, attr, raw.strip() not in ("0", "false", "False", ""))

        langs = os.environ.get("REWRITE_ENGINE_LANGUAGES")
        if langs:
            self.languages = tuple(part.strip() for part in langs.split(",") if part.strip())

        lang = os.environ.get("REWRITE_ENGINE_DEFAULT_LANG")
        if lang:
            self.default_language = lang.strip()

    def _normalize_language_settings(self) -> None:
        self.languages = normalize_language_list(self.languages, fallback=DEFAULT_LANGUAGES)
        self.default_language = normalize_language_code(
            self.default_language,
            default=self.languages[0],
        )
        if self.default_language not in self.languages:
            self.default_language = self.languages[0]
        self.data_dir = Path(self.data_dir)

    def similarity_threshold(self, *, sensitive: bool, creative: bool) -> float:
        """Umbral aplicable según la naturaleza del modo."""
        if sensitive:
            return self.similarity_sensitive
        if creative:
            return self.similarity_creative
        return self.similarity_normal
