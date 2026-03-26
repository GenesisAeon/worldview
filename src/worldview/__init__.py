"""worldview â€” Philosophical-ethical worldview layer with normative metrics.

This package provides the WorldviewEngine for assessing philosophical coherence,
ethical implications, and common-good alignment of world-models in the GenesisAeon
ecosystem.

References
----------
- CREP: Critical Reflexive Evaluation Protocol
- Sigillin: Symbolic integration layer for GenesisAeon
- GenesisAeon Normative Framework v0.2
"""

from worldview.core.critique import CriticalityChecker, CritiqueReport
from worldview.core.worldview import (
    NormativeMetrics,
    WorldviewAssessment,
    WorldviewEngine,
)
from worldview.governance.alignment import (
    AlignmentFramework,
    CommonGoodMetric,
    PersonhoodLevel,
)

__version__ = "0.3.1"
__author__ = "GenesisAeon"
__license__ = "MIT"

__all__ = [
    "WorldviewEngine",
    "WorldviewAssessment",
    "NormativeMetrics",
    "CriticalityChecker",
    "CritiqueReport",
    "AlignmentFramework",
    "CommonGoodMetric",
    "PersonhoodLevel",
    "__version__",
]

