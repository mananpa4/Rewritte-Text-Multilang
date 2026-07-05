"""Ollama local-LLM transformer — free, offline, no API keys, no tokens.

Plugs a locally-running Ollama model into the engine via :class:`BaseTransformer`.
The engine masks entities (``__PROTECTED_NNN__``) before this stage runs, and the
prompt instructs the model to keep those placeholders (and any HTML) intact.

Prereqs (once, on the machine that runs the batch):
    ollama serve              # start the local server (usually auto-starts)
    ollama pull qwen2.5:3b    # a small, strong multilingual model (~2 GB)

Uses only the Python standard library (urllib/json) — no extra dependency.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

from rewrite_engine.core.models import Mode
from rewrite_engine.transformers.base import BaseTransformer

_PROT_RE = re.compile(r"PROTECTEDTOKEN\d+X")  # engine protector token format

_LANG_NAMES = {
    "en": "English", "es": "Spanish", "pt": "Portuguese", "fr": "French",
    "it": "Italian", "de": "German", "nl": "Dutch", "pl": "Polish",
    "ru": "Russian", "uk": "Ukrainian", "sv": "Swedish",
}

_MODE_STYLE = {
    "marketplace": "an engaging app-store style, concise and benefit-focused",
    "seo": "a clear, natural style that reads well for search",
    "professional": "a professional, neutral tone",
    "natural": "a natural, fluent tone",
    "formal": "a formal tone",
    "informal": "a friendly, informal tone",
    "technical": "a precise, technical tone",
    "simple": "simple, easy-to-read language",
}


class OllamaTransformer(BaseTransformer):
    """Refine (rewrite) text with a local Ollama model."""

    def __init__(self, model: str = "qwen2.5:3b", url: str | None = None, timeout: float = 120.0) -> None:
        self._model = model
        self._url = (url or os.environ.get("OLLAMA_URL") or "http://localhost:11434").rstrip("/")
        self._timeout = timeout
        self._checked: bool | None = None

    @property
    def available(self) -> bool:
        if self._checked is not None:
            return self._checked
        try:
            with urllib.request.urlopen(self._url + "/api/tags", timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))
            names = {m.get("name", "") for m in data.get("models", [])}
            self._checked = any(n == self._model or n.startswith(self._model + ":")
                                or n.split(":")[0] == self._model.split(":")[0] for n in names)
        except Exception:
            self._checked = False
        return self._checked

    def refine(self, text: str, *, language: str, mode: Mode, keep: list[str] | None = None) -> str:
        """Rewrite ``text``. ``keep`` = exact names/brands to leave unchanged.

        When the engine calls this after its protector, entities are already
        masked as ALL-CAPS code words; the prompt tells the model to leave any
        such codes untouched. When called from the batch with ``keep`` (no
        masking), it tells the model to preserve those names directly.
        """
        if not text.strip():
            return text
        lang = _LANG_NAMES.get(str(language), "the same language")
        style = _MODE_STYLE.get(str(mode), "a natural tone")
        keep_line = ""
        if keep:
            names = "; ".join(k for k in keep if k and k.strip())
            if names:
                keep_line = f"Keep these names exactly as written, unchanged: {names}. "
        prompt = (
            f"You rewrite app-store descriptions. Rewrite the TEXT in {lang}, in {style}. "
            "Keep the same meaning and every fact; do NOT invent features, numbers or names. "
            "Make the wording original (do not copy the original phrasing) but accurate, "
            "and keep roughly the same length. "
            f"{keep_line}"
            "Leave URLs, numbers, prices, any HTML tags, and any ALL-CAPS code words unchanged. "
            "Do not add emojis or hashtags. "
            "Reply with ONLY the rewritten text — no preamble, no quotes, no notes, no labels.\n\n"
            f"TEXT:\n{text}"
        )
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 700},
        }
        try:
            req = urllib.request.Request(
                self._url + "/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=self._timeout) as r:
                out = json.loads(r.read().decode("utf-8"))
            result = (out.get("response") or "").strip()
        except Exception:
            return text  # never break the pipeline; keep the input on any error
        if not result:
            return text
        # Safety: if the model dropped a protected placeholder, keep the original.
        if set(_PROT_RE.findall(text)) - set(_PROT_RE.findall(result)):
            return text
        return result
