"""Concordancia morfológica: reflexiona un reemplazo para que concuerde en
género/número/tiempo con la palabra original, usando los rasgos que expone
spaCy (``token.morph``).

Sin esto, el motor sustituye por la forma base del diccionario tal cual —
p.ej. "bonita" (femenino) se reemplazaba por "hermoso" (masculino) en vez de
"hermosa". Es la misma idea que ``lang/esperanto.py:reinflect_eo``, pero por
idioma: cada uno tiene sus propias reglas de flexión y su propio nivel de
riesgo.

Alcance deliberado (para no arriesgar resultados peores que no reflexionar):

- **Adjetivos y sustantivos** (género + número): reglas de sufijo, seguras y de
  alto impacto — cubren la gran mayoría de casos comunes en es/pt/it/fr.
- **Verbos**: sólo se conjuga el **presente de indicativo, 3ª persona**
  (singular/plural) con las terminaciones regulares -ar/-er/-ir (y sus
  equivalentes en pt/it/fr) — es el tiempo/persona más frecuente en texto
  declarativo. Se elige deliberadamente NO intentar otros tiempos/modos ni
  verbos con cambio de raíz (o→ue, e→ie, etc.): sin una tabla de irregulares,
  una conjugación equivocada sonaría peor que dejar el reemplazo sin
  flexionar. Cuando no se puede conjugar con confianza, se devuelve el
  reemplazo tal cual (comportamiento actual, sin regresión).
- **Alemán**: la declinación de adjetivos alemana depende del artículo que la
  precede (fuerte/débil/mixta) — demasiado compleja para reglas de sufijo
  seguras. Se extraen los rasgos (por si una capa futura los usa) pero no se
  reflexiona nada; el reemplazo queda como lo entrega el diccionario.
- **Inglés**: sin género; sólo aplica el plural regular de sustantivos
  (-s/-es) y una conjugación mínima de verbos (presente 3ª sing. -s, pasado
  regular -ed).
"""

from __future__ import annotations

from dataclasses import dataclass

# Terminaciones de infinitivo reconocidas por idioma, en orden de prueba
# (más larga primero para no confundir -er con -re, etc. donde aplique).
_VERB_ENDINGS: dict[str, tuple[str, ...]] = {
    "es": ("ar", "er", "ir"),
    "pt": ("ar", "er", "ir"),
    "it": ("are", "ere", "ire"),
    "fr": ("er", "ir", "re"),
}

# Terminación regular de presente indicativo, 3ª persona, por infinitivo y
# número. Índice: idioma -> terminación_infinitivo -> (singular, plural).
_PRESENT_3RD: dict[str, dict[str, tuple[str, str]]] = {
    "es": {"ar": ("a", "an"), "er": ("e", "en"), "ir": ("e", "en")},
    "pt": {"ar": ("a", "am"), "er": ("e", "em"), "ir": ("e", "em")},
    "it": {"are": ("a", "ano"), "ere": ("e", "ono"), "ire": ("e", "ono")},
    "fr": {"er": ("e", "ent"), "ir": ("it", "issent"), "re": ("", "ent")},
}


@dataclass(frozen=True)
class MorphFeatures:
    """Rasgos morfológicos relevantes de un token (subconjunto de UD Morph)."""

    gender: str | None = None  # "Masc" | "Fem" | "Neut"
    number: str | None = None  # "Sing" | "Plur"
    tense: str | None = None  # "Pres" | "Past" | "Fut" | ...
    person: str | None = None  # "1" | "2" | "3"
    mood: str | None = None  # "Ind" | "Sub" | "Imp" | ...

    @property
    def is_empty(self) -> bool:
        return not any((self.gender, self.number, self.tense, self.person, self.mood))

    @staticmethod
    def from_dict(morph: dict[str, str]) -> "MorphFeatures":
        return MorphFeatures(
            gender=morph.get("Gender"),
            number=morph.get("Number"),
            tense=morph.get("Tense"),
            person=morph.get("Person"),
            mood=morph.get("Mood"),
        )


def reinflect(word: str, replacement: str, pos: str, features: MorphFeatures, lang: str) -> str:
    """Reflexiona ``replacement`` (forma base del diccionario) para que
    concuerde con los rasgos morfológicos de ``word`` (el original).

    Si no hay rasgos útiles, el idioma no tiene reglas, o la operación no es
    segura (p.ej. verbo irregular sospechoso), devuelve ``replacement`` sin
    tocar — nunca degrada el comportamiento actual.
    """
    if features.is_empty or not replacement:
        return replacement

    if pos in ("ADJ", "NOUN"):
        return _reinflect_nominal(replacement, features, pos, lang)
    if pos == "VERB":
        return _reinflect_verb(replacement, features, lang)
    return replacement


