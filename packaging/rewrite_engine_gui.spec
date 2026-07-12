# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para el ejecutable de escritorio.

Genera un único .exe con la app Tkinter, los diccionarios del motor y los datos
de las librerías de datos (wordfreq, simplemma, langdetect, spellchecker).

Excluye las dependencias pesadas y opcionales (nltk/WordNet, torch, spaCy,
embeddings, LanguageTool): el motor degrada con gracia y funciona con los
diccionarios JSON, lo que mantiene el ejecutable ligero y fiable.

Uso (desde la raíz del repo):
    pyinstaller packaging/rewrite_engine_gui.spec --noconfirm
"""

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).parent  # raíz del repo (SPECPATH = carpeta packaging/)

# Datos: diccionarios del motor + datos de las librerías de datos.
# `ttkthemes` incluye pixmaps (imágenes) por tema (p.ej. winxpblue) que deben
# empaquetarse para que el tema se vea igual dentro del .exe congelado.
datas = [(str(ROOT / "data"), "rewrite_engine/data")]
for pkg in ("wordfreq", "simplemma", "langdetect", "spellchecker", "ttkthemes"):
    try:
        datas += collect_data_files(pkg)
    except Exception:
        pass

hiddenimports = collect_submodules("rewrite_engine")
# pyexpat/_elementtree (XML) los usa pkg_resources->plistlib en el arranque.
hiddenimports += ["pyexpat", "_elementtree", "xml.parsers.expat"]

# En instalaciones conda varias DLLs viven en Library/bin (ruta no estándar que
# PyInstaller no escanea): pyexpat.pyd depende de libexpat.dll, y _tkinter.pyd
# depende de tcl86t.dll/tk86t.dll/zlib.dll. Sin ellas el .exe crashea al arrancar
# ("DLL load failed while importing pyexpat" / "_tkinter"). Las incluimos.
binaries = []
_seen_dll = set()
for _dll_dir in (
    os.path.join(sys.base_prefix, "Library", "bin"),
    os.path.join(sys.prefix, "Library", "bin"),
):
    for _name in (
        "libexpat.dll", "LIBBZ2.dll", "liblzma.dll",
        "tcl86t.dll", "tk86t.dll", "zlib.dll", "zlib1.dll",
    ):
        _p = os.path.join(_dll_dir, _name)
        if os.path.exists(_p) and _name.lower() not in _seen_dll:
            binaries.append((_p, "."))
            _seen_dll.add(_name.lower())

# Deps pesadas/opcionales que el motor sólo usa si están presentes: se excluyen
# para no inflar el .exe (el motor las detecta ausentes y usa sus fallbacks).
excludes = [
    "nltk", "torch", "sentence_transformers", "transformers", "spacy",
    "language_tool_python", "scipy", "sklearn", "matplotlib", "pandas",
    "fastapi", "uvicorn", "IPython", "notebook",
]

a = Analysis(
    [str(ROOT / "packaging" / "run_gui.py")],
    pathex=[str(ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="RewriteEngine",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # app de ventana (sin consola)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
