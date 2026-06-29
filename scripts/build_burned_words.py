#!/usr/bin/env python
"""Convierte HUMAN-AI/shared/burned-words.md a data/ai_markers/burned_words.json.

Parsea las secciones por idioma ("## Idioma (xx)") y sus subsecciones
("### Burned words", "### Empty intensifiers") en listas. Útil para regenerar o
ampliar el dataset de marcadores de IA a partir del recurso original (MIT).

    python scripts/build_burned_words.py \
        repos/HumanAI-main/shared/burned-words.md \
        --out data/ai_markers/burned_words.generated.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

_LANG_HEADER = re.compile(r"^##\s+.*\(([a-z]{2})\)", re.IGNORECASE)
_SUBSECTION = re.compile(r"^###\s+(.*)$")


def _split_terms(line: str) -> list[str]:
    # Elimina aclaraciones entre paréntesis y separa por comas.
    line = re.sub(r"\([^)]*\)", "", line)
    return [t.strip().lower() for t in line.split(",") if t.strip()]


def parse(md: str) -> dict:
    words: dict[str, list[str]] = {}
    intensifiers: dict[str, list[str]] = {}
    universal: list[str] = []

    lang: str | None = None
    section: str | None = None
    in_universal = False

    for raw in md.splitlines():
        line = raw.strip()
        m = _LANG_HEADER.match(line)
        if m:
            lang = m.group(1).lower()
            section = None
            in_universal = False
            words.setdefault(lang, [])
            intensifiers.setdefault(lang, [])
            continue
        if line.lower().startswith("## universal"):
            in_universal = True
            lang = None
            section = None
            continue
        sub = _SUBSECTION.match(line)
        if sub:
            section = sub.group(1).lower()
            continue
        if not line or line.startswith(("#", ">", "---", "|")):
            continue

        terms = _split_terms(line)
        if not terms:
            continue
        if in_universal:
            universal.extend(terms)
        elif lang and (section is None or "burned" in (section or "")):
            words[lang].extend(terms)
        elif lang and "intensifier" in (section or ""):
            intensifiers[lang].extend(terms)

    # dedup preservando orden
    def dedup(seq: list[str]) -> list[str]:
        return list(dict.fromkeys(seq))

    return {
        "universal": dedup(universal),
        "words": {k: dedup(v) for k, v in words.items() if v},
        "intensifiers": {k: dedup(v) for k, v in intensifiers.items() if v},
        "fillers": {},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path, help="Ruta a burned-words.md")
    ap.add_argument("--out", type=Path, required=True, help="JSON de salida")
    args = ap.parse_args()

    data = parse(args.source.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    langs = ", ".join(sorted(data["words"]))
    print(f"OK → {args.out}  (idiomas: {langs}; universal: {len(data['universal'])})")


if __name__ == "__main__":
    main()
