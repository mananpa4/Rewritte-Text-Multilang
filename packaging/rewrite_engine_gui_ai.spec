# -*- mode: python ; coding: utf-8 -*-
"""Distribución onedir con IA offline incluida.

Incluye el modelo de paráfrasis de calidad y el par MarianMT español↔inglés.
Otros pares de traducción se descargan bajo demanda y quedan en caché.
"""

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

ROOT = Path(SPECPATH).parent
HF_HUB = Path.home() / ".cache" / "huggingface" / "hub"


def model_snapshot(repo_id: str) -> Path:
    repo_dir = HF_HUB / f"models--{repo_id.replace('/', '--')}"
    refs_main = repo_dir / "refs" / "main"
    if refs_main.exists():
        revision = refs_main.read_text(encoding="utf-8").strip()
        candidate = repo_dir / "snapshots" / revision
        if candidate.is_dir():
            return candidate
    snapshots = sorted((repo_dir / "snapshots").glob("*"))
    if not snapshots:
        raise FileNotFoundError(
            f"Modelo no encontrado en caché: {repo_id}. Descárgalo antes de construir."
        )
    return snapshots[-1]


models = (
    "Ateeqq/Text-Rewriter-Paraphraser",
    "Helsinki-NLP/opus-mt-es-en",
    "Helsinki-NLP/opus-mt-en-es",
)

datas = [(str(ROOT / "data"), "rewrite_engine/data")]
datas.append((str(ROOT / "models" / "nllb-200-distilled-600M-int8"),
              "models/nllb-200-distilled-600M-int8"))
for pkg in (
    "wordfreq", "simplemma", "langdetect", "spellchecker", "ttkthemes",
    "transformers", "sentencepiece",
):
    try:
        datas += collect_data_files(pkg)
    except Exception:
        pass
datas += copy_metadata("torchcodec")
for model in models:
    datas.append((str(model_snapshot(model)), f"models/{model.replace('/', '--')}"))

hiddenimports = collect_submodules("rewrite_engine")
hiddenimports += collect_submodules("transformers.models.t5")
hiddenimports += collect_submodules("transformers.models.marian")
hiddenimports += collect_submodules("transformers.models.auto")
hiddenimports += collect_submodules("ctranslate2")
hiddenimports += ["pyexpat", "_elementtree", "xml.parsers.expat", "sentencepiece"]

binaries = []
seen_dll = set()
for dll_dir in (
    os.path.join(sys.base_prefix, "Library", "bin"),
    os.path.join(sys.prefix, "Library", "bin"),
):
    for name in (
        "libexpat.dll", "LIBBZ2.dll", "liblzma.dll", "tcl86t.dll", "tk86t.dll",
        "zlib.dll", "zlib1.dll",
    ):
        path = os.path.join(dll_dir, name)
        if os.path.exists(path) and name.lower() not in seen_dll:
            binaries.append((path, "."))
            seen_dll.add(name.lower())

a = Analysis(
    [str(ROOT / "packaging" / "run_gui.py")],
    pathex=[str(ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "spacy", "language_tool_python", "fastapi", "uvicorn", "IPython",
        "notebook", "matplotlib", "pandas", "torchaudio", "torchvision",
        "tensorflow", "onnx", "onnxruntime", "sklearn", "pyarrow",
        "datasets", "cv2", "tensorboard", "jax", "flax",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RewriteEngineAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="RewriteEngineAI",
)
