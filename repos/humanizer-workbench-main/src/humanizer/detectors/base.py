"""
Abstract base class for detectors and the composite that combines them.

Each detector is responsible for a distinct category of AI-like patterns.
The CompositeDetector merges results from all registered detectors into
a single DetectionResult, which the engine and scorer consume.
"""

from abc import ABC, abstractmethod

from humanizer.core.models import DetectionResult, PatternMatch


class BaseDetector(ABC):
    """Interface that all detectors must implement."""

    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        """Scan text and return detected AI-like patterns."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this detector."""
        ...


class CompositeDetector(BaseDetector):
    """Runs multiple detectors and merges their results.

    Merging strategy:
    - patterns: union of all matched patterns
    - ai_vocabulary_hits: deduplicated union
    - filler_phrase_hits: deduplicated union
    - structural_flags: deduplicated union
    - sentence_length_variance: taken from the first detector that computes it
      (currently only StructuralDetector does)
    """

    def __init__(self, detectors: list[BaseDetector]) -> None:
        if not detectors:
            raise ValueError("CompositeDetector requires at least one detector")
        self._detectors = detectors

    @property
    def name(self) -> str:
        return f"Composite({', '.join(d.name for d in self._detectors)})"

    def detect(self, text: str) -> DetectionResult:
        all_patterns: list[PatternMatch] = []
        all_vocab_hits: list[str] = []
        all_phrase_hits: list[str] = []
        all_structural_flags: list[str] = []
        sentence_length_variance: float = 0.0

        for detector in self._detectors:
            result = detector.detect(text)
            all_patterns.extend(result.patterns)
            all_vocab_hits.extend(result.ai_vocabulary_hits)
            all_phrase_hits.extend(result.filler_phrase_hits)
            all_structural_flags.extend(result.structural_flags)
            if result.sentence_length_variance > 0:
                sentence_length_variance = result.sentence_length_variance

        return DetectionResult(
            patterns=all_patterns,
            ai_vocabulary_hits=list(dict.fromkeys(all_vocab_hits)),
            filler_phrase_hits=list(dict.fromkeys(all_phrase_hits)),
            structural_flags=list(dict.fromkeys(all_structural_flags)),
            sentence_length_variance=sentence_length_variance,
        )
