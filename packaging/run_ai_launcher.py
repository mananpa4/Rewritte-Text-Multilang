"""Lanzador estable para la distribución onedir con modelos de IA."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    target = Path(sys.executable).resolve().parent / "RewriteEngineAI" / "RewriteEngineAI.exe"
    if not target.is_file():
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "RewriteEngine",
            "No se encontró RewriteEngineAI\\RewriteEngineAI.exe junto al lanzador.",
        )
        return 2
    return subprocess.run([str(target), *sys.argv[1:]], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
