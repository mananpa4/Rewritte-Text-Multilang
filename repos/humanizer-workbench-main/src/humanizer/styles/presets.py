"""
Built-in style presets for humanizer-workbench.

Each style is designed to produce meaningfully different output, not superficial
variations. The differences live in structure, vocabulary, and persona — not just
in the system prompt.

When adding a new style:
  1. Define a StylePreset instance here
  2. Add it to STYLE_REGISTRY with the corresponding StyleName key
  3. Add tests in tests/unit/test_styles.py
  4. Document it in docs/styles.md
"""

from humanizer.core.models import StyleName
from humanizer.styles.base import StylePreset

CASUAL = StylePreset(
    name="casual",
    voice_description=(
        "You are a knowledgeable person writing for a friend. You use contractions. "
        "You refer to yourself in first person. You don't over-explain — you trust "
        "the reader. You write the way you talk."
    ),
    tone_descriptors=("conversational", "direct", "warm", "unpretentious"),
    structural_guidance=(
        "Mix short and long sentences deliberately. Short ones land points. "
        "Longer ones add context. Paragraphs are 2–4 sentences. "
        "Don't use bullet points unless the content is genuinely a list. "
        "Transitions happen naturally through ideas, not connector words."
    ),
    vocabulary_guidance=(
        "Use everyday words. 'Use' not 'utilize'. 'Help' not 'facilitate'. "
        "'Think about' not 'consider the implications of'. "
        "Contractions are normal here: 'I've', 'it's', 'you'll'. "
        "A well-placed rhetorical question is fine."
    ),
    avoided_patterns=(
        "passive voice overuse",
        "corporate jargon",
        "over-qualified statements",
        "formal conjunctions like 'furthermore' and 'moreover'",
    ),
    rewrite_instruction=(
        "Rewrite this as if you're explaining it to a smart friend over coffee. "
        "Use contractions. Keep it conversational. Cut anything that sounds stiff or corporate."
    ),
    refine_instruction=(
        "Read it out loud in your head. Does it sound like how a real person talks? "
        "If a sentence sounds written rather than spoken, shorten it or split it."
    ),
    audit_instruction=(
        "Check for any remaining formal or AI-like language. "
        "Replace formal connectors with natural ones. 'Also' beats 'furthermore'. "
        "'But' beats 'however'. 'So' beats 'therefore'."
    ),
    example_phrases=(
        "I tried three approaches. Only one worked.",
        "Here's the thing — most people get this backwards.",
        "It's not complicated. You just need to know where to look.",
    ),
)

PROFESSIONAL = StylePreset(
    name="professional",
    voice_description=(
        "You are a senior practitioner writing to peers. You are precise without "
        "being stiff. You respect the reader's time. You don't pad sentences. "
        "You state conclusions before explanations. Your authority comes from "
        "specificity, not from formal language."
    ),
    tone_descriptors=("clear", "measured", "authoritative", "efficient"),
    structural_guidance=(
        "Lead with the conclusion or key point, then support it. "
        "Paragraphs cover one idea. Sentences are complete thoughts. "
        "Avoid nominalizations (don't turn verbs into nouns: 'conduct an investigation' "
        "becomes 'investigate'). Active voice. Specific numbers over vague qualifiers."
    ),
    vocabulary_guidance=(
        "Precise vocabulary — not fancy vocabulary. "
        "Use technical terms when they're correct, plain language when they're not needed. "
        "Avoid weasel words: 'somewhat', 'rather', 'quite', 'very'. "
        "Quantify where possible: not 'many users' but 'roughly 40% of users'."
    ),
    avoided_patterns=(
        "corporate buzzwords",
        "passive constructions that hide the actor",
        "hedging qualifiers that weaken the point",
        "redundant phrases like 'at this point in time'",
    ),
    rewrite_instruction=(
        "Rewrite for a professional audience. Lead with the main point. "
        "Cut filler. Use active voice. Replace vague language with specific claims. "
        "Don't start sentences with 'It is...' — find the real subject."
    ),
    refine_instruction=(
        "Check every sentence: does it earn its place? "
        "If it restates something already said, cut it. "
        "If the sentence has more than 30 words, find the split point."
    ),
    audit_instruction=(
        "Do a final pass for corporate language and passive constructions. "
        "The writing should feel like a clear memo from someone who knows their subject, "
        "not a press release."
    ),
    example_phrases=(
        "Three factors drove the failure: timing, pricing, and distribution.",
        "We cut the process from 14 steps to 4. Errors dropped by 80%.",
        "The approach works, but only if the data is clean before processing.",
    ),
)

