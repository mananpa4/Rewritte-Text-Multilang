"""Traducción local NLLB-200 con CTranslate2.

La implementación sigue el patrón del proyecto MIT ``sioaeko/NLLB_translator``
sin depender de su servidor FastAPI/Next.js. Los pesos de Meta se instalan de
forma separada y conservan su licencia CC-BY-NC-4.0.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from threading import RLock
from typing import Any

from rewrite_engine.core.models import Mode
from rewrite_engine.transformers._guards import is_safe_candidate
from rewrite_engine.transformers.base import BaseTransformer


ISO_TO_FLORES = {
    "ar": "arb_Arab",
    "de": "deu_Latn",
    "en": "eng_Latn",
    "eo": "epo_Latn",
    "es": "spa_Latn",
    "fr": "fra_Latn",
    "hi": "hin_Deva",
    "id": "ind_Latn",
    "it": "ita_Latn",
    "nl": "nld_Latn",
    "pl": "pol_Latn",
    "pt": "por_Latn",
    "ru": "rus_Cyrl",
    "sv": "swe_Latn",
    "tr": "tur_Latn",
    "uk": "ukr_Cyrl",
}


class NLLBUnavailableError(RuntimeError):
    """NLLB no está instalado o no se encontró el modelo local."""


class NLLBTranslator:
    """Traductor lazy y thread-safe para un modelo NLLB convertido a CT2 int8."""

    def __init__(
        self,
        model_dir: str | Path | None = None,
        tokenizer_source: str | Path | None = None,
        *,
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        configured = model_dir or os.getenv("REWRITE_ENGINE_NLLB_DIR")
        if configured:
            self.model_dir = Path(configured)
        elif getattr(sys, "frozen", False):
            bundle = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
            self.model_dir = bundle / "models" / "nllb-200-distilled-600M-int8"
        else:
            self.model_dir = Path("models/nllb-200-distilled-600M-int8")
        self.tokenizer_source = str(tokenizer_source or self.model_dir)
        self.device = device
        self.compute_type = compute_type
        self._translator: Any | None = None
        self._tokenizer: Any | None = None
        self._lock = RLock()

    @property
    def available(self) -> bool:
        return self.model_dir.is_dir()

    def _load(self) -> tuple[Any, Any]:
        with self._lock:
            if self._translator is not None and self._tokenizer is not None:
                return self._translator, self._tokenizer
            if not self.available:
                raise NLLBUnavailableError(
                    f"No se encontró el modelo NLLB CTranslate2 en {self.model_dir}"
                )
            try:
                import ctranslate2
                from transformers import AutoTokenizer
            except ImportError as exc:
                raise NLLBUnavailableError(
                    'Instala las dependencias opcionales con pip install -e ".[nllb]"'
                ) from exc
            self._translator = ctranslate2.Translator(
                str(self.model_dir), device=self.device, compute_type=self.compute_type
            )
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.tokenizer_source, local_files_only=True
            )
            return self._translator, self._tokenizer

    @staticmethod
    def language_code(value: str) -> str:
        """Acepta ISO-639 corto o un código FLORES-200 explícito."""
        normalized = value.strip()
        if "_" in normalized:
            return normalized
        try:
            return ISO_TO_FLORES[normalized.lower()]
        except KeyError as exc:
            raise ValueError(f"Idioma NLLB no configurado: {value}") from exc

    def translate(self, text: str, source: str, target: str) -> str:
        if not text.strip() or source == target:
            return text
        source_code = self.language_code(source)
        target_code = self.language_code(target)
        translator, tokenizer = self._load()
        with self._lock:
            tokenizer.src_lang = source_code
            encoded = tokenizer(text, return_tensors="pt")
            source_tokens = tokenizer.convert_ids_to_tokens(encoded.input_ids[0])
            result = translator.translate_batch(
                [source_tokens],
                target_prefix=[[target_code]],
                beam_size=4,
                max_decoding_length=512,
            )[0]
            ids = tokenizer.convert_tokens_to_ids(result.hypotheses[0][1:])
            return tokenizer.decode(ids, skip_special_tokens=True).strip()


class NLLBBridgeTransformer(BaseTransformer):
    """Extiende un parafraseador inglés a otros idiomas mediante NLLB."""

    def __init__(self, inner: BaseTransformer, translator: NLLBTranslator | None = None) -> None:
        self.inner = inner
        self.translator = translator or NLLBTranslator()

    @property
    def available(self) -> bool:
        return self.inner.available and self.translator.available

    def refine(self, text: str, *, language: str, mode: Mode) -> str:
        if language == "en":
            return self.inner.refine(text, language="en", mode=mode)
        if not self.available:
            return text
        try:
            english = self.translator.translate(text, language, "en")
            refined = self.inner.refine(english, language="en", mode=mode)
            result = self.translator.translate(refined, "en", language)
        except Exception:
            return text
        return result if is_safe_candidate(text, result) else text
