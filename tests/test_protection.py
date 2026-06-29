"""Tests de protección de entidades (prompt: tests 1-4, 13, 19)."""

import pytest


def test_urls_no_cambian(rewrite):
    """Test 1: las URLs nunca se modifican."""
    url = "https://www.ejemplo.com/path?x=1&y=2"
    r = rewrite(f"Visita {url} para más información buena.", language="es", strength=0.9)
    assert url in r.rewritten
    assert url in r.protected_terms


def test_precios_no_cambian(rewrite):
    """Test 2: los precios no se modifican."""
    r = rewrite("El producto bueno cuesta $1,299.00 y está barato.", language="es", strength=0.9)
    assert "$1,299.00" in r.rewritten


def test_porcentajes_y_skus_no_cambian(rewrite):
    r = rewrite("Bueno: 50% de descuento en el SKU ABC-123 ahora.", language="es", strength=0.9)
    assert "50%" in r.rewritten
    assert "ABC-123" in r.rewritten


def test_emails_no_cambian(rewrite):
    r = rewrite("Escribe a hola@ejemplo.com si necesitas ayuda buena.", language="es", strength=0.9)
    assert "hola@ejemplo.com" in r.rewritten


def test_nombres_propios_no_cambian(rewrite):
    """Test 3: nombres propios (mayúscula a media frase) se preservan."""
    r = rewrite("Compré una casa buena en Madrid con María y Pedro.", language="es", strength=0.9)
    assert "Madrid" in r.rewritten
    assert "María" in r.rewritten
    assert "Pedro" in r.rewritten


def test_marcas_protegidas_no_cambian(rewrite):
    """Test 4: marcas configuradas se preservan."""
    r = rewrite("Compra bueno en Amazon y MercadoLibre hoy.", language="es", strength=0.9)
    assert "Amazon" in r.rewritten
    assert "MercadoLibre" in r.rewritten


def test_preserve_keywords(rewrite):
    r = rewrite(
        "El producto de Mananpa Labs es bueno.",
        language="es", strength=0.9, preserve_keywords=["Mananpa Labs"],
    )
    assert "Mananpa Labs" in r.rewritten


def test_html_intacto(rewrite):
    """Test 13a: el HTML no se rompe; las etiquetas se conservan."""
    html = "<p>El <b>rápido</b> zorro marrón es bueno y barato.</p>"
    r = rewrite(html, language="es", strength=0.8)
    assert r.rewritten.count("<p>") == 1
    assert r.rewritten.count("</p>") == 1
    assert "<b>" in r.rewritten and "</b>" in r.rewritten


def test_markdown_intacto(rewrite):
    """Test 13b: los enlaces markdown no se rompen."""
    md = "Mira [este enlace](https://ejemplo.com) que es bueno."
    r = rewrite(md, language="es", strength=0.8)
    assert "](https://ejemplo.com)" in r.rewritten


def test_palabras_prohibidas_no_aparecen(rewrite):
    """Test 19: avoid_words no deben aparecer en la salida."""
    r = rewrite(
        "Este producto es bueno.",
        language="es", mode="marketplace", strength=0.9,
        avoid_words=["excelente"],
    )
    assert "excelente" not in r.rewritten.lower()
