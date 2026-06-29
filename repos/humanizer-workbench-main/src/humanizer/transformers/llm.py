"""
LLM-based transformer using the Anthropic API.

Each pipeline stage uses a distinct prompt strategy:

  REWRITE — Full transformation prompt. Injects detected patterns, style voice,
            vocabulary guidance, and intensity-specific instructions. This is the
            heaviest prompt and does the primary work.

  REFINE  — Lighter prompt focused on rhythm and sentence-level naturalness.
            Does not repeat the full style context; the text is already styled.
            Targets structural issues that survived the rewrite pass.

  AUDIT   — Minimal prompt for a final sanity check. Reads the text as a human
            editor would and fixes anything that still sounds generated.

Design decisions:
  - Model: claude-sonnet-4-6 by default. Sufficient quality for all stages.
    Users can pass a different model via HumanizerEngine.
  - Temperature: 0.7 for REWRITE (creative latitude), 0.4 for REFINE/AUDIT
    (preserve what's working, fix what isn't).
  - Output parsing: We strip common LLM preambles before returning. The prompt
    explicitly instructs the model to return only the transformed text, but
    models occasionally add a header anyway.
  - Changes detection: Computed programmatically by comparing detection results
    before and after, rather than asking the LLM to summarize its own changes.
    LLM self-reporting of changes is unreliable.
"""

import re

import anthropic

from humanizer.core.models import DetectionResult, Intensity, PipelineStage, StageResult
from humanizer.styles.base import StylePreset
from humanizer.transformers.base import BaseTransformer

DEFAULT_MODEL = "claude-sonnet-4-6"

# Temperature per stage. Lower = more conservative; higher = more creative.
STAGE_TEMPERATURES: dict[PipelineStage, float] = {
    PipelineStage.REWRITE: 0.7,
    PipelineStage.REFINE: 0.45,
    PipelineStage.AUDIT: 0.3,
}

# Max output tokens. Generous for REWRITE (text may expand slightly),
# tighter for AUDIT (should be roughly same length as input).
STAGE_MAX_TOKENS: dict[PipelineStage, int] = {
    PipelineStage.REWRITE: 4096,
    PipelineStage.REFINE: 4096,
    PipelineStage.AUDIT: 3072,
}

# LLM preamble patterns to strip from output.
_PREAMBLE_PATTERNS = re.compile(
    r"^(?:"
    r"here(?:'s| is) (?:the )?(?:rewritten|refined|humanized|revised|updated|transformed) (?:text|version|output)[:\s]*|"
    r"i(?:'ve| have) (?:rewritten|refined|revised|humanized|transformed|updated) (?:the )?(?:text|passage)[:\s]*|"
    r"(?:rewritten|refined|humanized|revised) (?:text|version)[:\s]*|"
    r"here(?:'s| is) (?:the )?(?:output|result)[:\s]*|"
    r"below is (?:the )?(?:rewritten|refined|humanized) (?:text|version)[:\s]*"
    r")\n+",
    re.IGNORECASE,
)


def _strip_preamble(text: str) -> str:
    """Remove common LLM preambles from output."""
    return _PREAMBLE_PATTERNS.sub("", text.strip()).strip()


def _format_vocabulary_hits(hits: list[str]) -> str:
    if not hits:
        return "none detected"
    return ", ".join(f'"{w}"' for w in hits[:15])  # cap for prompt length


def _format_phrase_hits(hits: list[str]) -> str:
    if not hits:
        return "none detected"
    return "; ".join(f'"{p}"' for p in hits[:10])


def _format_structural_flags(flags: list[str]) -> str:
    if not flags:
        return "none detected"
    return "; ".join(flags[:8])


def _intensity_guidance(intensity: Intensity) -> str:
    match intensity:
        case Intensity.LIGHT:
            return (
                "Make minimal changes. Fix the most obvious AI vocabulary and filler phrases. "
                "Preserve the original sentence structure wherever possible."
            )
        case Intensity.MEDIUM:
            return (
                "Rewrite for naturalness. Restructure sentences where needed but keep the "
                "overall flow recognizable. Don't add new ideas, but feel free to reorder "
                "or split sentences."
            )
        case Intensity.AGGRESSIVE:
            return (
                "Fully transform the text. Rewrite every sentence from scratch if needed. "
                "Restructure paragraphs. Change the order of ideas if it makes the writing "
                "more natural. The only constraint is preserving the core meaning."
            )


