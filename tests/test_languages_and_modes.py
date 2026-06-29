"""Tests de idiomas y modos (prompt: tests 6-12)."""

import pytest

from rewrite_engine.core.config import EngineConfig
from rewrite_engine.lang.detector import LanguageDetector


def test_reescribe_espanol(rewrite):
    """Test 6."""
    r = rewrite("Necesito ayuda para arreglar este error.", language="es", mode="formal", strength=0.6)
    assert r.language == "es"
    assert r.rewritten != r.original
    # ayuda -> apoyo/asistencia (diccionario formal)
    assert "apoyo" in r.rewritten or "asistencia" in r.rewritten


def test_reescribe_ingles(rewrite):
    """Test 7."""
    r = rewrite("I need help to fix this error.", language="en", mode="formal", strength=0.6)
    assert r.language == "en"
    assert r.rewritten != r.original
    assert "support" in r.rewritten or "assistance" in r.rewritten


def test_reescribe_portugues(rewrite):
    """Test 8."""
    r = rewrite("Preciso de ajuda boa e barata.", language="pt", mode="formal", strength=0.6)
    assert r.language == "pt"
    assert r.rewritten != r.original


def test_deteccion_automatica_idioma(rewrite):
    r = rewrite("This is a good and cheap product for everyone.", language="auto", strength=0.5)
    assert r.language == "en"


def test_modo_formal_prefiere_formalidad(rewrite):
    """Test 9: el modo formal elige sinónimos formales."""
    r = rewrite("Necesito ayuda buena.", language="es", mode="formal", strength=0.7)
    assert "apoyo" in r.rewritten or "asistencia" in r.rewritten


def test_modo_informal(rewrite):
    """Test 10."""
    r = rewrite("Voy a comprar esto.", language="es", mode="informal", strength=0.7)
    # 'llevar' es la opción informal de 'comprar'; al menos no debe fallar.
    assert isinstance(r.rewritten, str) and r.rewritten


def test_modo_marketplace(rewrite):
    """Test 11."""
    r = rewrite("Este producto es bueno y barato.", language="es", mode="marketplace", strength=0.6)
    assert r.mode.value == "marketplace"
    assert r.rewritten != r.original


def test_modo_seo(rewrite):
    """Test 12."""
    r = rewrite("Esta guía es buena y fácil de leer.", language="es", mode="seo", strength=0.6)
    assert r.mode.value == "seo"
    assert isinstance(r.rewritten, str)


def test_modo_grammar_only_no_cambia_lexico(rewrite):
    """grammar_only no debe sustituir palabras por sinónimos."""
    r = rewrite("Este producto es bueno y barato.", language="es", mode="grammar_only", strength=0.9)
    assert len(r.changed_words) == 0


@pytest.mark.parametrize(
    ("lang", "text", "expected"),
    [
        ("nl", "Ik zoek hulp voor deze fout.", ("ondersteuning", "assistentie")),
        ("pl", "Szukam pomoc przy błąd.", ("wsparcie", "asysta")),
        ("ru", "Нужна помощь при ошибка.", ("поддержка", "содействие")),
        ("uk", "Потрібна допомога при помилка.", ("підтримка", "сприяння")),
        ("sv", "Jag söker hjälp med detta fel.", ("stöd", "assistans")),
    ],
)
def test_reescribe_idiomas_nuevos(rewrite, lang, text, expected):
    r = rewrite(text, language=lang, mode="formal", strength=0.9)
    assert r.language == lang
    assert r.rewritten != r.original
    assert any(word in r.rewritten.lower() for word in expected)


@pytest.mark.parametrize(
    ("lang", "text"),
    [
        ("nl", "Dit is een goede gids en het is nuttig voor iedereen."),
        ("pl", "To jest dobry tekst i nie jest trudny dla czytelnika."),
        ("ru", "Это хороший текст и он не сложный для читателя."),
        ("uk", "Це добрий текст і він не складний для читача."),
        ("sv", "Det här är en bra text och den är inte svår för läsaren."),
    ],
)
def test_heuristica_detecta_idiomas_nuevos(lang, text):
    detector = LanguageDetector(("nl", "pl", "ru", "uk", "sv"), default="nl")
    detector._impl = None
    assert detector.detect(text).language == lang


def test_config_normaliza_aliases_de_idioma():
    cfg = EngineConfig(
        languages=("es-MX", "EN-us", "nl-NL", "es"),
        default_language="EN-GB",
    )
    assert cfg.languages == ("es", "en", "nl")
    assert cfg.default_language == "en"


@pytest.mark.parametrize(
    ("lang", "text", "expected"),
    [
        ("nl", "verzending aanbieding duurzaam comfortabel", ("actie", "prettig")),
        ("pl", "wysyłka oferta trwały wygodny", ("promocja", "komfortowy")),
        ("ru", "доставка предложение прочный удобный", ("акция", "комфортный")),
        ("uk", "доставка пропозиція міцний зручний", ("акція", "комфортний")),
        ("sv", "frakt erbjudande hållbar bekväm", ("kampanj", "komfortabel")),
    ],
)
def test_diccionarios_marketplace_idiomas_nuevos(rewrite, lang, text, expected):
    r = rewrite(text, language=lang, mode="marketplace", strength=0.9)
    assert r.language == lang
    assert r.rewritten != r.original
    assert any(word in r.rewritten.lower() for word in expected)


@pytest.mark.parametrize(
    ("lang", "text", "expected"),
    [
        ("nl", "snel installatie", ("configuratie", "setup")),
        ("pl", "szybki konfiguracja", ("ustawienie", "parametryzacja")),
        ("ru", "быстрый настройка", ("конфигурация", "параметризация")),
        ("uk", "швидкий налаштування", ("конфігурація", "параметризація")),
        ("sv", "snabb konfiguration", ("inställning", "uppsättning")),
    ],
)
def test_diccionarios_tecnicos_idiomas_nuevos(rewrite, lang, text, expected):
    r = rewrite(text, language=lang, mode="technical", strength=0.9)
    assert r.language == lang
    assert r.rewritten != r.original
    assert any(word in r.rewritten.lower() for word in expected)
