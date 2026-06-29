#!/usr/bin/env python
"""Demo del motor de reescritura: procesa texto en español e inglés.

    python examples/demo.py
"""

from rewrite_engine import RewriteEngine, RewriteRequest

EXAMPLES = [
    # (texto, idioma, modo, intensidad)
    ("Este producto es bueno y barato, cómpralo ahora.", "es", "marketplace", 0.4),
    ("Necesito ayuda para arreglar este error en mi sitio web.", "es", "formal", 0.5),
    ("I need help to fix this error fast.", "en", "professional", 0.5),
    ("Visita https://ejemplo.com — el precio es $1,299.00 con 50% de descuento.", "es", "natural", 0.6),
    ("<p>El <b>rápido</b> zorro es bueno y barato.</p>", "es", "natural", 0.6),
    ("Este suplemento cura enfermedades.", "es", "natural", 0.5),
]


def main() -> None:
    engine = RewriteEngine()
    print(
        f"embeddings={engine._scorer.uses_embeddings} "
        f"wordnet={engine._synonyms.has_lexical_source}\n"
    )
    for text, lang, mode, strength in EXAMPLES:
        result = engine.rewrite(
            RewriteRequest(
                text=text, language=lang, mode=mode, strength=strength,
                return_alternatives=2,
            )
        )
        print("─" * 72)
        print("IN  :", result.original)
        print("OUT :", result.rewritten)
        print(
            f"      [lang={result.language} mode={result.mode} "
            f"sim={result.similarity_score:.2f} read={result.readability_score:.2f} "
            f"changed={len(result.changed_words)}]"
        )
        for alt in result.alternatives:
            print("  alt:", alt)
        for w in result.warnings:
            print("   ! ", w)


if __name__ == "__main__":
    main()
