#!/usr/bin/env python3
"""Batch-rewrite dowdes.com app descriptions OFFLINE.

Bridge between dowdes.com (PHP) and this engine. Reads the JSON exported by
`php artisan appvault:rewrite-export` and writes a JSON consumable by
`php artisan appvault:rewrite-import`. No API keys, no tokens, $0.

Two rewrite backends:

  --transformer ollama   (RECOMMENDED) a local Ollama LLM rewrites the text.
        Free + offline + publishable quality. Bypasses the dictionary stage and
        only uses the engine's entity protection (URLs/prices/brands/HTML stay
        intact) + an embeddings faithfulness check. Prereq:
            ollama serve && ollama pull qwen2.5:3b

  --transformer dict     the offline dictionary/WordNet engine (fast, but on real
        app descriptions it produces wrong-sense swaps — kept only for testing).

Usage:
    python scripts/batch_rewrite.py --in rewrite_export.json --out rewrite_rewritten.json \
        --transformer ollama --ollama-model qwen2.5:3b --min-similarity 0.80

Round-trip (run the artisan steps from the dowdes.com root):
    php artisan appvault:rewrite-export --lang=en,es --only-new --with-package
    python <engine>/scripts/batch_rewrite.py --in  storage/app/appvault/rewrite_export.json \
                                              --out storage/app/appvault/rewrite_rewritten.json \
                                              --transformer ollama
    php artisan appvault:rewrite-import storage/app/appvault/rewrite_rewritten.json --dry-run
    php artisan appvault:rewrite-import storage/app/appvault/rewrite_rewritten.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")
_URL_RE = re.compile(r"https?://\S+")


def _preserves_markup(orig: str, new: str) -> bool:
    """True unless the rewrite dropped HTML tags or URLs the original had."""
    if set(_TAG_RE.findall(orig)) - set(_TAG_RE.findall(new)):
        return False
    if set(_URL_RE.findall(orig)) - set(_URL_RE.findall(new)):
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Offline batch rewriter for dowdes.com exports")
    ap.add_argument("--in", dest="inp", required=True, help="export JSON from appvault:rewrite-export")
    ap.add_argument("--out", dest="out", required=True, help="output JSON for appvault:rewrite-import")
    ap.add_argument("--transformer", choices=["ollama", "dict"], default="ollama",
                    help="rewrite backend (default: ollama = local LLM)")
    ap.add_argument("--ollama-model", default="qwen2.5:3b", help="Ollama model name")
    ap.add_argument("--ollama-url", default=None, help="Ollama base URL (default http://localhost:11434)")
    ap.add_argument("--mode", default="marketplace", help="rewrite mode/tone (default: marketplace)")
    ap.add_argument("--strength", type=float, default=0.4, help="dict backend only: 0.1..0.9 (default 0.4)")
    ap.add_argument("--min-similarity", type=float, default=0.80,
                    help="skip a field if semantic similarity drops below this (0 disables)")
    ap.add_argument("--limit", type=int, default=0, help="max items to process (0 = all)")
    args = ap.parse_args()

    src = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    items = src.get("items", [])
    if args.limit:
        items = items[: args.limit]

    rewrite_field = _make_ollama(args) if args.transformer == "ollama" else _make_dict(args)

    out_items: list[dict] = []
    n_fields = 0
    for idx, it in enumerate(items, 1):
        lang = it.get("lang") or "auto"
        preserve = [v for v in (it.get("title", ""), it.get("developer", "")) if v]
        new_fields: dict[str, str] = {}
        meta: dict[str, dict] = {}

        for field, text in (it.get("fields") or {}).items():
            text = "" if text is None else str(text)
            if not text.strip():
                continue
            new_text, sim, info = rewrite_field(text, lang, args.mode, preserve)
            if args.min_similarity and sim is not None and sim < args.min_similarity:
                meta[field] = {"skipped_low_similarity": round(sim, 3)}
                continue
            if new_text.strip() == text.strip():
                meta[field] = {"unchanged": True}
                continue
            new_fields[field] = new_text
            meta[field] = {"similarity": (round(sim, 3) if sim is not None else None), **info}
            n_fields += 1

        if new_fields:
            out_items.append({
                "ref": it.get("ref"), "table": it.get("table"), "pk": it.get("pk"),
                "app_id": it.get("app_id"), "lang": lang, "fields": new_fields, "_meta": meta,
            })
        if idx % 25 == 0:
            print(f"  ...{idx}/{len(items)} items", file=sys.stderr)

    payload = {"schema": "appvault-rewrite/1", "transformer": args.transformer,
               "mode": args.mode, "items": out_items}
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rewrote {n_fields} fields across {len(out_items)} items -> {args.out}")
    return 0


def _make_ollama(args):
    """Ollama path: LLM rewrite (names/HTML preserved via the prompt) + similarity check.

    No entity masking here — LLMs corrupt mask tokens, so we instead tell the
    model to keep the app name/developer, URLs, numbers and HTML unchanged, and
    verify faithfulness with an embeddings similarity score.
    """
    from rewrite_engine.rewrite.scorer import ContextScorer
    from rewrite_engine.transformers.ollama import OllamaTransformer

    transformer = OllamaTransformer(model=args.ollama_model, url=args.ollama_url)
    if not transformer.available:
        sys.exit(f"ERROR: Ollama model '{args.ollama_model}' not reachable. "
                 f"Run:  ollama serve  &&  ollama pull {args.ollama_model}")
    scorer = ContextScorer()  # embeddings if installed, else lexical proxy

    def run(text, lang, mode, preserve):
        refined = transformer.refine(text, language=lang, mode=mode, keep=preserve)
        # Safety: if the rewrite dropped HTML tags or URLs (common on HTML
        # `details`), keep the original for that field rather than degrade it.
        if not _preserves_markup(text, refined):
            return text, None, {"backend": "ollama", "kept_original_markup": True}
        sim = scorer.similarity(text, refined)
        return refined, sim, {"backend": "ollama"}

    return run


def _make_dict(args):
    """Dictionary/WordNet engine path (legacy/testing)."""
    from rewrite_engine import RewriteEngine, RewriteRequest

    engine = RewriteEngine()

    def run(text, lang, mode, preserve):
        res = engine.rewrite(RewriteRequest(
            text=text, language=lang, mode=mode, strength=args.strength,
            preserve_keywords=preserve,
        ))
        return res.rewritten, res.similarity_score, {"changed": len(res.changed_words),
                                                      "warnings": res.warnings}

    return run


if __name__ == "__main__":
    sys.exit(main())
