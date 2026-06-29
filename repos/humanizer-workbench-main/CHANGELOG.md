# Changelog

All notable changes to humanizer-workbench are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project uses semantic versioning.

## [Unreleased]

### Added

- `SKILL.md`: Claude Code skill interface for interactive humanization in Claude Code sessions
- Updated README to document both CLI and Claude Code skill usage
- `examples/sample_ai_text.txt`: realistic sample for testing the tool

## [0.1.0] - 2024-01-01

### Added

- Multi-stage humanization pipeline: REWRITE → REFINE → AUDIT
- Six writing style presets: casual, professional, technical, founder, academic, storytelling
- Three intensity levels: light (1 stage), medium (2 stages), aggressive (3 stages)
- Heuristic AI-likeness scorer with five components:
  - AI vocabulary density (up to 30 points)
  - Filler phrase density (up to 25 points)
  - Sentence length uniformity (up to 20 points)
  - Structural pattern density (up to 15 points)
  - AI sentence opener patterns (up to 10 points)
- Lexical detector with 50+ AI vocabulary words and 30+ filler phrases
- Structural detector for sentence uniformity, em dash overuse, rule-of-three patterns
- CLI with `--style`, `--intensity`, `--diff`, `--score`, `--explain`, `--output` flags
- `humanizer detect` subcommand for pattern analysis without transformation
- Python API: `HumanizerEngine.humanize()` returns a `HumanizerResult`
- Unit tests covering detectors, scorer, styles, engine, and pipeline
- Integration tests marked with `@pytest.mark.integration`
