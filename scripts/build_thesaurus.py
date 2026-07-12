#!/usr/bin/env python
"""Convierte un tesauro de texto plano a un diccionario JSON del motor.

Formato de entrada (una entrada por línea):

    palabra; sinónimo1, sinónimo2, sinónimo3, ...

Fuente usada: ``repos/repos-new/sinonimos.txt`` (tesauro español, ~3556 voces).
Genera ``data/dictionaries/<lang>/thesaurus.json`` en el formato que consume
``DictSource`` (que carga TODOS los .json del idioma y los fusiona por lema).

Reglas de calidad:
- sólo sinónimos de una palabra (evita sustituciones multipalabra inseguras);
- normaliza a minúsculas (corrige mayúsculas sueltas de la fuente);
- descarta el propio lema y duplicados;
- estima la frecuencia con ``wordfreq`` si está disponible (los sinónimos más
  comunes rankean mejor → resultado más natural).

    python scripts/build_thesaurus.py repos/repos-new/sinonimos.txt \
        --lang es --out data/dictionaries/es/thesaurus.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

_WORD_RE = re.compile(r"^[\p{L}]+$" if False else r"^[a-záéíóúüñ]+$", re.IGNORECASE)


def _load_freq():
    try:
        from wordfreq import zipf_frequency

        return zipf_frequency
    except ImportError:
        return None


def parse(text: str, lang: str) -> list[dict]:
    freq = _load_freq()
    entries: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or ";" not in line:
            continue
        head, _, tail = line.partition(";")
        word = head.strip().lower()
        if not word or " " in word or not _WORD_RE.match(word):
            continue

        seen: set[str] = set()
        synonyms: list[dict] = []
        for chunk in tail.split(","):
            syn = chunk.strip().lower()
            # Descarta multipalabra, el propio lema, vacíos y repetidos.
            if not syn or " " in syn or syn == word or syn in seen:
                continue
            if not _WORD_RE.match(syn) or len(syn) < 3:
                continue
            seen.add(syn)
            frequency = 0.5
            if freq is not None:
                try:
                    frequency = round(max(0.0, min(1.0, freq(syn, lang) / 8.0)), 3)
                except Exception:
                    frequency = 0.5
            synonyms.append(
                {"text": syn, "formality": "neutral", "frequency": frequency, "contexts": []}
            )
        if synonyms:
            entries.append(
                {"word": word, "lemma": word, "pos": "", "language": lang, "synonyms": synonyms}
            )
    return entries


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path, help="Tesauro de texto plano (palabra; sinónimos)")
    ap.add_argument("--lang", default="es", help="Código ISO del idioma")
    ap.add_argument("--out", type=Path, required=True, help="JSON de salida")
    args = ap.parse_args()

    entries = parse(args.source.read_text(encoding="utf-8", errors="ignore"), args.lang)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    total_syn = sum(len(e["synonyms"]) for e in entries)
    print(f"OK → {args.out}  ({len(entries)} voces, {total_syn} sinónimos)")


if __name__ == "__main__":
    main()
