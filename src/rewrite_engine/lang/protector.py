"""Protección y restauración de entidades.

Sustituye temporalmente por tokens seguros todo lo que NO debe reescribirse:
URLs, emails, teléfonos, fechas, precios, porcentajes, SKUs/códigos, hashtags,
menciones, HTML, markdown, además de marcas y palabras protegidas por el
usuario. Al final restaura cada token por su valor exacto original.

Implementación de una sola pasada: se construye una única regex con
alternativas en orden de prioridad y se reemplaza de izquierda a derecha. Como
los tokens insertados no se reescanean, una entidad ya protegida nunca vuelve a
emparejarse (evita corrupción por solapamiento).
"""

from __future__ import annotations

import regex as re

from rewrite_engine.core.models import ProtectedTerm

# Token sentinela. Sobrevive a la tokenización por \w+ (solo letras/dígitos/_)
# y, al usarse una única pasada, nunca se vuelve a emparejar.
_TOKEN = "PROTECTEDTOKEN{idx}X"

# Patrones en ORDEN DE PRIORIDAD (el primero que casa en una posición gana).
# Cada entrada: (kind, patrón). Se combinan en una sola regex con grupos.
_PATTERNS: list[tuple[str, str]] = [
    ("html", r"<[^>]+>"),
    ("md_image", r"!\[[^\]]*\]\([^)]*\)"),
    ("md_link", r"\[[^\]]*\]\([^)]*\)"),
    ("code_block", r"```[\s\S]*?```"),
    ("code_inline", r"`[^`]+`"),
    ("url", r"(?:https?://|www\.)[^\s<>\"')\]]+"),
    ("email", r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    ("mention", r"@\w+"),
    ("hashtag", r"#\w+"),
    # Precio: símbolo + número, o número + código/símbolo de moneda.
    ("price", r"(?:[$£€¥₡₱]\s?\d[\d.,]*|\d[\d.,]*\s?(?:USD|EUR|MXN|GBP|JPY|BRL|ARS|COP|CLP|PEN)\b|\d[\d.,]*\s?[$£€¥₡₱])"),
    ("percent", r"\d+(?:[.,]\d+)?\s?%"),
    # Fecha numérica (dd/mm/yyyy, yyyy-mm-dd y variantes) o ISO con hora.
    ("date", r"\b\d{1,4}[/-]\d{1,2}[/-]\d{1,4}(?:[T ]\d{2}:\d{2}(?::\d{2})?)?\b"),
    # Teléfono: opcional +, al menos 7 dígitos con separadores comunes.
    ("phone", r"\+?\d(?:[\d\s().\-]{5,}\d)"),
    # SKU/código: token con al menos una letra y un dígito (p.ej. ABC-123, iPhone15).
    ("code", r"\b(?=[\w-]*\d)(?=[\w-]*[A-Za-z])[\w-]{2,}\b"),
    # Número suelto (miles/decimales).
    ("number", r"\b\d[\d.,]*\b"),
]

_FLAGS = re.IGNORECASE


class TextProtector:
    """Enmascara y restaura entidades que no deben reescribirse."""

    def __init__(self, brands: list[str] | None = None) -> None:
        self._brands = [b for b in (brands or []) if b.strip()]

    def protect(
        self, text: str, *, extra_terms: list[str] | None = None
    ) -> tuple[str, list[ProtectedTerm]]:
        """Devuelve (texto_enmascarado, lista_de_términos_protegidos)."""
        terms: list[ProtectedTerm] = []
        counter = {"i": 0}

        # Las marcas y keywords del usuario tienen máxima prioridad: se anteponen
        # como un grupo 'keyword' construido dinámicamente.
        keywords = sorted(
            {*(self._brands), *(extra_terms or [])},
            key=len,
            reverse=True,  # frases largas antes que cortas
        )
        groups: list[tuple[str, str]] = []
        if keywords:
            kw_pattern = "|".join(re.escape(k) for k in keywords if k.strip())
            if kw_pattern:
                groups.append(("keyword", kw_pattern))
        groups.extend(_PATTERNS)

        combined = "|".join(
            f"(?P<{name}>{pat})" for name, pat in groups
        )
        pattern = re.compile(combined, _FLAGS)

        def _replace(match: "re.Match") -> str:
            kind = match.lastgroup or "entity"
            original = match.group()
            token = _TOKEN.format(idx=counter["i"])
            counter["i"] += 1
            terms.append(ProtectedTerm(token=token, original=original, kind=kind))
            return token

        masked = pattern.sub(_replace, text)
        return masked, terms

    @staticmethod
    def restore(text: str, terms: list[ProtectedTerm]) -> str:
        """Restaura cada token por su valor original exacto.

        Restaura en orden inverso de creación por robustez (por si un original
        contuviera, hipotéticamente, otro token).
        """
        for term in reversed(terms):
            text = text.replace(term.token, term.original)
        return text

    @staticmethod
    def is_token(word: str) -> bool:
        """True si ``word`` es (o contiene) un token protegido."""
        return "PROTECTEDTOKEN" in word
