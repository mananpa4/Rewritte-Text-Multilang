"""App de escritorio del motor de reescritura (Tkinter).

Interfaz de dos paneles: a la izquierda pegas el texto; a la derecha aparece el
texto reescrito. Incluye selector de idioma y modo, control de intensidad,
generación de alternativas y un **corrector ortográfico** (offline, opcional)
que subraya las palabras desconocidas y ofrece sugerencias con clic derecho, en
ambos paneles.

Ejecutar:  ``rewrite-engine-gui``  (o ``python -m rewrite_engine.desktop.app``)
Requiere el extra ``[desktop]`` para el corrector (``pyspellchecker``); sin él,
la reescritura funciona igual y el corrector queda inactivo.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import regex as re

from rewrite_engine.core.models import Mode
from rewrite_engine.desktop.spell import SpellService
from rewrite_engine.lang.metadata import DEFAULT_LANGUAGES

_WORD_RE = re.compile(r"\p{L}[\p{L}\p{M}'’\-]*")
_MISSPELLED_TAG = "misspelled"

# Los 12 modos como (etiqueta visible, valor de Mode) para los radio-botones.
_MODE_LABELS: list[tuple[str, str]] = [
    ("Natural", "natural"),
    ("Formal", "formal"),
    ("Informal", "informal"),
    ("Profesional", "professional"),
    ("SEO", "seo"),
    ("Marketplace", "marketplace"),
    ("Técnico", "technical"),
    ("Simple", "simple"),
    ("Expandido", "expanded"),
    ("Resumido", "summarized"),
    ("Solo gramática", "grammar_only"),
    ("Creativo", "creative"),
]


def _resolve_data_dir() -> Path | None:
    """Ubica los datos empaquetados cuando corre como .exe (PyInstaller)."""
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        for candidate in (base / "rewrite_engine" / "data", base / "data"):
            if candidate.exists():
                return candidate
    return None  # en desarrollo/instalado, config.DATA_DIR ya lo resuelve


# Orden de preferencia de temas con aspecto "Windows clásico" (XP/7), de más a
# menos fiel:
#   - 'winxpblue' (paquete de terceros `ttkthemes`, extra [desktop]): azul
#     XP-Luna dibujado por pixmaps, idéntico en cualquier versión de Windows.
#     Licencia **GPL-3.0-or-later** (copyleft) — si distribuyes el .exe con
#     este tema, GPL obliga a poder entregar el código fuente completo a quien
#     lo reciba. Opt-in a propósito: sólo se usa si `ttkthemes` está instalado.
#   - 'vista' / 'xpnative' / 'winnative': incluidos en Tcl/Tk en Windows (sin
#     dependencias ni licencias nuevas), dibujan los controles con el motor de
#     temas real del sistema operativo (UxTheme) — Aero en 7, Luna en XP,
#     controles nativos actuales en 10/11.
#   - 'clam': aspecto genérico multiplataforma (el usado antes de este cambio).
_PREFERRED_THEMES = ("winxpblue", "vista", "xpnative", "winnative", "clam")


def _create_style(root: tk.Misc) -> ttk.Style:
    """``ThemedStyle`` de ``ttkthemes`` si está instalado (para que Tcl
    conozca temas de terceros como 'winxpblue'); si no, el ``ttk.Style`` normal."""
    try:
        from ttkthemes import ThemedStyle

        return ThemedStyle(root)
    except ImportError:
        return ttk.Style(root)


def _apply_native_theme(style: ttk.Style) -> None:
    """Aplica el tema disponible más parecido a Windows clásico (XP/7)."""
    available = style.theme_names()
    for theme in _PREFERRED_THEMES:
        if theme in available:
            try:
                style.theme_use(theme)
                return
            except tk.TclError:
                continue


class RewriteApp(tk.Tk):
    """Ventana principal."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Rewrite Engine — Reescritor multilenguaje")
        self.geometry("1080x680")
        self.minsize(820, 480)

        self._engine = None
        self._spell = SpellService()
        self._last_lang = "es"
        self._ai_transformer = None  # instancia cargada del T5 (None = descargado/no cargado)
        self._ai_bridge = None  # envuelve _ai_transformer con traducción; cachea modelos por idioma

        self._build_ui()
        self._load_engine_async()

    # -- construcción de la UI ---------------------------------------------
    def _build_ui(self) -> None:
        style = _create_style(self)
        _apply_native_theme(style)
        style.configure("Rewrite.TButton", font=("Segoe UI", 10, "bold"), padding=6)

        # --- Fila de opciones generales ---
        opts = ttk.Frame(self, padding=(8, 6, 8, 2))
        opts.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(opts, text="Idioma:").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value="auto")
        ttk.Combobox(
            opts, textvariable=self.lang_var, width=7, state="readonly",
            values=["auto", *DEFAULT_LANGUAGES],
        ).pack(side=tk.LEFT, padx=(4, 14))

        ttk.Label(opts, text="Intensidad:").pack(side=tk.LEFT)
        self.strength_var = tk.DoubleVar(value=0.4)
        ttk.Scale(
            opts, from_=0.1, to=0.9, variable=self.strength_var,
            length=130, command=self._on_strength,
        ).pack(side=tk.LEFT, padx=(4, 4))
        self.strength_lbl = ttk.Label(opts, text="0.40", width=4)
        self.strength_lbl.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(opts, text="Alternativas:").pack(side=tk.LEFT)
        self.alts_var = tk.IntVar(value=0)
        ttk.Spinbox(opts, from_=0, to=3, width=3, textvariable=self.alts_var).pack(
            side=tk.LEFT, padx=(4, 14)
        )

        self.summarize_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opts, text="Resumir texto", variable=self.summarize_var,
            command=self._on_summarize_toggle,
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.autospell_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opts, text="Corregir ortografía", variable=self.autospell_var,
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.ai_var = tk.BooleanVar(value=False)
        self.ai_checkbox = ttk.Checkbutton(
            opts, text="Reescritura con IA (T5, beta)", variable=self.ai_var,
            command=self._on_ai_toggle,
        )
        self.ai_checkbox.pack(side=tk.LEFT, padx=(0, 12))

        self.ai_translate_var = tk.BooleanVar(value=False)
        self.ai_translate_checkbox = ttk.Checkbutton(
            opts, text="Traducir para IA en todos los idiomas (más lento)",
            variable=self.ai_translate_var, command=self._on_ai_translate_toggle,
        )
        self.ai_translate_checkbox.pack(side=tk.LEFT)

        ai_note = ttk.Frame(self, padding=(8, 0, 8, 2))
        ai_note.pack(side=tk.TOP, fill=tk.X)
        self.ai_note_var = tk.StringVar()
        ttk.Label(
            ai_note, textvariable=self.ai_note_var,
            foreground="#666666", font=("Segoe UI", 8, "italic"),
        ).pack(side=tk.LEFT)
        self._update_ai_note()

        # --- Selección de MODO (los 12 modos como opciones seleccionables) ---
        self.mode_var = tk.StringVar(value=Mode.NATURAL.value)
        self.mode_var.trace_add("write", self._on_mode_var_change)
        modes = ttk.LabelFrame(self, text="Modo de reescritura", padding=(8, 4))
        modes.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(2, 4))
        cols = 6
        for i, (label, value) in enumerate(_MODE_LABELS):
            ttk.Radiobutton(
                modes, text=label, value=value, variable=self.mode_var,
            ).grid(row=i // cols, column=i % cols, sticky=tk.W, padx=6, pady=1)

        # --- Acciones ---
        actions = ttk.Frame(self, padding=(8, 0, 8, 6))
        actions.pack(side=tk.TOP, fill=tk.X)
        self.rewrite_btn = ttk.Button(
            actions, text="Reescribir  ▶", command=self._on_rewrite,
            state=tk.DISABLED, style="Rewrite.TButton",
        )
        self.rewrite_btn.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions, text="Revisar ortografía  ✓", command=self._on_spellcheck).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(actions, text="Copiar resultado", command=self._on_copy).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(actions, text="Limpiar", command=self._on_clear).pack(side=tk.LEFT)

        # --- Paneles izquierda/derecha ---
        panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 6))
        self.input_text = self._make_pane(panes, "Texto original (pega aquí)")
        self.output_text = self._make_pane(panes, "Texto reescrito")

        # --- Barra de estado ---
        self.status_var = tk.StringVar(value="Cargando motor…")
        ttk.Label(
            self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W,
            padding=(8, 3),
        ).pack(side=tk.BOTTOM, fill=tk.X)

    def _on_summarize_toggle(self) -> None:
        self.mode_var.set("summarized" if self.summarize_var.get() else "natural")

    def _on_mode_var_change(self, *_args) -> None:
        # Mantiene el checkbox "Resumir" sincronizado con el modo elegido.
        self.summarize_var.set(self.mode_var.get() == "summarized")

    def _on_copy(self) -> None:
        text = self.output_text.get("1.0", "end-1c")
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_var.set("Resultado copiado al portapapeles.")

    # -- toggle de IA (T5 paráfrasis, opt-in) + puente de traducción ---------
    def _update_ai_note(self) -> None:
        if self.ai_translate_var.get():
            self.ai_note_var.set(
                "Traduce a inglés, aplica la IA y traduce de vuelta: aplica a los 12 "
                "idiomas, pero es más lento y añade el riesgo propio de traducir dos veces."
            )
        else:
            self.ai_note_var.set(
                "La IA sólo se aplica a texto en inglés (modelos T5 disponibles son "
                "monolingües); los otros 11 idiomas siguen usando el motor offline."
            )

    def _on_ai_translate_toggle(self) -> None:
        self._update_ai_note()
        if self.ai_var.get():
            self._apply_ai_transformer()  # re-envuelve/desenvuelve sin recargar el T5

    def _on_ai_toggle(self) -> None:
        if not self.ai_var.get():
            if self._engine is not None:
                self._engine.set_transformer(None)  # vuelve a NullTransformer
            self.status_var.set(
                "IA desactivada. Motor 100% offline (mismo comportamiento en los 12 idiomas)."
            )
            return

        if self._engine is None:
            self.ai_var.set(False)
            return

        # Ya cargado en esta sesión: reutiliza la instancia (evita recargar el
        # modelo en cada toggle, que puede tardar varios segundos).
        if self._ai_transformer is not None and self._ai_transformer.available:
            self._apply_ai_transformer()
            return

        self._load_ai_transformer_async()

    def _apply_ai_transformer(self) -> None:
        """Aplica el T5 al motor, envuelto en el puente de traducción si el
        checkbox correspondiente está activo. No recarga ningún modelo."""
        if self._engine is None or self._ai_transformer is None:
            return
        if self.ai_translate_var.get():
            if self._ai_bridge is None:
                from rewrite_engine.transformers.translation_bridge import (
                    TranslationBridgeTransformer,
                )

                self._ai_bridge = TranslationBridgeTransformer(inner=self._ai_transformer)
            self._engine.set_transformer(self._ai_bridge)
            self.status_var.set(
                "IA activa con traducción (T5 + MarianMT). Aplica a los 12 idiomas."
            )
        else:
            self._engine.set_transformer(self._ai_transformer)
            self.status_var.set("IA activa (T5). Se aplica sólo a texto en inglés.")

    def _load_ai_transformer_async(self) -> None:
        self.ai_checkbox.config(state=tk.DISABLED)
        self.status_var.set(
            "Cargando modelo de IA (T5)… la primera vez descarga ~240 MB, puede tardar."
        )

        def worker() -> None:
            try:
                from rewrite_engine.transformers.t5_paraphraser import T5ParaphraserTransformer

                transformer = T5ParaphraserTransformer()
            except Exception as exc:  # noqa: BLE001 - se reporta al usuario
                self.after(0, lambda: self._on_ai_load_error(exc))
                return
            self.after(0, lambda: self._on_ai_loaded(transformer))

        threading.Thread(target=worker, daemon=True).start()

    def _on_ai_loaded(self, transformer) -> None:
        self.ai_checkbox.config(state=tk.NORMAL)
        if not transformer.available:
            self.ai_var.set(False)
            err = transformer.load_error or "modelo no disponible"
            self.status_var.set(f"No se pudo cargar la IA: {err}")
            messagebox.showwarning(
                "IA no disponible",
                "No se pudo cargar el modelo de IA.\n\n"
                "Instala las dependencias con:\n"
                '  pip install -e ".[ai-paraphrase]"\n\n'
                f"Detalle: {err}",
            )
            return
        self._ai_transformer = transformer
        self._ai_bridge = None  # se reconstruye envolviendo la instancia nueva
        self._apply_ai_transformer()

    def _on_ai_load_error(self, exc: Exception) -> None:
        self.ai_checkbox.config(state=tk.NORMAL)
        self.ai_var.set(False)
        self.status_var.set(f"Error al cargar la IA: {exc}")

    def _make_pane(self, parent: ttk.PanedWindow, title: str) -> tk.Text:
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=title, padding=(2, 2)).pack(side=tk.TOP, anchor=tk.W)
        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(container, orient=tk.VERTICAL)
        text = tk.Text(
            container, wrap=tk.WORD, undo=True, font=("Segoe UI", 11),
            padx=8, pady=8, yscrollcommand=scroll.set,
        )
        scroll.config(command=text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text.tag_config(_MISSPELLED_TAG, foreground="#c0392b", underline=True)
        text.bind("<Button-3>", lambda e, w=text: self._show_context_menu(e, w))
        # Ctrl+A para seleccionar todo (Tkinter no lo bindea por defecto;
        # Ctrl+C/V/X sí funcionan de forma nativa en tk.Text).
        text.bind("<Control-a>", self._select_all)
        text.bind("<Control-A>", self._select_all)
        parent.add(frame, weight=1)
        return text

    @staticmethod
    def _select_all(event: tk.Event) -> str:
        widget = event.widget
        widget.tag_add(tk.SEL, "1.0", tk.END)
        widget.mark_set(tk.INSERT, tk.END)
        widget.see(tk.INSERT)
        return "break"  # evita el salto de línea que Ctrl+A insertaría

    # -- carga del motor en segundo plano ----------------------------------
    def _load_engine_async(self) -> None:
        def worker() -> None:
            try:
                from rewrite_engine.core.config import EngineConfig
                from rewrite_engine.core.engine import RewriteEngine

                data_dir = _resolve_data_dir()
                config = EngineConfig.load()
                if data_dir is not None:
                    config.data_dir = data_dir
                engine = RewriteEngine(config=config)
                self.after(0, lambda: self._on_engine_ready(engine))
            except Exception as exc:  # noqa: BLE001 - mostrar al usuario
                self.after(0, lambda: self._on_engine_error(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _on_engine_ready(self, engine) -> None:
        self._engine = engine
        self.rewrite_btn.config(state=tk.NORMAL)
        spell = "corrector activo" if self._spell.available else "corrector no instalado"
        self.status_var.set(f"Listo · {len(engine._cfg.languages)} idiomas · {spell}")

    def _on_engine_error(self, exc: Exception) -> None:
        self.status_var.set(f"Error al cargar el motor: {exc}")
        messagebox.showerror("Error", f"No se pudo iniciar el motor:\n{exc}")

    # -- acciones -----------------------------------------------------------
    def _on_strength(self, _value: str) -> None:
        self.strength_lbl.config(text=f"{self.strength_var.get():.2f}")

    def _on_clear(self) -> None:
        for widget in (self.input_text, self.output_text):
            widget.tag_remove(_MISSPELLED_TAG, "1.0", tk.END)
            widget.delete("1.0", tk.END)
        self.status_var.set("Limpio")

    def _on_rewrite(self) -> None:
        if self._engine is None:
            return
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text:
            self.status_var.set("Escribe o pega texto en el panel izquierdo.")
            return

        from rewrite_engine.core.models import RewriteRequest

        request = RewriteRequest(
            text=text,
            language=self.lang_var.get(),
            mode=self.mode_var.get(),
            strength=float(self.strength_var.get()),
            return_alternatives=int(self.alts_var.get()),
        )
        self.rewrite_btn.config(state=tk.DISABLED)
        self.status_var.set("Reescribiendo…")

        def worker() -> None:
            try:
                result = self._engine.rewrite(request)
                self.after(0, lambda: self._on_rewrite_done(result))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._on_rewrite_error(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _on_rewrite_done(self, result) -> None:
        self.rewrite_btn.config(state=tk.NORMAL)
        self._last_lang = result.language

        out = result.rewritten
        if result.alternatives:
            out += "\n\n— Alternativas —\n" + "\n".join(
                f"• {alt}" for alt in result.alternatives
            )
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", out)

        status = (
            f"idioma={result.language} · modo={result.mode} · "
            f"similitud={result.similarity_score:.2f} · "
            f"legibilidad={result.readability_score:.2f} · "
            f"cambios={len(result.changed_words)}"
        )
        if result.warnings:
            status += "  ⚠ " + " | ".join(result.warnings)
        self.status_var.set(status)

        # Corrector automático sobre la salida (si el checkbox está activo).
        if self.autospell_var.get():
            self._spell_check_widget(self.output_text, result.language)

    def _on_rewrite_error(self, exc: Exception) -> None:
        self.rewrite_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Error: {exc}")
        messagebox.showerror("Error al reescribir", str(exc))

    # -- corrector ortográfico ---------------------------------------------
    def _resolve_lang(self, text: str) -> str:
        lang = self.lang_var.get()
        if lang and lang != "auto":
            from rewrite_engine.lang.metadata import normalize_language_code

            return normalize_language_code(lang, default=self._last_lang)
        if self._engine is not None and text.strip():
            try:
                return self._engine._detector.detect(text).language
            except Exception:
                pass
        return self._last_lang

    def _on_spellcheck(self) -> None:
        if not self._spell.available:
            messagebox.showinfo(
                "Corrector no disponible",
                "Instala el corrector con:\n\npip install pyspellchecker\n\n"
                "(o el extra: pip install -e \".[desktop]\")",
            )
            return
        total = 0
        for widget in (self.input_text, self.output_text):
            text = widget.get("1.0", "end-1c")
            if text.strip():
                total += self._spell_check_widget(widget, self._resolve_lang(text))
        self.status_var.set(f"Ortografía: {total} palabra(s) marcada(s).")

    def _spell_check_widget(self, widget: tk.Text, lang: str) -> int:
        widget.tag_remove(_MISSPELLED_TAG, "1.0", tk.END)
        if not self._spell.supports(lang):
            return 0
        content = widget.get("1.0", "end-1c")
        spans = [(m.group(), m.start(), m.end()) for m in _WORD_RE.finditer(content)]
        unknown = self._spell.unknown([w.lower() for w, _, _ in spans], lang)
        count = 0
        for word, start, end in spans:
            if word.lower() in unknown:
                s_idx = widget.index(f"1.0 + {start} chars")
                e_idx = widget.index(f"1.0 + {end} chars")
                widget.tag_add(_MISSPELLED_TAG, s_idx, e_idx)
                count += 1
        return count

    def _show_context_menu(self, event: tk.Event, widget: tk.Text) -> None:
        """Menú contextual del clic derecho: edición estándar + ortografía.

        Siempre ofrece Cortar/Copiar/Pegar/Seleccionar todo/Deshacer/Rehacer.
        Si el clic cae sobre una palabra subrayada como mal escrita, antepone
        las sugerencias de corrección.
        """
        widget.mark_set(tk.INSERT, f"@{event.x},{event.y}")
        menu = tk.Menu(self, tearoff=0)

        misspelled_range = self._misspelled_at(widget, event)
        if misspelled_range is not None:
            start, end = misspelled_range
            word = widget.get(start, end)
            lang = self._resolve_lang(widget.get("1.0", "end-1c"))
            suggestions = self._spell.suggestions(word.lower(), lang)
            if suggestions:
                for sugg in suggestions:
                    menu.add_command(
                        label=sugg,
                        command=lambda s=sugg, a=start, b=end, w=widget: self._replace_word(w, a, b, s),
                    )
            else:
                menu.add_command(label="(sin sugerencias)", state=tk.DISABLED)
            menu.add_command(
                label="Ignorar",
                command=lambda a=start, b=end, w=widget: w.tag_remove(_MISSPELLED_TAG, a, b),
            )
            menu.add_separator()

        has_selection = bool(widget.tag_ranges(tk.SEL))
        has_content = bool(widget.get("1.0", "end-1c"))
        try:
            has_clipboard = bool(self.clipboard_get())
        except tk.TclError:
            has_clipboard = False

        menu.add_command(
            label="Cortar", accelerator="Ctrl+X",
            state=tk.NORMAL if has_selection else tk.DISABLED,
            command=lambda w=widget: w.event_generate("<<Cut>>"),
        )
        menu.add_command(
            label="Copiar", accelerator="Ctrl+C",
            state=tk.NORMAL if has_selection else tk.DISABLED,
            command=lambda w=widget: w.event_generate("<<Copy>>"),
        )
        menu.add_command(
            label="Pegar", accelerator="Ctrl+V",
            state=tk.NORMAL if has_clipboard else tk.DISABLED,
            command=lambda w=widget: w.event_generate("<<Paste>>"),
        )
        menu.add_separator()
        menu.add_command(
            label="Seleccionar todo", accelerator="Ctrl+A",
            state=tk.NORMAL if has_content else tk.DISABLED,
            command=lambda w=widget: self._select_all_widget(w),
        )
        menu.add_separator()
        menu.add_command(
            label="Deshacer", accelerator="Ctrl+Z",
            command=lambda w=widget: self._safe_edit(w, "<<Undo>>"),
        )
        menu.add_command(
            label="Rehacer", accelerator="Ctrl+Y",
            command=lambda w=widget: self._safe_edit(w, "<<Redo>>"),
        )

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    @staticmethod
    def _misspelled_at(widget: tk.Text, event: tk.Event) -> tuple[str, str] | None:
        idx = widget.index(f"@{event.x},{event.y}")
        rng = widget.tag_prevrange(_MISSPELLED_TAG, f"{idx}+1c")
        if not rng or widget.compare(idx, "<", rng[0]) or widget.compare(idx, ">=", rng[1]):
            return None
        return rng

    @staticmethod
    def _select_all_widget(widget: tk.Text) -> None:
        widget.tag_add(tk.SEL, "1.0", tk.END)
        widget.mark_set(tk.INSERT, tk.END)

    @staticmethod
    def _safe_edit(widget: tk.Text, virtual_event: str) -> None:
        try:
            widget.event_generate(virtual_event)
        except tk.TclError:
            pass  # pila de deshacer/rehacer vacía

    def _replace_word(self, widget: tk.Text, start: str, end: str, replacement: str) -> None:
        original = widget.get(start, end)
        if original[:1].isupper():
            replacement = replacement[:1].upper() + replacement[1:]
        widget.delete(start, end)
        widget.insert(start, replacement)


def main() -> None:
    app = RewriteApp()
    app.mainloop()


if __name__ == "__main__":
    main()