def _build_rewrite_prompt(
    text: str,
    style: StylePreset,
    detection: DetectionResult,
    intensity: Intensity,
) -> str:
    return f"""You are transforming AI-generated text into natural, human-written prose.

STYLE: {style.name.upper()}
{style.voice_description}

TONE: {", ".join(style.tone_descriptors)}

STRUCTURAL GUIDANCE:
{style.structural_guidance}

VOCABULARY GUIDANCE:
{style.vocabulary_guidance}

WHAT TO AVOID:
{chr(10).join(f"- {p}" for p in style.avoided_patterns)}

REWRITE INSTRUCTION:
{style.rewrite_instruction}

INTENSITY: {intensity.value.upper()}
{_intensity_guidance(intensity)}

DETECTED AI PATTERNS IN THIS TEXT:
- AI vocabulary found: {_format_vocabulary_hits(detection.ai_vocabulary_hits)}
- Filler phrases found: {_format_phrase_hits(detection.filler_phrase_hits)}
- Structural issues: {_format_structural_flags(detection.structural_flags)}

CRITICAL RULES:
1. Preserve all factual information, names, numbers, and core meaning.
2. Do not add information that was not in the original text.
3. Do not use any of the detected AI vocabulary words in your output.
4. Output ONLY the rewritten text. No preamble, no explanation, no commentary.

TEXT TO REWRITE:
{text}"""


def _build_refine_prompt(
    text: str,
    style: StylePreset,
    detection: DetectionResult,
    intensity: Intensity,
) -> str:
    return f"""You are refining a piece of writing to improve its natural rhythm and flow.

The text has already been rewritten for style ({style.name}). Your job is to:
1. Vary sentence lengths more deliberately. Short punchy sentences for key points.
   Longer sentences for context and nuance.
2. Remove any remaining formulaic sentence openers
   (furthermore, moreover, additionally, importantly, notably).
3. Break up excessive parallel structure — not every item needs to be the same length.
4. Ensure transitions feel organic, not mechanical.

REFINE INSTRUCTION:
{style.refine_instruction}

REMAINING STRUCTURAL ISSUES:
{_format_structural_flags(detection.structural_flags)}

RULES:
1. Do not change the meaning or add information.
2. Only change what genuinely improves the naturalness.
3. Output ONLY the refined text. No preamble or explanation.

TEXT TO REFINE:
{text}"""


def _build_audit_prompt(
    text: str,
    style: StylePreset,
    detection: DetectionResult,
    intensity: Intensity,
) -> str:
    return f"""You are doing a final editorial pass on a piece of writing.

Read the text below as a human editor would. Your goal: make sure it sounds like
a real person wrote it, not an AI approximating human writing.

Specific things to check:
- Any remaining AI vocabulary (delve, leverage, tapestry, nuanced, robust, seamless, etc.)
- Formulaic sentence openers
- Overly uniform sentence lengths
- Phrases that sound like they were generated rather than written
- Excessive hedging or qualification

Style context: {style.name} — {", ".join(style.tone_descriptors)}

AUDIT INSTRUCTION:
{style.audit_instruction}

RULES:
1. Only fix what still sounds AI-generated. Leave natural-sounding text alone.
2. Preserve all factual content.
3. Output ONLY the final text. No preamble or explanation.

TEXT TO AUDIT:
{text}"""


_PROMPT_BUILDERS = {
    PipelineStage.REWRITE: _build_rewrite_prompt,
    PipelineStage.REFINE: _build_refine_prompt,
    PipelineStage.AUDIT: _build_audit_prompt,
}


def _infer_changes(detection: DetectionResult) -> list[str]:
    """Build a list of human-readable change descriptions from detection data."""
    changes = []
    if detection.ai_vocabulary_hits:
        top = detection.ai_vocabulary_hits[:5]
        changes.append(f"Removed AI vocabulary: {', '.join(top)}")
    if detection.filler_phrase_hits:
        top = detection.filler_phrase_hits[:3]
        changes.append(f"Removed filler phrases: {'; '.join(top)}")
    if detection.structural_flags:
        flag_types = set()
        for flag in detection.structural_flags:
            flag_type = flag.split(":")[0]
            flag_types.add(flag_type)
        for ft in list(flag_types)[:3]:
            changes.append(f"Addressed structural pattern: {ft.replace('_', ' ')}")
    return changes


class LLMTransformer(BaseTransformer):
    """Transforms text using the Anthropic API via stage-specific prompts."""

    def __init__(
        self,
        client: anthropic.Anthropic,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self._client = client
        self._model = model

    @property
    def name(self) -> str:
        return f"LLMTransformer({self._model})"

    def transform(
        self,
        text: str,
        stage: PipelineStage,
        style: StylePreset,
        detection: DetectionResult,
        intensity: Intensity,
    ) -> StageResult:
        """Run a single pipeline stage transformation via the Anthropic API."""
        prompt_builder = _PROMPT_BUILDERS[stage]
        prompt = prompt_builder(text, style, detection, intensity)

        response = self._client.messages.create(
            model=self._model,
            max_tokens=STAGE_MAX_TOKENS[stage],
            temperature=STAGE_TEMPERATURES[stage],
            messages=[{"role": "user", "content": prompt}],
        )

        raw_output = response.content[0].text  # type: ignore[union-attr]
        transformed = _strip_preamble(raw_output)

        # If the model returned an empty string (shouldn't happen, but defensive):
        if not transformed.strip():
            transformed = text

        changes = _infer_changes(detection)

        return StageResult(
            stage=stage,
            input_text=text,
            output_text=transformed,
            changes_made=changes,
        )
