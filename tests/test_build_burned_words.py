from __future__ import annotations

from scripts.build_burned_words import merge


def test_merge_preserva_curados_y_agrega_idiomas():
    base = {
        "_note": "curado",
        "universal": ["robust"],
        "words": {"es": ["robusto"]},
        "intensifiers": {},
        "fillers": {},
    }
    generated = {
        "universal": ["robust", "seamless"],
        "words": {"es": ["integral"], "uk": ["інноваційний"]},
        "intensifiers": {},
        "fillers": {},
    }

    result = merge(base, generated)

    assert result["universal"] == ["robust", "seamless"]
    assert result["words"]["es"] == ["robusto", "integral"]
    assert result["words"]["uk"] == ["інноваційний"]
