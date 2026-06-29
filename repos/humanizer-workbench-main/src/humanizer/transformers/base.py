"""
Abstract base class for text transformers.

The interface is deliberately narrow. A transformer takes text and context,
and returns a StageResult. The engine handles sequencing and context
propagation — the transformer just does the transformation.

This makes it straightforward to add non-LLM transformers (rule-based,
fine-tuned models) that conform to the same interface.
"""

from abc import ABC, abstractmethod

from humanizer.core.models import DetectionResult, Intensity, PipelineStage, StageResult
from humanizer.styles.base import StylePreset


class BaseTransformer(ABC):
    """Interface for all text transformers."""

    @abstractmethod
    def transform(
        self,
        text: str,
        stage: PipelineStage,
        style: StylePreset,
        detection: DetectionResult,
        intensity: Intensity,
    ) -> StageResult:
        """Transform text for the given pipeline stage.

        Args:
            text: The text to transform (output of previous stage, or original).
            stage: Which pipeline stage this is (REWRITE, REFINE, AUDIT).
            style: The active style preset.
            detection: Detection results from the most recent detector run.
            intensity: The user-requested intensity level.

        Returns:
            StageResult with the transformed text and a summary of changes made.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this transformer."""
        ...
