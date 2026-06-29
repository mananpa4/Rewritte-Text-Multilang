"""
StylePreset: the contract each writing style must fulfill.

A StylePreset is not just a prompt template. It encodes:
  - The voice and persona the writer should embody
  - Structural preferences (sentence length, paragraph density)
  - Vocabulary guidance (what to use, what to avoid)
  - Stage-specific instructions that vary by pipeline stage

This separation means the LLM transformer can build targeted prompts for
each stage rather than relying on a single generic system prompt.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StylePreset:
    """Defines the behavioral contract for a writing style.

    Attributes:
        name: The style identifier (matches StyleName enum values).
        voice_description: Who the writer is. Written in second person ("You are...").
            This sets the persona for all transformation stages.
        tone_descriptors: Short adjectives describing the target tone. Used in
            prompt construction to quickly frame the expected output character.
        structural_guidance: How sentences and paragraphs should be shaped.
            Include specifics: sentence length preferences, paragraph density,
            how to handle transitions.
        vocabulary_guidance: What word choices characterize this style. Be
            specific — "prefer concrete nouns over abstract ones" is more useful
            than "use simple language".
        avoided_patterns: Patterns this style should actively not use. These
            supplement the global AI vocabulary list with style-specific concerns.
        rewrite_instruction: The core instruction for the REWRITE stage.
        refine_instruction: Additional instruction for the REFINE stage.
        audit_instruction: Final check instruction for the AUDIT stage.
    """

    name: str
    voice_description: str
    tone_descriptors: tuple[str, ...]
    structural_guidance: str
    vocabulary_guidance: str
    avoided_patterns: tuple[str, ...]
    rewrite_instruction: str
    refine_instruction: str
    audit_instruction: str
    example_phrases: tuple[str, ...] = field(default_factory=tuple)
