# Contributing

## Getting started

```bash
git clone https://github.com/puneethkotha/humanizer-workbench
cd humanizer-workbench
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=your_key_here
```

## Running tests

Unit tests (no API key required):

```bash
pytest tests/ -m "not integration"
```

Integration tests (requires API key):

```bash
pytest tests/ -m integration
```

All tests:

```bash
pytest tests/
```

## Linting and formatting

```bash
ruff check src/ tests/
ruff format src/ tests/
mypy src/
```

## What to work on

The best contributions at this stage:

**Detectors** — The current lexical and structural detectors cover common patterns but miss some. Adding more structural patterns (question-then-answer openers, paragraph-length uniformity) or expanding the vocabulary list is low-risk and high-value.

**Style presets** — New styles need to produce meaningfully different output, not just different system prompts. If you add a style, include examples of what the voice sounds like and tests that validate the preset fields.

**Scoring calibration** — The scorer's thresholds were set against a small test set. Better calibration against a larger corpus of AI-generated and human-written text would improve reliability.

**Chunking for long texts** — Long documents (> 2000 words) should be split into chunks, processed independently, and reassembled. The engine currently warns but doesn't split.

## Pull request guidelines

- One concern per PR. Don't combine a new style with scoring changes.
- Unit tests for all new code.
- Update `CHANGELOG.md` under `[Unreleased]`.
- The CI must pass before merging.

## Adding a new style preset

1. Define a `StylePreset` in `src/humanizer/styles/presets.py`
2. Add a `StyleName` entry in `src/humanizer/core/models.py`
3. Register it in `STYLE_REGISTRY`
4. Add tests in `tests/unit/test_styles.py`

The style's `voice_description`, `structural_guidance`, and `vocabulary_guidance` fields drive the prompt. Make them specific and substantive — "write conversationally" is not useful guidance; "use contractions, mix short and long sentences, trust the reader" is.

## Adding a new detector

1. Subclass `BaseDetector` in `src/humanizer/detectors/`
2. Implement `detect()` returning a `DetectionResult`
3. Add it to the `CompositeDetector` instantiation in `engine.py`
4. Add tests in `tests/unit/test_detectors.py` with positive and negative cases

## Reporting issues

Include:
- The input text (or a representative sample)
- The style and intensity used
- The actual output
- What you expected

If the issue is scoring-related, include the before and after scores and the component breakdown (run with `--score --explain`).
