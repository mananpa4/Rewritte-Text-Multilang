"""Metadatos lingüísticos compartidos por el motor.

Mantener aquí los idiomas de primera clase evita que config, detector,
tokenizador y filtros léxicos se desalineen al ampliar cobertura.
"""

from __future__ import annotations

# Idiomas con soporte sembrado: diccionario local + heurísticas de seguridad.
DEFAULT_LANGUAGES = (
    "es", "en", "pt", "fr", "it", "de", "nl", "pl", "ru", "uk", "sv", "eo",
)

LANGUAGE_ALIASES: dict[str, str] = {
    "en-us": "en",
    "en-gb": "en",
    "es-mx": "es",
    "es-es": "es",
    "pt-br": "pt",
    "pt-pt": "pt",
    "fr-fr": "fr",
    "de-de": "de",
    "nl-nl": "nl",
    "pl-pl": "pl",
    "ru-ru": "ru",
    "uk-ua": "uk",
    "sv-se": "sv",
    "zh-cn": "zh",
    "zh-tw": "zh",
    "zh-hans": "zh",
    "zh-hant": "zh",
    "ja-jp": "ja",
    "th-th": "th",
}


def normalize_language_code(lang: str | None, default: str = "en") -> str:
    """Normaliza códigos tipo ``es-MX`` a ISO-639-1 base cuando procede."""
    raw = (lang or "").strip().lower().replace("_", "-")
    if not raw:
        return default
    if raw in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[raw]
    base = raw.split("-", 1)[0]
    return LANGUAGE_ALIASES.get(base, base)


def normalize_language_list(
    languages: tuple[str, ...] | list[str],
    *,
    fallback: tuple[str, ...] = DEFAULT_LANGUAGES,
) -> tuple[str, ...]:
    """Normaliza una lista de idiomas, preservando orden y eliminando duplicados."""
    seen: list[str] = []
    for lang in languages:
        code = normalize_language_code(str(lang), default="")
        if code and code not in seen:
            seen.append(code)
    return tuple(seen) if seen else fallback


# Palabras muy frecuentes por idioma, para el fallback sin langdetect.
STOPWORD_HINTS: dict[str, frozenset[str]] = {
    "es": frozenset({
        "el", "la", "los", "las", "de", "que", "y", "en", "un", "una",
        "por", "con", "para", "es", "su", "lo", "como", "más", "pero", "este",
    }),
    "en": frozenset({
        "the", "of", "and", "to", "in", "a", "is", "that", "it", "for",
        "on", "with", "as", "are", "this", "be", "by", "an", "or", "not",
    }),
    "pt": frozenset({
        "o", "a", "os", "as", "de", "que", "e", "em", "um", "uma",
        "por", "com", "para", "não", "se", "do", "da", "mais", "como", "mas",
    }),
    "fr": frozenset({
        "le", "la", "les", "de", "que", "et", "en", "un", "une", "pour",
        "avec", "est", "ce", "qui", "ne", "pas", "sur", "plus", "des", "du",
    }),
    "it": frozenset({
        "il", "la", "le", "di", "che", "e", "in", "un", "una", "per",
        "con", "è", "non", "si", "del", "della", "come", "più", "ma", "su",
    }),
    "de": frozenset({
        "der", "die", "das", "und", "in", "zu", "den", "mit", "ist", "von",
        "ein", "eine", "für", "auf", "nicht", "dem", "des", "im", "auch", "als",
    }),
    "nl": frozenset({
        "de", "het", "een", "en", "van", "in", "op", "voor", "met", "is",
        "zijn", "dat", "die", "dit", "niet", "aan", "te", "om", "als", "maar",
    }),
    "pl": frozenset({
        "i", "w", "na", "z", "do", "że", "to", "jest", "nie", "się",
        "dla", "po", "jak", "ale", "oraz", "ten", "ta", "te", "może", "czy",
    }),
    "ru": frozenset({
        "и", "в", "во", "не", "что", "он", "на", "я", "с", "со",
        "как", "а", "то", "все", "она", "так", "его", "но", "да", "для",
    }),
    "uk": frozenset({
        "і", "й", "в", "у", "не", "що", "на", "я", "з", "із",
        "як", "це", "а", "але", "для", "та", "він", "вона", "ми", "ви",
    }),
    "sv": frozenset({
        "och", "i", "att", "det", "som", "en", "ett", "är", "på", "för",
        "med", "av", "inte", "den", "de", "har", "till", "om", "men", "från",
    }),
    "eo": frozenset({
        "la", "kaj", "de", "en", "al", "por", "kun", "mi", "vi", "li",
        "estas", "ne", "ke", "tiu", "ĉi", "pri", "el", "ĝi", "ni", "aŭ",
    }),
}

