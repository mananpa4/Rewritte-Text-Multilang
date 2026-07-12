"""Paráfrasis neuronal opcional vía un modelo T5 ligero de HuggingFace.

Etapa de refinado **opt-in**: por defecto el motor usa ``NullTransformer``
(100% offline, misma calidad para los 12 idiomas). Este transformer añade una
pasada de parafraseo neuronal con un T5 pequeño — pero **sólo para inglés**:
los modelos T5 de parafraseo disponibles públicamente son monolingües en
inglés, así que en cualquier otro idioma esta etapa se salta sin tocar el
texto (no hay degradación silenciosa: se comunica en la UI/CLI).

El modelo se descarga una sola vez a la caché de HuggingFace
(``~/.cache/huggingface/hub``) y luego corre 100% localmente: no hace falta
alojarlo en ningún servidor propio ni hay llamadas de red en cada uso.

Requiere el extra ``[ai-paraphrase]`` (transformers + torch + sentencepiece).
Degrada con gracia si no está instalado o si la carga falla (``available``
queda en False y ``refine`` es un no-op).
"""

from __future__ import annotations

import regex as re

from rewrite_engine.core.models import Mode
from rewrite_engine.transformers.base import BaseTransformer
from rewrite_engine.transformers._guards import is_safe_candidate

# Modelo por defecto: T5-small (~240 MB), el más ligero y probado de los
# parafraseadores públicos en inglés. Alternativa de mayor calidad (más lenta
# y pesada, ~850 MB): "Ateeqq/Text-Rewriter-Paraphraser".
DEFAULT_MODEL = "mrm8488/t5-small-finetuned-quora-for-paraphrasing"

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Por oración: si el texto es más largo que esto, se deja sin refinar (evita
# generaciones lentas o degeneradas en párrafos largos).
_MAX_SENTENCE_CHARS = 400


class T5ParaphraserTransformer(BaseTransformer):
    """Parafraseador T5 ligero, sólo-inglés, con guardas de seguridad.

    Decisión de diseño: se usa *beam search determinista*
    (``do_sample=False, num_beams=4``) en vez del muestreo con temperatura que
    sugiere la tarjeta del modelo, para respetar el principio de determinismo
    del proyecto (misma entrada → misma salida, sin ``random``).
    """

    def __init__(self, model_name: str = DEFAULT_MODEL, *, device: str | None = None) -> None:
        self._model_name = model_name
        self._tokenizer = None
        self._model = None
        self._torch = None
        self._device = device
        self._load_error: str | None = None
        self._load(device)

    def _load(self, device: str | None) -> None:
        try:
            import torch
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self._model_name)
            resolved_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
            model = model.to(resolved_device)
            model.eval()

            self._tokenizer = tokenizer
            self._model = model
            self._torch = torch
            self._device = resolved_device
        except Exception as exc:  # noqa: BLE001 - se reporta vía load_error
            self._load_error = str(exc)
            self._tokenizer = None
            self._model = None

    @property
    def available(self) -> bool:
        return self._model is not None

    @property
    def load_error(self) -> str | None:
        """Motivo de fallo de carga, si lo hubo (para mostrar al usuario)."""
        return self._load_error

    @property
    def model_name(self) -> str:
        return self._model_name

    def refine(self, text: str, *, language: str, mode: Mode) -> str:
        if self._model is None or language != "en":
            return text  # sólo-inglés; en cualquier otro idioma, no-op

        sentences = [s for s in _SENT_SPLIT.split(text) if s.strip()]
        if not sentences:
            return text

        out_sentences = []
        for sentence in sentences:
            if len(sentence) > _MAX_SENTENCE_CHARS:
                out_sentences.append(sentence)
                continue
            paraphrased = self._paraphrase_one(sentence)
            out_sentences.append(paraphrased if paraphrased else sentence)
        candidate = " ".join(out_sentences)

        if not is_safe_candidate(text, candidate):
            return text  # guarda de seguridad: descarta si es sospechoso
        return candidate

    def _paraphrase_one(self, sentence: str) -> str | None:
        try:
            input_text = f"paraphrase: {sentence}"
            enc = self._tokenizer.encode_plus(
                input_text, return_tensors="pt", truncation=True, max_length=256,
            )
            enc = {k: v.to(self._device) for k, v in enc.items()}
            with self._torch.no_grad():
                out_ids = self._model.generate(
                    **enc,
                    max_length=256,
                    num_beams=4,
                    do_sample=False,
                    early_stopping=True,
                )
            decoded = self._tokenizer.decode(out_ids[0], skip_special_tokens=True)
            return decoded.strip()
        except Exception:
            return None
