"""
humanizer-workbench: A multi-stage AI text humanization engine.

Transforms AI-generated text into natural, human-like writing through
a configurable pipeline of detection, transformation, and refinement stages.
"""

__version__ = "0.1.0"
__author__ = "humanizer-workbench contributors"

from humanizer.core.engine import HumanizerEngine
from humanizer.core.models import HumanizerResult, Intensity, StyleName

__all__ = ["HumanizerEngine", "HumanizerResult", "Intensity", "StyleName"]