# Palabras función que NO deben reemplazarse cuando no hay POS fiable.
FUNCTION_WORDS: dict[str, frozenset[str]] = {
    "es": frozenset({
        "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del",
        "al", "a", "ante", "con", "en", "para", "por", "sin", "sobre", "tras",
        "y", "e", "o", "u", "que", "se", "su", "sus", "lo", "le", "les",
        "me", "te", "nos", "es", "son", "fue", "ser", "está", "están", "ya",
        "no", "sí", "más", "como", "pero", "este", "esta", "esto", "estos",
        "estas", "ese", "esa", "mi", "tu",
    }),
    "en": frozenset({
        "the", "a", "an", "of", "to", "in", "on", "for", "with", "as", "at",
        "by", "from", "and", "or", "but", "nor", "so", "yet", "is", "are",
        "was", "were", "be", "been", "being", "this", "that", "these", "those",
        "it", "its", "he", "she", "they", "we", "you", "i", "not", "no",
        "yes", "do", "does", "did", "have", "has", "had", "will", "would",
        "can", "could", "my", "your",
    }),
    "pt": frozenset({
        "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
        "no", "na", "em", "para", "por", "com", "sem", "sobre", "e", "ou",
        "que", "se", "seu", "sua", "lhe", "me", "te", "nos", "é", "são",
        "foi", "ser", "já", "não", "sim", "mais", "como", "mas", "este",
        "esta", "isso", "meu", "teu",
    }),
    "fr": frozenset({
        "le", "la", "les", "un", "une", "des", "de", "du", "au", "aux", "à",
        "en", "dans", "pour", "par", "avec", "sans", "sur", "et", "ou", "que",
        "qui", "se", "son", "sa", "ses", "ne", "pas", "est", "sont", "été",
        "être", "ce", "cet", "cette", "ces", "il", "elle", "ils", "nous",
        "vous", "je", "plus",
    }),
    "it": frozenset({
        "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "del",
        "della", "a", "al", "in", "nel", "per", "con", "su", "tra", "fra",
        "e", "o", "che", "si", "suo", "sua", "non", "è", "sono", "era",
        "essere", "questo", "questa", "ma", "più", "come", "lui", "lei", "noi",
        "voi", "mi", "ti",
    }),
    "de": frozenset({
        "der", "die", "das", "ein", "eine", "einen", "dem", "den", "des", "und",
        "oder", "aber", "in", "an", "auf", "für", "mit", "von", "zu", "bei",
        "aus", "ist", "sind", "war", "sein", "nicht", "kein", "dieser", "diese",
        "dieses", "ich", "du", "er", "sie", "es", "wir", "ihr", "mehr", "als",
        "wie", "im",
    }),
    "nl": frozenset({
        "de", "het", "een", "en", "of", "maar", "want", "dat", "die", "dit",
        "deze", "voor", "met", "zonder", "op", "in", "aan", "van", "naar",
        "te", "om", "als", "is", "zijn", "was", "waren", "niet", "geen", "ik",
        "jij", "je", "hij", "zij", "we", "wij", "u", "mijn", "jouw",
    }),
    "pl": frozenset({
        "i", "oraz", "lub", "ale", "że", "to", "ten", "ta", "te", "w", "we",
        "na", "z", "ze", "do", "od", "po", "dla", "bez", "przez", "o", "jest",
        "są", "był", "była", "nie", "tak", "się", "ja", "ty", "on", "ona",
        "my", "wy", "ich", "mój", "twój",
    }),
    "ru": frozenset({
        "и", "или", "но", "а", "что", "это", "этот", "эта", "эти", "в", "во",
        "на", "с", "со", "к", "ко", "от", "до", "для", "без", "по", "о", "об",
        "из", "за", "у", "есть", "был", "была", "были", "не", "да", "нет", "я",
        "ты", "он", "она", "мы", "вы", "они", "мой", "твой",
    }),
    "uk": frozenset({
        "і", "й", "або", "але", "що", "це", "цей", "ця", "ці", "в", "у", "на",
        "з", "із", "до", "від", "для", "без", "по", "про", "є", "був", "була",
        "були", "не", "так", "ні", "я", "ти", "він", "вона", "ми", "ви", "вони",
        "мій", "твій",
    }),
    "sv": frozenset({
        "och", "eller", "men", "att", "som", "det", "den", "de", "denna",
        "detta", "en", "ett", "i", "på", "för", "med", "utan", "av", "till",
        "från", "om", "är", "var", "vara", "har", "hade", "inte", "ingen",
        "jag", "du", "han", "hon", "vi", "ni", "min", "din",
    }),
    "eo": frozenset({
        "la", "kaj", "aŭ", "sed", "ke", "ne", "de", "en", "al", "por",
        "kun", "sur", "pri", "el", "mi", "vi", "li", "ŝi", "ĝi", "ni",
        "ili", "estas", "esti", "se", "ĉu", "tiu", "tio", "min", "sia", "do",
    }),
}

