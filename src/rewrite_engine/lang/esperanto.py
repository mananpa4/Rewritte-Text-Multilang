"""Lematizador por reglas para Esperanto (eo).

Esperanto es un idioma construido *súper regular* (16 reglas, sin irregulares),
lo que permite lematizar con reglas simples en vez de un modelo estadístico
(simplemma/spaCy no cubren eo). Basado en la morfología descrita por
``repos/repos-new/esperanto-analyzer``:

- Sustantivos terminan en ``-o``; adjetivos en ``-a``; adverbios en ``-e``.
- Plural: ``-j``; acusativo: ``-n`` (pueden combinarse: ``-ojn``, ``-ajn``).
- Verbos: infinitivo ``-i``, presente ``-as``, pasado ``-is``, futuro ``-os``,
  condicional ``-us``, volitivo/imperativo ``-u``.

La lematización reduce las flexiones a la forma base (quita acusativo y plural,
y lleva los verbos al infinitivo). No unifica clases de palabra distintas
(``rapida`` adjetivo vs ``rapide`` adverbio), que son entradas separadas.
"""

from __future__ import annotations

# Palabras cortas/correlativos que no deben desflexionarse.
_KEEP = frozenset(
    {"la", "kaj", "aŭ", "sed", "ke", "ne", "jes", "ĉu", "se", "do", "ja", "nur"}
)

_VERB_TENSES = ("as", "is", "os", "us")


def lemmatize_eo(word: str) -> str:
    """Devuelve el lema (forma base) de una palabra en Esperanto."""
    w = word.lower()
    if w in _KEEP or len(w) <= 3:
        return w

    # Acusativo (-n) y plural (-j), en ese orden (raíz + terminación + j + n).
    if w.endswith("n"):
        w = w[:-1]
    if w.endswith("j"):
        w = w[:-1]

    # Verbos conjugados -> infinitivo -i.
    if len(w) > 3:
        if w[-2:] in _VERB_TENSES:
            return w[:-2] + "i"
        if w.endswith("u"):
            return w[:-1] + "i"

    return w


def reinflect_eo(original: str, replacement: str) -> str:
    """Aplica al ``replacement`` (forma base del diccionario) la misma flexión
    que tenía el ``original``, aprovechando la regularidad de Esperanto.

    - Verbos (``replacement`` en ``-i``): copia el tiempo del original
      (``-as/-is/-os/-us/-u``).
    - Nominales (``-o/-a/-e``): reaplica plural ``-j`` y acusativo ``-n``.

    Así ``helpon`` (acusativo) + base ``subteno`` → ``subtenon``, y ``bonajn``
    + base ``eminenta`` → ``eminentajn``.
    """
    o = original.lower()
    r = replacement.lower()
    if not r:
        return replacement

    # Verbo: replacement es infinitivo (termina en -i).
    if r.endswith("i") and len(r) > 2:
        if o[-2:] in _VERB_TENSES:
            return r[:-1] + o[-2:]
        if o.endswith("u") and len(o) > 3:
            return r[:-1] + "u"
        return r

    # Nominal (sustantivo -o, adjetivo -a, adverbio -e): plural + acusativo.
    if r[-1] in "oae":
        stem = o
        accusative = stem.endswith("n")
        if accusative:
            stem = stem[:-1]
        plural = stem.endswith("j")
        return r + ("j" if plural else "") + ("n" if accusative else "")

    return replacement
