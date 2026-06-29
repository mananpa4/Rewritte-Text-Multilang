"""Tests de tokenización sin pérdida."""

import pytest

from rewrite_engine.lang.tokenizer import TokenizerLemmatizer


@pytest.mark.parametrize(
    ("lang", "text"),
    [
        ("zh", "快速产品很好"),
        ("ja", "高速テスト良好"),
        ("th", "สินค้าเร็วดี"),
    ],
)
def test_segmenta_scripts_sin_espacios_sin_perder_texto(lang, text):
    tokenizer = TokenizerLemmatizer(use_spacy=False)
    spans = tokenizer.spans(text, lang=lang)

    assert "".join(span.text for span in spans) == text
    assert sum(1 for span in spans if span.kind == "word") > 1


def test_segmentacion_mantiene_tokens_protegidos_atomicos():
    tokenizer = TokenizerLemmatizer(use_spacy=False)
    text = "快速PROTECTEDTOKEN12X产品"
    spans = tokenizer.spans(text, lang="zh")

    assert "".join(span.text for span in spans) == text
    assert [span.text for span in spans if span.kind == "prot"] == ["PROTECTEDTOKEN12X"]