# Intensificadores: se dejan intactos para evitar sustituciones forzadas.
INTENSIFIERS: dict[str, frozenset[str]] = {
    "es": frozenset({
        "muy", "tan", "demasiado", "bastante", "realmente", "sumamente", "casi",
        "tanto", "muchísimo",
    }),
    "en": frozenset({
        "very", "really", "quite", "rather", "too", "so", "just", "pretty",
        "highly", "extremely", "incredibly", "absolutely", "totally",
    }),
    "pt": frozenset({"muito", "bastante", "demais", "realmente", "tão", "quase"}),
    "fr": frozenset({"très", "trop", "vraiment", "assez", "plutôt", "si", "tellement"}),
    "it": frozenset({"molto", "troppo", "davvero", "abbastanza", "piuttosto", "così"}),
    "de": frozenset({"sehr", "zu", "wirklich", "ziemlich", "recht", "so", "äußerst"}),
    "nl": frozenset({"heel", "erg", "zeer", "echt", "best", "vrij", "nogal", "te", "zo"}),
    "pl": frozenset({
        "bardzo", "naprawdę", "dość", "zbyt", "tak", "całkiem", "wyjątkowo",
        "prawie",
    }),
    "ru": frozenset({
        "очень", "действительно", "довольно", "слишком", "так", "почти",
        "крайне", "совсем",
    }),
    "uk": frozenset({
        "дуже", "справді", "доволі", "занадто", "так", "майже", "вкрай",
        "зовсім",
    }),
    "sv": frozenset({
        "mycket", "väldigt", "riktigt", "ganska", "för", "så", "nästan",
        "otroligt",
    }),
    "eo": frozenset({
        "tre", "tro", "sufiĉe", "plej", "pli", "tute", "vere", "preskaŭ",
    }),
}

SPACY_MODELS: dict[str, str] = {
    "es": "es_core_news_sm",
    "en": "en_core_web_sm",
    "pt": "pt_core_news_sm",
    "fr": "fr_core_news_sm",
    "it": "it_core_news_sm",
    "de": "de_core_news_sm",
    "nl": "nl_core_news_sm",
    "pl": "pl_core_news_sm",
    "ru": "ru_core_news_sm",
    "uk": "uk_core_news_sm",
    "sv": "sv_core_news_sm",
}

# ISO-639-1 -> código OMW/ISO-639-3 usado por NLTK WordNet.
WORDNET_LANGS: dict[str, str] = {
    "en": "eng",
    "es": "spa",
    "pt": "por",
    "fr": "fra",
    "it": "ita",
    "de": "deu",
    "nl": "nld",
    "pl": "pol",
    "ru": "rus",
    "uk": "ukr",
    "sv": "swe",
}

# Idiomas/escrituras sin separación por espacios. No son idiomas de primera
# clase aún; esta lista sólo activa segmentación conservadora cuando se fuerzan
# explícitamente o se testea el tokenizer.
SEGMENTED_SCRIPT_LANGS: frozenset[str] = frozenset({"zh", "ja", "th"})
