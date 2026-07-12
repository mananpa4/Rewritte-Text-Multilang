"""Punto de entrada del ejecutable de escritorio (para PyInstaller).

Envuelve el arranque en un manejador que registra cualquier fallo en un archivo
de log y lo muestra en un diálogo, para que un .exe de ventana (sin consola) no
se cierre en silencio ante un error de arranque.
"""

import os
import sys
import tempfile
import traceback


def _log_path() -> str:
    return os.path.join(tempfile.gettempdir(), "rewrite_engine_error.log")


def _selftest() -> int:
    """Prueba end-to-end del bundle: carga el motor y reescribe una frase.

    Escribe el resultado en un log (el .exe de ventana no tiene stdout) y
    devuelve 0 si todo funcionó. Se invoca con ``RewriteEngine.exe --selftest``.
    """
    out = os.path.join(tempfile.gettempdir(), "rewrite_engine_selftest.log")
    try:
        from rewrite_engine.desktop.app import _resolve_data_dir
        from rewrite_engine.core.config import EngineConfig
        from rewrite_engine.core.engine import RewriteEngine
        from rewrite_engine.core.models import RewriteRequest

        config = EngineConfig.load()
        data_dir = _resolve_data_dir()
        if data_dir is not None:
            config.data_dir = data_dir
        engine = RewriteEngine(config=config)
        r = engine.rewrite(RewriteRequest(
            text="Este producto es bueno y barato.", language="es",
            mode="marketplace", strength=0.5,
        ))
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(f"OK\nidiomas={len(engine._cfg.languages)}\n")
            fh.write(f"data_dir={config.data_dir}\n")
            fh.write(f"IN ={r.original}\nOUT={r.rewritten}\n")
            fh.write(f"changed={len(r.changed_words)} sim={r.similarity_score:.2f}\n")
        return 0
    except Exception:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("FAIL\n" + traceback.format_exc())
        return 1


def main() -> None:
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    try:
        from rewrite_engine.desktop.app import main as gui_main

        gui_main()
    except Exception:  # noqa: BLE001 - diagnóstico de arranque
        tb = traceback.format_exc()
        try:
            with open(_log_path(), "w", encoding="utf-8") as fh:
                fh.write(tb)
        except OSError:
            pass
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "RewriteEngine — error de arranque",
                f"{tb}\n\n(Guardado en {_log_path()})",
            )
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
