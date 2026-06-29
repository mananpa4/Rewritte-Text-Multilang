"""Interfaz de línea de comandos del motor de reescritura.

    rewrite-engine "Este producto es bueno y barato." --lang es --mode marketplace
    rewrite-engine input.txt --mode formal --strength 0.5 --output out.txt
    echo "Buy this now." | rewrite-engine - --lang en

El argumento INPUT puede ser: una ruta a un archivo, ``-`` para stdin, o el
propio texto literal.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from rewrite_engine.core.engine import RewriteEngine
from rewrite_engine.core.models import Mode, RewriteRequest
from rewrite_engine.lang.metadata import DEFAULT_LANGUAGES


def _read_input(value: str) -> str:
    if value == "-":
        return sys.stdin.read()
    path = Path(value)
    try:
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except OSError:
        pass
    return value  # texto literal


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input", required=True)
@click.option(
    "-l",
    "--lang",
    default="auto",
    help=f"Idioma (auto, {', '.join(DEFAULT_LANGUAGES)}).",
)
@click.option(
    "-m", "--mode",
    type=click.Choice([m.value for m in Mode]),
    default="natural", help="Modo de reescritura.",
)
@click.option("-s", "--strength", type=float, default=0.35, help="Intensidad 0.1–0.9.")
@click.option("-a", "--alternatives", type=int, default=0, help="Nº de alternativas a generar.")
@click.option("--preserve", multiple=True, help="Palabra/frase a no cambiar (repetible).")
@click.option("--avoid", multiple=True, help="Palabra que no debe aparecer (repetible).")
@click.option("--locale", default=None, help="Variante regional, p.ej. es-MX.")
@click.option("--json", "as_json", is_flag=True, help="Salida JSON completa.")
@click.option("--explain", is_flag=True, help="Muestra métricas y avisos por stderr.")
@click.option("-o", "--output", type=click.Path(), default=None, help="Escribe la salida a un archivo.")
def main(
    input: str,
    lang: str,
    mode: str,
    strength: float,
    alternatives: int,
    preserve: tuple[str, ...],
    avoid: tuple[str, ...],
    locale: str | None,
    as_json: bool,
    explain: bool,
    output: str | None,
) -> None:
    """Reescribe texto de forma natural y multilenguaje."""
    text = _read_input(input)
    engine = RewriteEngine()
    result = engine.rewrite(
        RewriteRequest(
            text=text, language=lang, mode=mode, strength=strength,
            preserve_keywords=list(preserve), avoid_words=list(avoid),
            return_alternatives=alternatives, locale=locale,
        )
    )

    if as_json:
        rendered = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    else:
        rendered = result.rewritten

    if output:
        Path(output).write_text(rendered + ("\n" if not as_json else ""), encoding="utf-8")
        click.echo(f"Escrito en {output}", err=True)
    else:
        click.echo(rendered)
        if not as_json and result.alternatives:
            click.echo("\nAlternativas:", err=True)
            for alt in result.alternatives:
                click.echo(f"  - {alt}", err=True)

    if explain:
        click.echo(
            f"\n[lang={result.language} mode={result.mode} "
            f"sim={result.similarity_score:.3f} read={result.readability_score:.3f} "
            f"changed={len(result.changed_words)}]",
            err=True,
        )
        for w in result.warnings:
            click.echo(f"  ! {w}", err=True)


if __name__ == "__main__":
    main()
