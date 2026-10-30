"""Resolución de modelos Hugging Face incluidos junto al ejecutable.

En desarrollo se aceptan identificadores del Hub. En una distribución congelada
se prefiere una copia local bajo ``models/<nombre-normalizado>`` para garantizar
el funcionamiento offline y evitar descargas en el primer arranque.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def model_slug(model_name: str) -> str:
    """Convierte ``organización/modelo`` en un nombre de carpeta estable."""
    return model_name.replace("/", "--")


def bundled_model_path(model_name: str) -> Path | None:
    """Localiza una copia empaquetada del modelo, si existe."""
    roots: list[Path] = []
    configured = os.environ.get("REWRITE_ENGINE_MODELS_DIR")
    if configured:
        roots.append(Path(configured))
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        roots.append(Path(frozen_root) / "models")
    if getattr(sys, "frozen", False):
        roots.append(Path(sys.executable).resolve().parent / "models")

    slug = model_slug(model_name)
    for root in roots:
        candidate = root / slug
        if candidate.is_dir():
            return candidate
    return None


def resolve_model_source(model_name: str) -> str:
    """Devuelve ruta local empaquetada o, fuera del bundle, el id del Hub."""
    bundled = bundled_model_path(model_name)
    return str(bundled) if bundled is not None else model_name
