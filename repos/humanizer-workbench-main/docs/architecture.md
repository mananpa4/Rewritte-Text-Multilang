# Architecture

## Overview

humanizer-workbench is organized around a four-concern separation: detection, transformation, scoring, and orchestration. Each concern lives in its own module. The engine assembles them.

```
Input text
    │
    ▼
CompositeDetector ──────────────────────────────────────────────┐
    │                                                            │
    │  DetectionResult                                           │
    ▼                                                            │
AIScorer (before score)                                          │
    │                                                            │
    ▼                                                            │
Pipeline.for_intensity(intensity)                                │
    │                                                            │
    │  [REWRITE, REFINE, AUDIT] (depends on intensity)           │
    ▼                                                            │
LLMTransformer.transform() ──── StylePreset ─────────────────────┘
    │  (per stage)
    ▼
Updated text → CompositeDetector → AIScorer (after score)
    │
    ▼
HumanizerResult
```

## Components

### `core/models.py`

All shared data types. Keeping them in one file prevents circular imports and makes the data flow explicit. No business logic lives here.

Key types:
- `Intensity` — enum controlling pipeline length (LIGHT/MEDIUM/AGGRESSIVE)
- `StyleName` — enum of available style presets
- `PipelineStage` — enum of transformation stages (REWRITE/REFINE/AUDIT)
- `DetectionResult` — output from the composite detector
- `StageResult` — output from a single pipeline stage
- `HumanizerResult` — the complete output of a humanization run

### `core/engine.py`

The orchestrator. It owns the lifecycle of a humanization run:
1. Initial detection + scoring
2. Pipeline execution
3. Final detection + scoring
4. Result assembly

The engine has no knowledge of prompts, API calls, or style logic. It wires components together and moves data between them.

### `core/pipeline.py`

Maps intensity levels to ordered sequences of pipeline stages. A frozen dataclass — pipelines do not change during execution.

### `detectors/`

Two detectors, composed by `CompositeDetector`:

**`LexicalDetector`** — Scans for AI vocabulary and filler phrases using a curated word list and phrase list. Uses whole-word regex matching for vocabulary, substring matching for phrases.

**`StructuralDetector`** — Scans for structural patterns: sentence length uniformity, AI sentence openers, em dash overuse, rule-of-three patterns, uniform paragraph lengths. Uses regex-based sentence splitting (no NLTK/spaCy dependency).

**`CompositeDetector`** — Runs both detectors, merges and deduplicates results into a single `DetectionResult`.

### `styles/`

**`StylePreset`** — Frozen dataclass defining a writing style's behavioral contract: voice, tone, structural guidance, vocabulary guidance, and stage-specific instructions.

**`presets.py`** — The six built-in styles: casual, professional, technical, founder, academic, storytelling. Each meaningfully differs in structure, vocabulary, and persona.

**`STYLE_REGISTRY`** — Dict mapping `StyleName` → `StylePreset`. Adding a new style is one dict entry plus a `StylePreset` definition.

### `transformers/`

**`BaseTransformer`** — Abstract interface. Takes text + context, returns `StageResult`.

**`LLMTransformer`** — Calls the Anthropic API. Each pipeline stage uses a distinct prompt strategy:

- `REWRITE`: Full transformation prompt with style voice, vocabulary guidance, intensity instructions, and detected patterns. Temperature: 0.7.
- `REFINE`: Lighter prompt focused on rhythm and sentence-level naturalness. Temperature: 0.45.
- `AUDIT`: Minimal prompt for final sanity check. Temperature: 0.3.

The transformer strips common LLM preambles ("Here is the rewritten text:") before returning output. Changes are inferred programmatically from detection results, not from asking the LLM to summarize its own changes (LLM self-reporting of changes is unreliable).

### `scoring/`

**`AIScorer`** — Five-component heuristic scorer producing a 0–100 score:

| Component | Max | Signal |
|-----------|-----|--------|
| AI vocabulary density | 30 | Words/total word ratio |
| Filler phrase density | 25 | Distinct phrases found |
| Sentence length uniformity | 20 | Inverted std dev of sentence lengths |
| Structural patterns | 15 | Structural flag count |
| AI sentence openers | 10 | Opener pattern matches in first 5 sentences |

The score is a diagnostic tool, not a classifier. It guides the humanization process and shows improvement; it is not designed to make binary "AI vs. human" judgments.

### `cli/`

**`main.py`** — Click-based CLI. Thin layer: translates command-line arguments into engine calls, formats output using Rich.

Two commands:
- `humanizer` — the main transformation command (default entry point)
- `humanizer detect` — analyze a file for AI patterns without transforming

## Data Flow

Each pipeline stage receives:
- The text output from the previous stage (or original text for REWRITE)
- The `StylePreset` for the chosen style
- The `DetectionResult` from the most recent detector run
- The `Intensity` level

The engine re-runs detection before the AUDIT stage to give it accurate signal about what patterns remain after REWRITE and REFINE.

## Adding a New Style

1. Define a `StylePreset` in `styles/presets.py`
2. Add a `StyleName` enum entry in `core/models.py`
3. Register it in `STYLE_REGISTRY`
4. Add a test in `tests/unit/test_styles.py`

## Adding a New Detector

1. Subclass `BaseDetector` in `detectors/`
2. Implement `detect()` and `name`
3. Add it to the `CompositeDetector` instantiation in `engine.py`
4. Add tests in `tests/unit/test_detectors.py`

## Adding a New Transformer Backend

1. Subclass `BaseTransformer` in `transformers/`
2. Implement `transform()` and `name`
3. Inject it into `HumanizerEngine` via a constructor parameter

The engine only depends on `BaseTransformer`, so swapping in a different backend (rule-based, fine-tuned model, different API) requires no changes to the engine.
