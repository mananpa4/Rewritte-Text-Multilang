"""
Core data models for humanizer-workbench.

These dataclasses form the contract between pipeline stages. Keeping them
in one module avoids circular imports and makes the data flow explicit.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class Intensity(StrEnum):
    """Controls how aggressively the engine rewrites the text.

    LIGHT  — Fixes obvious AI vocabulary and filler phrases. Sentence structure
             is largely preserved. Useful when you want a light touch or when
             the text is mostly clean.

    MEDIUM — Rewrites sentences for naturalness and varies structure. This is
             the default and handles the majority of use cases well.

    AGGRESSIVE — Full multi-stage transformation: rewrite, structural refinement,
                 and a final audit pass. Use for text that is heavily templated
                 or structurally uniform.
    """

    LIGHT = "light"
    MEDIUM = "medium"
    AGGRESSIVE = "aggressive"


class StyleName(StrEnum):
    """Writing style presets.

    Each style meaningfully changes tone, vocabulary, and sentence structure —
    not just the system prompt. See styles/presets.py for the full definitions.
    """

    CASUAL = "casual"
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    FOUNDER = "founder"
    ACADEMIC = "academic"
    STORYTELLING = "storytelling"


class PipelineStage(StrEnum):
    """Stages in the humanization pipeline.

    REWRITE — Primary transformation. Removes AI patterns, applies style.
    REFINE  — Improves sentence rhythm, varies lengths, removes parallelism.
    AUDIT   — Final pass to catch any remaining AI-like constructs.
    """

    REWRITE = "rewrite"
    REFINE = "refine"
    AUDIT = "audit"


@dataclass
class PatternMatch:
    """A single detected AI-like pattern in the source text."""

    pattern_type: str  # e.g., "ai_vocabulary", "filler_phrase", "structural"
    matched_text: str
    start: int
    end: int
    severity: float  # 0.0–1.0, where 1.0 is most AI-like


@dataclass
class DetectionResult:
    """Output from the composite detector after scanning a piece of text."""

    patterns: list[PatternMatch] = field(default_factory=list)
    ai_vocabulary_hits: list[str] = field(default_factory=list)
    filler_phrase_hits: list[str] = field(default_factory=list)
    structural_flags: list[str] = field(default_factory=list)
    sentence_length_variance: float = 0.0  # higher = more varied = more human

    @property
    def phrase_count(self) -> int:
        return len(self.filler_phrase_hits)

    @property
    def structural_flag_count(self) -> int:
        return len(self.structural_flags)

    @property
    def total_pattern_count(self) -> int:
        return len(self.patterns)


@dataclass
class StageResult:
    """Output from a single pipeline stage transformation."""

    stage: PipelineStage
    input_text: str
    output_text: str
    changes_made: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.input_text.strip() != self.output_text.strip()


@dataclass
class HumanizerResult:
    """The complete result from a humanization run.

    This is the primary output type consumers interact with.
    """

    original: str
    output: str
    style: StyleName
    intensity: Intensity
    before_score: float  # 0–100, higher = more AI-like
    after_score: float
    stages: list[StageResult] = field(default_factory=list)
    changes_summary: list[str] = field(default_factory=list)

    @property
    def improvement(self) -> float:
        """Score reduction achieved. Positive means more human after processing."""
        return self.before_score - self.after_score

    @property
    def improvement_pct(self) -> float:
        """Percentage improvement relative to the before score."""
        if self.before_score == 0:
            return 0.0
        return (self.improvement / self.before_score) * 100