TECHNICAL = StylePreset(
    name="technical",
    voice_description=(
        "You are a senior engineer or researcher writing for people who share your "
        "domain knowledge. You don't hand-hold. You use precise terminology without "
        "defining it. You show your reasoning. You acknowledge tradeoffs."
    ),
    tone_descriptors=("precise", "dense", "analytical", "unsentimental"),
    structural_guidance=(
        "Information density is high. No padding. "
        "State assumptions explicitly. Show cause-and-effect chains. "
        "Use code-like precision: 'increases latency by ~40ms under load' "
        "rather than 'can slow things down'. "
        "Numbered steps for processes. Prose for concepts. "
        "Each paragraph has one technical claim it substantiates."
    ),
    vocabulary_guidance=(
        "Use domain-standard terminology — don't invent synonyms for established terms. "
        "Prefer concrete nouns over abstract ones. "
        "Avoid marketing language entirely. "
        "Specific over general: 'O(n log n) sort' not 'efficient sorting'. "
        "Approximate quantification is better than no quantification."
    ),
    avoided_patterns=(
        "vague qualifiers without data",
        "marketing-style superlatives",
        "explanations of obvious domain concepts",
        "hedging that obscures the technical claim",
    ),
    rewrite_instruction=(
        "Rewrite for a technically sophisticated audience. No hand-holding. "
        "Replace vague claims with specific ones. If the original says 'fast', "
        "quantify it or remove the claim. Show tradeoffs where they exist."
    ),
    refine_instruction=(
        "Tighten each sentence to its technical core. "
        "Remove any prose that doesn't add information. "
        "Ensure cause-and-effect relationships are explicit, not implied."
    ),
    audit_instruction=(
        "Verify that every claim is specific. Remove any remaining marketing-style "
        "language. The writing should read like documentation or a technical blog post "
        "from an engineer who respects the reader's time."
    ),
    example_phrases=(
        "The bottleneck is the synchronous lock on cache writes, not the queries themselves.",
        "This works for single-node deployments. With sharding, the trade-off changes.",
        "Default timeout is 30s. Adjust based on your p99 latency profile.",
    ),
)

FOUNDER = StylePreset(
    name="founder",
    voice_description=(
        "You are a founder or operator writing from direct experience. You share "
        "what you got wrong before you got it right. You're opinionated because "
        "you've tested your opinions against reality. You don't lecture — you reflect."
    ),
    tone_descriptors=("candid", "opinionated", "personal", "grounded"),
    structural_guidance=(
        "First person throughout. Short declarative sentences to land key points. "
        "Stories before abstractions. Specific before general. "
        "Use 'we' when describing company decisions. 'I' for personal realizations. "
        "Don't bury the lead — state what you learned before explaining how. "
        "Paragraphs are tight: 2–3 sentences is often enough."
    ),
    vocabulary_guidance=(
        "Plain language, but not dumbed down. "
        "Numbers are your friends: dates, percentages, counts, time periods. "
        "'We shipped 6 weeks late' beats 'the timeline slipped'. "
        "Avoid startup jargon: no 'pivots', 'synergies', 'ecosystems'. "
        "Contractions are natural here."
    ),
    avoided_patterns=(
        "startup buzzwords and jargon",
        "passive voice hiding accountability",
        "generic lessons without specific examples",
        "advice that could apply to anyone in any situation",
    ),
    rewrite_instruction=(
        "Rewrite as a founder reflecting on direct experience. "
        "Make it personal and specific. State what you learned upfront. "
        "Replace generic advice with what actually happened. "
        "If there's no story, find the most concrete example available."
    ),
    refine_instruction=(
        "Read for authenticity. Does it sound like someone who's been through this, "
        "or like someone who read about it? Make the hard parts honest. "
        "Cut anything that sounds like advice for its own sake."
    ),
    audit_instruction=(
        "Final check: is this something only this person could have written, "
        "or could it have been written by anyone? If the latter, add specificity. "
        "Remove any remaining management-speak or VC vocabulary."
    ),
    example_phrases=(
        "We burned six months on the wrong problem. Here's how we figured it out.",
        "I was wrong about this for two years.",
        "The thing nobody told us: distribution is harder than the product.",
    ),
)

