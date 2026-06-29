"""
Demonstration script for humanizer-workbench.

Shows the Python API directly, without going through the CLI.
Requires ANTHROPIC_API_KEY to be set.

Usage:
    python examples/demo.py
"""

import os
import sys

# Make sure the package is importable when running from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from humanizer import HumanizerEngine, Intensity, StyleName

SAMPLE_TEXT = """
In today's fast-paced digital landscape, it is important to note that organizations
must leverage comprehensive strategies to facilitate seamless collaboration across
all stakeholders. Furthermore, the implementation of robust and innovative
methodologies plays a crucial role in empowering teams to streamline their workflows
and optimize overall performance.

Moreover, it is worth noting that these transformative approaches enable enterprises
to navigate complex challenges with unprecedented agility. In conclusion, the holistic
integration of cutting-edge solutions represents a paramount step toward achieving
sustainable organizational excellence and delivering impactful results that resonate
across the entire ecosystem.
""".strip()


def run_demo():
    print("humanizer-workbench demo\n" + "=" * 40)
    print("\nOriginal text:")
    print("-" * 40)
    print(SAMPLE_TEXT)
    print()

    engine = HumanizerEngine()

    # Demo 1: Professional style, medium intensity
    print("\n[1] Professional style, medium intensity")
    print("-" * 40)
    result = engine.humanize(
        SAMPLE_TEXT,
        style=StyleName.PROFESSIONAL,
        intensity=Intensity.MEDIUM,
    )
    print(result.output)
    print(f"\nScore: {result.before_score:.0f} → {result.after_score:.0f} "
          f"({result.improvement:.0f} point improvement)")

    # Demo 2: Founder style, aggressive intensity
    print("\n\n[2] Founder style, aggressive intensity")
    print("-" * 40)
    result2 = engine.humanize(
        SAMPLE_TEXT,
        style=StyleName.FOUNDER,
        intensity=Intensity.AGGRESSIVE,
    )
    print(result2.output)
    print(f"\nScore: {result2.before_score:.0f} → {result2.after_score:.0f} "
          f"({result2.improvement:.0f} point improvement)")

    # Demo 3: Casual style, light intensity
    print("\n\n[3] Casual style, light intensity")
    print("-" * 40)
    result3 = engine.humanize(
        SAMPLE_TEXT,
        style=StyleName.CASUAL,
        intensity=Intensity.LIGHT,
    )
    print(result3.output)
    print(f"\nScore: {result3.before_score:.0f} → {result3.after_score:.0f} "
          f"({result3.improvement:.0f} point improvement)")

    print("\n\nDone.")


if __name__ == "__main__":
    run_demo()
