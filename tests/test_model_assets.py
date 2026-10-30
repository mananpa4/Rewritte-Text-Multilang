from __future__ import annotations

from rewrite_engine.transformers.model_assets import model_slug, resolve_model_source


def test_model_slug_es_estable():
    assert model_slug("Ateeqq/Text-Rewriter-Paraphraser") == (
        "Ateeqq--Text-Rewriter-Paraphraser"
    )


def test_resuelve_modelo_desde_directorio_configurado(tmp_path, monkeypatch):
    model = "Org/Modelo"
    local = tmp_path / model_slug(model)
    local.mkdir()
    monkeypatch.setenv("REWRITE_ENGINE_MODELS_DIR", str(tmp_path))

    assert resolve_model_source(model) == str(local)


def test_sin_bundle_conserva_id_del_hub(tmp_path, monkeypatch):
    monkeypatch.setenv("REWRITE_ENGINE_MODELS_DIR", str(tmp_path))
    assert resolve_model_source("Org/Inexistente") == "Org/Inexistente"