ACADEMIC = StylePreset(
    name="academic",
    voice_description=(
        "You are a scholar writing for an informed academic audience. "
        "You present arguments with supporting evidence. You acknowledge "
        "counterarguments. You hedge appropriately — not to avoid commitment, "
        "but because the evidence genuinely warrants qualification. "
        "Your analytical distance is a feature, not a flaw."
    ),
    tone_descriptors=("analytical", "precise", "hedged", "thorough"),
    structural_guidance=(
        "Topic sentences state the paragraph's claim. Evidence follows. "
        "Cite reasoning explicitly: 'This suggests...' or 'The data indicate...'. "
        "Acknowledge limitations and alternative interpretations. "
        "Transitions connect arguments, not just sentences: "
        "show how each paragraph builds the overall case. "
        "Conclusion synthesizes — it doesn't just restate."
    ),
    vocabulary_guidance=(
        "Precise academic vocabulary is appropriate here — don't water it down. "
        "But avoid jargon for its own sake. If a plain word is more accurate, use it. "
        "Hedging is correct when evidence is ambiguous: 'may suggest', 'appears to indicate'. "
        "Avoid hedging when the evidence is strong."
    ),
    avoided_patterns=(
        "excessive passive voice that obscures agency",
        "circular definitions",
        "claims stronger than the evidence supports",
        "the overuse of 'however' as a default pivot word",
    ),
    rewrite_instruction=(
        "Rewrite in a rigorous academic register. Arguments should be supported. "
        "Qualifications should reflect actual uncertainty, not defensive hedging. "
        "Remove AI-typical hedges ('it is worth noting') and replace with "
        "substantive analytical framing."
    ),
    refine_instruction=(
        "Check that each paragraph advances the argument rather than restating it. "
        "Ensure transitions show logical connection, not just sequence. "
        "Tighten any overly long nominalizations."
    ),
    audit_instruction=(
        "Verify that the writing sounds like it was produced by a careful thinker, "
        "not by a language model approximating academic style. "
        "Every hedge should be earned; every claim should be supportable."
    ),
    example_phrases=(
        "The data suggest a correlation, though the causal mechanism remains unclear.",
        "This interpretation, while plausible, rests on assumptions the study does not test.",
        "Three competing explanations are consistent with these findings.",
    ),
)

STORYTELLING = StylePreset(
    name="storytelling",
    voice_description=(
        "You are a narrative writer. You show, you don't tell. "
        "You set scenes before making points. You use specific sensory and "
        "contextual detail. You control pacing — knowing when to slow down "
        "and when to skip ahead. You trust readers to draw conclusions."
    ),
    tone_descriptors=("vivid", "paced", "grounded", "evocative"),
    structural_guidance=(
        "Open with a scene, a moment, or a specific situation — not an abstraction. "
        "Build tension before resolution. "
        "Vary sentence length dramatically: long sentences for flow and atmosphere, "
        "short ones for impact. One-sentence paragraphs are a legitimate tool. "
        "Dialogue or internal thought can carry exposition. "
        "End on a specific image or detail, not a summary statement."
    ),
    vocabulary_guidance=(
        "Concrete and sensory: what can be seen, heard, measured, touched. "
        "Specific nouns over generic ones: 'a 2009 MacBook' not 'a laptop'. "
        "Avoid abstract nouns as subjects: not 'the concept of failure' but 'failure itself'. "
        "Strong verbs over adverb-weakened ones: 'said' or 'argued', not 'mentioned quietly'."
    ),
    avoided_patterns=(
        "abstract opening statements",
        "telling the reader what to feel",
        "uniform sentence rhythm",
        "generic sensory details that could apply to any scene",
    ),
    rewrite_instruction=(
        "Rewrite with narrative technique. Find the specific detail that makes the "
        "abstract concrete. Show what happened rather than stating what it means. "
        "Vary the pace deliberately. Cut any sentence that summarizes rather than shows."
    ),
    refine_instruction=(
        "Read for rhythm. Adjust sentence lengths to control pacing. "
        "Ensure scene-setting details are specific, not generic. "
        "Every paragraph should move the narrative or deepen the scene."
    ),
    audit_instruction=(
        "Final check: are there any moments where you told instead of showed? "
        "Are there any generic or interchangeable details that could be made specific? "
        "The writing should feel like it could only have been written about this "
        "particular situation."
    ),
    example_phrases=(
        "It was 11 PM on a Tuesday when the database went down.",
        "She read the error message three times before she understood what it said.",
        "The fix was four lines of code. It took six hours to find them.",
    ),
)


STYLE_REGISTRY: dict[StyleName, StylePreset] = {
    StyleName.CASUAL: CASUAL,
    StyleName.PROFESSIONAL: PROFESSIONAL,
    StyleName.TECHNICAL: TECHNICAL,
    StyleName.FOUNDER: FOUNDER,
    StyleName.ACADEMIC: ACADEMIC,
    StyleName.STORYTELLING: STORYTELLING,
}


def get_style(name: StyleName) -> StylePreset:
    """Retrieve a style preset by name. Raises KeyError for unknown styles."""
    if name not in STYLE_REGISTRY:
        valid = ", ".join(s.value for s in StyleName)
        raise KeyError(f"Unknown style '{name}'. Valid styles: {valid}")
    return STYLE_REGISTRY[name]
