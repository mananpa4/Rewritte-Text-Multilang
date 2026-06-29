#!/usr/bin/env python3
"""Batch-rewrite dowdes.com app descriptions OFFLINE.

Bridge between dowdes.com (PHP) and this engine. Reads the JSON exported by
`php artisan appvault:rewrite-export` and writes a JSON consumable by
`php artisan appvault:rewrite-import`. Runs the full offline engine
(dictionaries + WordNet/OMW if installed) — no API keys, no tokens, $0.

Usage:
    python scripts/batch_rewrite.py \
        --in  rewrite_export.json \
        --out rewrite_rewritten.json \
        --mode marketplace --strength 0.4

Full round-trip (run from the dowdes.com root for the artisan steps):
    php artisan appvault:rewrite-export --lang=en --with-package
    python <engine>/scripts/batch_rewrite.py \
        --in  storage/app/appvault/rewrite_export.json \
        --out storage/app/appvault/rewrite_rewritten.json
    php artisan appvault:rewrite-import storage/app/appvault/rewrite_rewritten.json --dry-run
    php artisan appvault:rewrite-import storage/app/appvault/rewrite_rewritten.json

Each item's ``title`` and ``developer`` are passed as preserve_keywords so app
and developer names are never altered. The engine auto-detects HTML in
``details`` and rewrites only visible text nodes, leaving tags intact.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rewrite_engine import RewriteEngine, RewriteRequest


def main() -> int:
    ap = argparse.ArgumentParser(description="Offline batch rewriter for dowdes.com exports")
    ap.add_argument("--in", dest="inp", required=True,
                    help="export JSON produced by appvault:rewrite-export")
    ap.add_argument("--out", dest="out", required=True,
                    help="output JSON consumed by appvault:rewrite-import")
    ap.add_argument("--mode", default="marketplace",
                    help="rewrite mode (default: marketplace)")
    ap.add_argument("--strength", type=float, default=0.4,
                    help="0.1 (light) .. 0.9 (aggressive); default 0.4")
    ap.add_argument("--min-similarity", type=float, default=0.0,
                    help="skip a field if semantic similarity drops below this (0 disables)")
    ap.add_argument("--limit", type=int, default=0, help="max items to process (0 = all)")
    args = ap.parse_args()

    src = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    items = src.get("items", [])
    if args.limit:
        items = items[: args.limit]

    engine = RewriteEngine()
    out_items: list[dict] = []
    n_fields = 0

    for it in items:
        lang = it.get("lang") or "auto"
        preserve = [v for v in (it.get("title", ""), it.get("developer", "")) if v]
        new_fields: dict[str, str] = {}
        meta: dict[str, dict] = {}

        for field, text in (it.get("fields") or {}).items():
            text = "" if text is None else str(text)
            if not text.strip():
                continue
            res = engine.rewrite(RewriteRequest(
                text=text,
                language=lang,
                mode=args.mode,
                strength=args.strength,
                preserve_keywords=preserve,
            ))
            if args.min_similarity and res.similarity_score < args.min_similarity:
                meta[field] = {"skipped_low_similarity": round(res.similarity_score, 3)}
                continue
            # Only emit fields that actually changed (import also guards this).
            if res.rewritten.strip() == text.strip():
                meta[field] = {"unchanged": True}
                continue
            new_fields[field] = res.rewritten
            meta[field] = {
                "similarity": round(res.similarity_score, 3),
                "changed": len(res.changed_words),
                "warnings": res.warnings,
            }
            n_fields += 1

        if not new_fields:
            continue
        out_items.append({
            "ref": it.get("ref"),
            "table": it.get("table"),
            "pk": it.get("pk"),
            "app_id": it.get("app_id"),
            "lang": lang,
            "fields": new_fields,
            "_meta": meta,
        })

    payload = {
        "schema": "appvault-rewrite/1",
        "mode": args.mode,
        "strength": args.strength,
        "items": out_items,
    }
    Path(args.out).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Rewrote {n_fields} fields across {len(out_items)} items -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
