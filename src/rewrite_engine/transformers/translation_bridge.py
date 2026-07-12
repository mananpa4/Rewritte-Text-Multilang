"""Puente de traducción: extiende un transformer inglés-only a los 12 idiomas.

``T5ParaphraserTransformer`` (y cualquier otro backend "sólo inglés") sólo
mejora texto en inglés. Este transformer lo envuelve y lo hace funcionar en
**cualquier idioma soportado**: traduce el texto al inglés, aplica el
transformer interno, y traduce el resultado de vuelta al idioma original.

Modelos: `Helsinki-NLP/opus-mt-<lang>-en` / `opus-mt-en-<lang>` (arquitectura
MarianMT). Se eligieron sobre otras alternativas evaluadas por una combinación
de motivos verificados, no supuestos:

- **Licencia Apache-2.0** (permisiva) — a diferencia de ``facebook/nllb-200-
  distilled-600M`` (Meta), que es **CC BY-NC 4.0, no comercial** y por tanto
  incompatible con el resto del stack de este proyecto (todo lo demás es
  MIT/Apache/BSD; ver README §Licencias).
- **Sin código remoto de terceros**: la tokenización es la ``MarianTokenizer``
  nativa de ``transformers``. La alternativa ``alirezamsh/small100`` (MIT,
  también ligera) requiere cargar un ``tokenization_small100.py`` con
  ``trust_remote_code=True`` — un riesgo de cadena de suministro que se evita
  aquí a propósito.
- **Un modelo por idioma** (~300 MB c/u, se cargan sólo bajo demanda) en vez
  de un único modelo masivo: más liviano en el caso común (la mayoría de
  sesiones usan 1–2 idiomas), aunque implica más descargas si se usan muchos
  idiomas en la misma sesión.
- Verificado que cubre incluso Esperanto (``opus-mt-eo-en``), el idioma menos
  común de los 12 soportados.

``google/mt5-small`` (mT5) **no se usa**: su propia tarjeta de modelo declara
que sólo se preentrenó con el objetivo de corrupción de spans (sin ninguna
tarea supervisada) y "debe afinarse (fine-tune) antes de poder usarse en una
tarea downstream" — conectarlo tal cual para parafraseo produciría texto sin
sentido. No existe un fine-tune de mT5 para paráfrasis multilenguaje fiable y
mantenido que cubra los 12 idiomas de este proyecto (se revisaron los
candidatos en HuggingFace: son proyectos experimentales monolingües con muy
poca adopción). El puente de traducción logra el mismo objetivo — reescritura
con IA en cualquier idioma — apoyándose en modelos que sí están validados para
su tarea.

**Limitación verificada (no una suposición):** un round-trip de traducción
"limpio" reconstruye el original con fidelidad (verificado manualmente:
ES→EN→ES sin ningún paso intermedio reproduce el texto original exacto). Pero
si el texto que llega a este transformer ya viene con una sustitución de
sinónimo cuestionable de la capa léxica offline (ruido de WordNet, ver
``synonyms/wordnet_source.py`` y el README §Limitaciones), la traducción la
propaga fielmente en ambos idiomas — no la introduce, pero tampoco la corrige.
Se comprobó además que ni la puerta de similitud léxica ni la de **embeddings
reales** (``[semantic]``, umbral ≥0.88) detectan de forma fiable este patrón
concreto (sustituir un verbo por otro relacionado pero distinto, p.ej.
"cierra"→"bloquea"): ambas miden similitud temática/estructural de la frase
completa, no corrección de una sola palabra, así que una frase con un verbo
equivocado puede seguir puntuando muy alto. Es una limitación conocida de la
similitud a nivel de oración en general, no algo que este transformer pueda
arreglar por sí solo.
"""

from __future__ import annotations

import regex as re

from rewrite_engine.core.models import Mode
from rewrite_engine.transformers._guards import is_safe_candidate
from rewrite_engine.transformers.base import BaseTransformer

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_MAX_SENTENCE_CHARS = 400


class TranslationBridgeTransformer(BaseTransformer):
    """Envuelve un ``BaseTransformer`` inglés-only y lo extiende a cualquier
    idioma vía traducción ida y vuelta (MarianMT, Helsinki-NLP/opus-mt).

    Uso:
        bridge = TranslationBridgeTransformer(inner=T5ParaphraserTransformer())
        engine.set_transformer(bridge)   # ahora la IA aplica a los 12 idiomas
    """

    def __init__(self, inner: BaseTransformer, *, device: str | None = None) -> None:
        self._inner = inner
        self._device = device
        self._torch = None
        # lang -> (tok_a_en, modelo_a_en, tok_de_en, modelo_de_en) | None si falló
        self._pairs: dict[str, tuple | None] = {}

    @property
    def available(self) -> bool:
        return self._inner.available

    @property
    def inner(self) -> BaseTransformer:
        return self._inner

    def refine(self, text: str, *, language: str, mode: Mode) -> str:
        if language == "en":
            return self._inner.refine(text, language=language, mode=mode)
        if not self._inner.available:
            return text

        pair = self._load_pair(language)
        if pair is None:
            return text  # sin modelo para este idioma: no-op seguro

        to_en_tok, to_en_model, from_en_tok, from_en_model = pair
        try:
            english = self._translate(text, to_en_tok, to_en_model)
            refined_en = self._inner.refine(english, language="en", mode=mode)
            back = self._translate(refined_en, from_en_tok, from_en_model)
        except Exception:
            return text

        if not is_safe_candidate(text, back):
            return text
        return back

    # -- carga perezosa de los modelos de traducción -------------------------

    def _load_pair(self, lang: str):
        if lang in self._pairs:
            return self._pairs[lang]
        try:
            import torch
            from transformers import MarianMTModel, MarianTokenizer

            self._torch = torch
            device = self._device or ("cuda" if torch.cuda.is_available() else "cpu")

            to_en_name = f"Helsinki-NLP/opus-mt-{lang}-en"
            from_en_name = f"Helsinki-NLP/opus-mt-en-{lang}"

            to_en_tok = MarianTokenizer.from_pretrained(to_en_name)
            to_en_model = MarianMTModel.from_pretrained(to_en_name).to(device).eval()
            from_en_tok = MarianTokenizer.from_pretrained(from_en_name)
            from_en_model = MarianMTModel.from_pretrained(from_en_name).to(device).eval()

            pair = (to_en_tok, to_en_model, from_en_tok, from_en_model)
        except Exception:
            pair = None
        self._pairs[lang] = pair
        return pair

    # -- traducción -----------------------------------------------------------

    def _translate(self, text: str, tokenizer, model) -> str:
        sentences = [s for s in _SENT_SPLIT.split(text) if s.strip()]
        if not sentences:
            return text
        out = []
        for sentence in sentences:
            if len(sentence) > _MAX_SENTENCE_CHARS:
                out.append(sentence)
                continue
            out.append(self._translate_one(sentence, tokenizer, model))
        return " ".join(out)

    def _translate_one(self, sentence: str, tokenizer, model) -> str:
        device = next(model.parameters()).device
        enc = tokenizer(sentence, return_tensors="pt", truncation=True, max_length=256)
        enc = {k: v.to(device) for k, v in enc.items()}
        with self._torch.no_grad():
            out_ids = model.generate(**enc, max_length=256, num_beams=4)
        return tokenizer.decode(out_ids[0], skip_special_tokens=True).strip()