# -- nominal: género + número --------------------------------------------


def _reinflect_nominal(word: str, features: MorphFeatures, pos: str, lang: str) -> str:
    # El género sólo se reflexiona en ADJETIVOS: un adjetivo concuerda en
    # género con el sustantivo que modifica. El género de un SUSTANTIVO es una
    # propiedad léxica fija, no algo que deba "concordar" con nada — dos
    # sustantivos sinónimos pueden tener géneros distintos legítimamente
    # (es. "ayuda" fem. / "apoyo" masc.), así que forzar el género de un
    # sustantivo de reemplazo produciría palabras incorrectas o inventadas.
    if pos == "ADJ":
        if lang in ("es", "pt"):
            word = _apply_gender_o_a(word, features.gender)
        elif lang == "it":
            word = _apply_gender_o_a_it(word, features.gender)
        elif lang == "fr":
            word = _apply_gender_fr(word, features.gender)

    if lang in ("es", "pt", "it"):
        return _apply_plural_romance(word, features.number, lang)
    if lang == "fr":
        return _apply_plural_fr(word, features.number)
    if lang == "en":
        return _apply_plural_en(word, features.number)
    return word  # de y otros: sin reglas seguras (ver docstring del módulo)


def _apply_gender_o_a(word: str, gender: str | None) -> str:
    """es/pt: variación -o/-a más común (bueno/buena, económico/económica)."""
    if gender == "Fem" and word.endswith("o"):
        return word[:-1] + "a"
    if gender == "Masc" and word.endswith("a") and not word.endswith(("ista", "ma")):
        return word[:-1] + "o"
    return word


def _apply_gender_o_a_it(word: str, gender: str | None) -> str:
    """it: variación -o/-a (buono/buona); -e es común de género (grande)."""
    if gender == "Fem" and word.endswith("o"):
        return word[:-1] + "a"
    if gender == "Masc" and word.endswith("a") and not word.endswith("ista"):
        return word[:-1] + "o"
    return word


def _apply_gender_fr(word: str, gender: str | None) -> str:
    """fr: femenino regular añade -e (grand/grande); no toca si ya termina en -e."""
    if gender == "Fem" and not word.endswith("e"):
        return word + "e"
    return word


def _apply_plural_romance(word: str, number: str | None, lang: str) -> str:
    if number != "Plur" or word.endswith("s"):
        return word
    if lang == "es" and word[-1:] in "aeiou":
        return word + "s"
    if lang == "es":
        return word + "es"
    if lang == "pt":
        if word.endswith(("r", "z")):
            return word + "es"
        if word.endswith("l"):
            return word[:-1] + "is"
        return word + "s"
    if lang == "it":
        if word.endswith("o"):
            return word[:-1] + "i"
        if word.endswith("a"):
            return word[:-1] + "e"
        if word.endswith("e"):
            return word[:-1] + "i"
        return word
    return word


def _apply_plural_fr(word: str, number: str | None) -> str:
    if number != "Plur" or word.endswith(("s", "x")):
        return word
    return word + "s"


def _apply_plural_en(word: str, number: str | None) -> str:
    if number != "Plur" or word.endswith("s"):
        return word
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if word.endswith("y") and word[-2:-1] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


# -- verbos: sólo presente indicativo, 3ª persona ------------------------


def _reinflect_verb(word: str, features: MorphFeatures, lang: str) -> str:
    if lang == "en":
        return _reinflect_verb_en(word, features)
    if lang not in _VERB_ENDINGS:
        return word

    if features.tense != "Pres" or features.mood not in (None, "Ind") or features.person != "3":
        return word  # fuera del caso seguro: no arriesgar una conjugación incorrecta

    endings = _VERB_ENDINGS[lang]
    ending = next((e for e in endings if word.endswith(e)), None)
    if ending is None:
        return word  # no es un infinitivo reconocible (o ya viene conjugado)

    stem = word[: -len(ending)]
    sing, plur = _PRESENT_3RD[lang][ending]
    return stem + (plur if features.number == "Plur" else sing)


def _reinflect_verb_en(word: str, features: MorphFeatures) -> str:
    if features.tense == "Past":
        if word.endswith("e"):
            return word + "d"
        return word + "ed"
    if features.tense == "Pres" and features.person == "3" and features.number != "Plur":
        if word.endswith(("s", "x", "z", "ch", "sh", "o")):
            return word + "es"
        if word.endswith("y") and word[-2:-1] not in "aeiou":
            return word[:-1] + "ies"
        return word + "s"
    return word
