"""Ventana de sincronización privada con dowdes.com."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import tkinter as tk
from tkinter import messagebox, ttk

from rewrite_engine.core.models import RewriteRequest


class DowdesClient:
    def __init__(self, base_url: str, token: str, timeout: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _request(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            method="POST" if payload is not None else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc

    def jobs(self, scope: str, languages: str, limit: int) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode(
            {"scope": scope, "lang": languages, "fields": "description", "limit": limit}
        )
        return self._request(f"/api/appvault/rewrite/jobs?{query}").get("jobs", [])

    def save(self, job: dict[str, Any], text: str) -> None:
        self._request(
            "/api/appvault/rewrite/results",
            {
                **{key: job[key] for key in ("ref", "table", "pk", "field", "source_hash")},
                "text": text,
                "engine": "rewrite-engine",
                "model": "local",
            },
        )


class DowdesSyncWindow(tk.Toplevel):
    """Cola con progreso, pausa, reanudación y cancelación cooperativa."""

    def __init__(self, parent: tk.Misc, engine: Any) -> None:
        super().__init__(parent)
        self.engine = engine
        self.title("Sincronizar descripciones de dowdes.com")
        self.geometry("760x430")
        self.minsize(650, 380)
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.cancel_event = threading.Event()
        self.running = False
        self._build()

    def _build(self) -> None:
        config = ttk.LabelFrame(self, text="Conexión privada", padding=8)
        config.pack(fill=tk.X, padx=10, pady=8)
        self.url = tk.StringVar(value="https://dowdes.com")
        self.token = tk.StringVar()
        self.scope = tk.StringVar(value="missing")
        self.languages = tk.StringVar(value="en,es")
        self.limit = tk.IntVar(value=100)
        ttk.Label(config, text="URL:").grid(row=0, column=0, sticky="w")
        ttk.Entry(config, textvariable=self.url, width=38).grid(row=0, column=1, sticky="ew")
        ttk.Label(config, text="Token:").grid(row=0, column=2, padx=(10, 0))
        ttk.Entry(config, textvariable=self.token, show="•", width=24).grid(row=0, column=3)
        ttk.Label(config, text="Acción:").grid(row=1, column=0, pady=(8, 0), sticky="w")
        ttk.Combobox(
            config,
            textvariable=self.scope,
            state="readonly",
            values=("missing", "all", "rewrite"),
            width=12,
        ).grid(row=1, column=1, pady=(8, 0), sticky="w")
        ttk.Label(config, text="Idiomas:").grid(row=1, column=2, padx=(10, 0), pady=(8, 0))
        ttk.Entry(config, textvariable=self.languages, width=12).grid(row=1, column=3, pady=(8, 0), sticky="w")
        config.columnconfigure(1, weight=1)

        self.progress = ttk.Progressbar(self, mode="determinate", style="W7.Horizontal.TProgressbar")
        style = ttk.Style(self)
        style.configure(
            "W7.Horizontal.TProgressbar", troughcolor="#d7e4ef", background="#55b93f",
            lightcolor="#8ee073", darkcolor="#278c24", bordercolor="#7295b2",
        )
        self.progress.pack(fill=tk.X, padx=10, pady=(6, 2))
        self.status = tk.StringVar(value="Preparado.")
        ttk.Label(self, textvariable=self.status).pack(fill=tk.X, padx=10)
        self.log = tk.Text(self, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        actions = ttk.Frame(self)
        actions.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.start_button = ttk.Button(actions, text="Reescribir", command=self._start)
        self.start_button.pack(side=tk.LEFT)
        ttk.Button(actions, text="Pausar", command=self._pause).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Reanudar", command=self._resume).pack(side=tk.LEFT)
        ttk.Button(actions, text="Cancelar", command=self._cancel).pack(side=tk.LEFT, padx=5)

    def _start(self) -> None:
        if self.running:
            return
        if not self.token.get().strip():
            messagebox.showerror("Token requerido", "Configura REWRITE_DESKTOP_TOKEN en el servidor y escríbelo aquí.", parent=self)
            return
        self.running = True
        self.cancel_event.clear()
        self.pause_event.set()
        self.start_button.configure(state=tk.DISABLED)
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        try:
            client = DowdesClient(self.url.get(), self.token.get())
            jobs = client.jobs(self.scope.get(), self.languages.get(), self.limit.get())
            self.after(0, lambda: self.progress.configure(maximum=max(1, len(jobs)), value=0))
            for index, job in enumerate(jobs, 1):
                self.pause_event.wait()
                if self.cancel_event.is_set():
                    break
                result = self.engine.rewrite(
                    RewriteRequest(
                        text=job["text"], language=job["lang"], mode="marketplace", strength=0.5
                    )
                )
                client.save(job, result.rewritten)
                self.after(0, self._progress, index, len(jobs), job.get("title", ""))
            message = "Cancelado." if self.cancel_event.is_set() else "Sincronización completada."
            self.after(0, self.status.set, message)
        except Exception as exc:
            self.after(0, messagebox.showerror, "Error de sincronización", str(exc), parent=self)
            self.after(0, self.status.set, "Error; revisa la conexión y el token.")
        finally:
            self.running = False
            self.after(0, self.start_button.configure, {"state": tk.NORMAL})

    def _progress(self, index: int, total: int, title: str) -> None:
        self.progress.configure(value=index)
        self.status.set(f"{index}/{total}: {title}")
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, f"✓ {title or 'Sin título'}\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _pause(self) -> None:
        self.pause_event.clear()
        self.status.set("Pausado (se detendrá al terminar el elemento actual).")

    def _resume(self) -> None:
        self.pause_event.set()
        self.status.set("Reanudando…")

    def _cancel(self) -> None:
        self.cancel_event.set()
        self.pause_event.set()
        self.status.set("Cancelando…")
