"""
Pipeline configuration for the humanization engine.

The Pipeline determines which stages run and in what order, based on intensity.
This is intentionally a simple data structure — business logic lives in the
engine, not here.
"""

from dataclasses import dataclass

from humanizer.core.models import Intensity, PipelineStage


@dataclass(frozen=True)
class Pipeline:
    """An ordered sequence of pipeline stages to execute.

    Design note: pipelines are immutable because they're derived from intensity
    at construction time and should not change during a run. The frozen=True
    dataclass enforces this cheaply.
    """

    stages: tuple[PipelineStage, ...]

    @classmethod
    def for_intensity(cls, intensity: Intensity) -> "Pipeline":
        """Build a pipeline appropriate for the requested intensity level.

        Light:      REWRITE only — fast, minimal disruption.
        Medium:     REWRITE → REFINE — default, handles most cases.
        Aggressive: REWRITE → REFINE → AUDIT — full transformation.
        """
        match intensity:
            case Intensity.LIGHT:
                return cls(stages=(PipelineStage.REWRITE,))
            case Intensity.MEDIUM:
                return cls(stages=(PipelineStage.REWRITE, PipelineStage.REFINE))
            case Intensity.AGGRESSIVE:
                return cls(
                    stages=(
                        PipelineStage.REWRITE,
                        PipelineStage.REFINE,
                        PipelineStage.AUDIT,
                    )
                )

    @property
    def stage_count(self) -> int:
        return len(self.stages)

    def __repr__(self) -> str:
        stage_names = " → ".join(s.value.upper() for s in self.stages)
        return f"Pipeline({stage_names})"
