from pathlib import Path

import pytest

from rewrite_engine.transformers.nllb import NLLBTranslator


def test_nllb_language_codes() -> None:
    assert NLLBTranslator.language_code("es") == "spa_Latn"
    assert NLLBTranslator.language_code("zho_Hans") == "zho_Hans"


def test_nllb_unknown_short_code() -> None:
    with pytest.raises(ValueError):
        NLLBTranslator.language_code("xx")


def test_nllb_missing_model_is_not_available(tmp_path: Path) -> None:
    translator = NLLBTranslator(tmp_path / "missing")
    assert translator.available is False
