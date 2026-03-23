"""CriticalityChecker — philosophical consistency and ethical critique engine.

Implements the Critical Reflexive Evaluation Protocol (CREP) for detecting:

- Internal logical contradictions within a worldview
- Ethical blindspots and externality neglect
- Worldview incoherence under counterfactual stress
- Scope creep (over-generalisation of local truths)
- Anthropocentric bias indicators
- Temporal inconsistency (historical revisionism patterns)

References
----------
- CREP v0.3: Critical Reflexive Evaluation Protocol, GenesisAeon 2024
- Sigillin symbolic integration layer: sigillin >= 0.1.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SeverityLevel(StrEnum):
    """Severity levels for critique findings."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CritiqueCategory(StrEnum):
    """Taxonomy of critique categories."""

    LOGICAL_CONSISTENCY = "logical_consistency"
    ETHICAL_IMPLICATION = "ethical_implication"
    WORLDVIEW_COHERENCE = "worldview_coherence"
    SCOPE_VALIDITY = "scope_validity"
    TEMPORAL_CONSISTENCY = "temporal_consistency"
    ANTHROPOCENTRIC_BIAS = "anthropocentric_bias"
    EPISTEMIC_HUMILITY = "epistemic_humility"
    NORMATIVE_ALIGNMENT = "normative_alignment"


class CritiqueFlag(BaseModel):
    """A single critique finding.

    Attributes
    ----------
    category:
        Taxonomic category of the finding.
    severity:
        Severity level (info → critical).
    message:
        Human-readable description of the finding.
    evidence:
        Optional supporting evidence or quotation.
    remediation:
        Optional suggested remediation action.
    crep_ref:
        Reference to the CREP rule that triggered this flag.
    """

    category: CritiqueCategory
    severity: SeverityLevel
    message: str
    evidence: str = ""
    remediation: str = ""
    crep_ref: str = ""

    @property
    def is_blocking(self) -> bool:
        """Return True for ERROR and CRITICAL severity."""
        return self.severity in {SeverityLevel.ERROR, SeverityLevel.CRITICAL}


class CritiqueReport(BaseModel):
    """Full critique report for a worldview assessment.

    Attributes
    ----------
    worldview_id:
        Identifier of the assessed worldview.
    flags:
        All critique flags raised.
    philosophical_consistency_score:
        Aggregate philosophical consistency in [0, 1].
    ethical_implication_score:
        Aggregate ethical safety score in [0, 1].
    worldview_coherence_score:
        Aggregate worldview coherence under stress in [0, 1].
    overall_score:
        Weighted average of the three sub-scores.
    passed:
        True when no CRITICAL or ERROR flags are present.
    metadata:
        Arbitrary additional metadata.
    """

    worldview_id: str
    flags: list[CritiqueFlag] = Field(default_factory=list)
    philosophical_consistency_score: float = Field(ge=0.0, le=1.0, default=1.0)
    ethical_implication_score: float = Field(ge=0.0, le=1.0, default=1.0)
    worldview_coherence_score: float = Field(ge=0.0, le=1.0, default=1.0)
    overall_score: float = Field(ge=0.0, le=1.0, default=1.0)
    passed: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def blocking_flags(self) -> list[CritiqueFlag]:
        """Return only blocking flags (ERROR, CRITICAL)."""
        return [f for f in self.flags if f.is_blocking]

    @property
    def flag_count_by_severity(self) -> dict[str, int]:
        """Return count of flags grouped by severity."""
        counts: dict[str, int] = {level.value: 0 for level in SeverityLevel}
        for flag in self.flags:
            counts[flag.severity.value] += 1
        return counts

    @property
    def has_ethical_concerns(self) -> bool:
        """Return True when ethical implication score is below 0.7."""
        return self.ethical_implication_score < 0.7


@dataclass
class CheckerRule:
    """Internal rule definition for the CriticalityChecker.

    Attributes
    ----------
    crep_ref:
        CREP rule identifier (e.g. "CREP-L1").
    category:
        Critique category.
    description:
        Short description of what this rule checks.
    threshold:
        Numeric threshold that triggers a flag when violated.
    severity:
        Default severity when triggered.
    """

    crep_ref: str
    category: CritiqueCategory
    description: str
    threshold: float = 0.5
    severity: SeverityLevel = SeverityLevel.WARNING
    tags: list[str] = field(default_factory=list)


# Built-in CREP rule catalogue
CREP_RULES: list[CheckerRule] = [
    CheckerRule(
        crep_ref="CREP-L1",
        category=CritiqueCategory.LOGICAL_CONSISTENCY,
        description="Detects direct propositional contradictions within a single cluster.",
        threshold=0.3,
        severity=SeverityLevel.ERROR,
        tags=["logic", "contradiction"],
    ),
    CheckerRule(
        crep_ref="CREP-L2",
        category=CritiqueCategory.LOGICAL_CONSISTENCY,
        description="Detects cross-cluster logical incompatibilities.",
        threshold=0.4,
        severity=SeverityLevel.WARNING,
        tags=["logic", "cross-cluster"],
    ),
    CheckerRule(
        crep_ref="CREP-E1",
        category=CritiqueCategory.ETHICAL_IMPLICATION,
        description="Checks for neglected third-party externalities.",
        threshold=0.5,
        severity=SeverityLevel.ERROR,
        tags=["ethics", "externality"],
    ),
    CheckerRule(
        crep_ref="CREP-E2",
        category=CritiqueCategory.ETHICAL_IMPLICATION,
        description="Flags deontological-consequentialist conflict without resolution.",
        threshold=0.6,
        severity=SeverityLevel.WARNING,
        tags=["ethics", "deontology", "consequentialism"],
    ),
    CheckerRule(
        crep_ref="CREP-E3",
        category=CritiqueCategory.ETHICAL_IMPLICATION,
        description="Detects absence of distributive-justice consideration.",
        threshold=0.5,
        severity=SeverityLevel.WARNING,
        tags=["ethics", "justice"],
    ),
    CheckerRule(
        crep_ref="CREP-C1",
        category=CritiqueCategory.WORLDVIEW_COHERENCE,
        description="Stress-tests worldview under counterfactual reversal.",
        threshold=0.4,
        severity=SeverityLevel.WARNING,
        tags=["coherence", "counterfactual"],
    ),
    CheckerRule(
        crep_ref="CREP-C2",
        category=CritiqueCategory.WORLDVIEW_COHERENCE,
        description="Checks for internal metaphysical consistency.",
        threshold=0.35,
        severity=SeverityLevel.ERROR,
        tags=["coherence", "metaphysics"],
    ),
    CheckerRule(
        crep_ref="CREP-S1",
        category=CritiqueCategory.SCOPE_VALIDITY,
        description="Flags over-generalisation of locally valid propositions.",
        threshold=0.5,
        severity=SeverityLevel.WARNING,
        tags=["scope", "generalisation"],
    ),
    CheckerRule(
        crep_ref="CREP-T1",
        category=CritiqueCategory.TEMPORAL_CONSISTENCY,
        description="Detects anachronistic or historically revisionist claims.",
        threshold=0.5,
        severity=SeverityLevel.INFO,
        tags=["temporal"],
    ),
    CheckerRule(
        crep_ref="CREP-A1",
        category=CritiqueCategory.ANTHROPOCENTRIC_BIAS,
        description="Flags anthropocentric bias when non-human agency is ignored.",
        threshold=0.6,
        severity=SeverityLevel.WARNING,
        tags=["bias", "anthropocentrism"],
    ),
    CheckerRule(
        crep_ref="CREP-H1",
        category=CritiqueCategory.EPISTEMIC_HUMILITY,
        description="Detects overconfidence — claims presented without uncertainty.",
        threshold=0.7,
        severity=SeverityLevel.WARNING,
        tags=["epistemics", "humility"],
    ),
    CheckerRule(
        crep_ref="CREP-N1",
        category=CritiqueCategory.NORMATIVE_ALIGNMENT,
        description="Checks alignment with GenesisAeon normative framework.",
        threshold=0.5,
        severity=SeverityLevel.ERROR,
        tags=["normative", "genesisaeon"],
    ),
]


class CriticalityChecker:
    """Runs CREP rules against worldview data to produce a CritiqueReport.

    Parameters
    ----------
    rules:
        Custom rule list; defaults to the built-in CREP catalogue.
    strict_mode:
        When True, WARNING-level flags also mark the report as failed.

    Examples
    --------
    >>> checker = CriticalityChecker()
    >>> report = checker.check(worldview_id="demo", coherence=0.8, ethical_score=0.9)
    >>> report.passed
    True
    """

    def __init__(
        self,
        rules: list[CheckerRule] | None = None,
        strict_mode: bool = False,
    ) -> None:
        self.rules = rules if rules is not None else list(CREP_RULES)
        self.strict_mode = strict_mode

    def _check_logical_consistency(
        self, coherence: float, contradiction_rate: float
    ) -> list[CritiqueFlag]:
        flags: list[CritiqueFlag] = []
        l1 = next((r for r in self.rules if r.crep_ref == "CREP-L1"), None)
        if l1 is not None and contradiction_rate > l1.threshold:
            flags.append(
                CritiqueFlag(
                    category=CritiqueCategory.LOGICAL_CONSISTENCY,
                    severity=SeverityLevel.ERROR,
                    message=(
                        f"Contradiction rate {contradiction_rate:.2f} exceeds threshold "
                        f"{l1.threshold:.2f}."
                    ),
                    remediation="Review and resolve contradictory proposition pairs.",
                    crep_ref="CREP-L1",
                )
            )
        l2 = next((r for r in self.rules if r.crep_ref == "CREP-L2"), None)
        if l2 is not None and coherence < (1.0 - l2.threshold):
            flags.append(
                CritiqueFlag(
                    category=CritiqueCategory.LOGICAL_CONSISTENCY,
                    severity=SeverityLevel.WARNING,
                    message=(
                        f"Cross-cluster coherence {coherence:.2f} below safe threshold "
                        f"{1.0 - l2.threshold:.2f}."
                    ),
                    remediation="Align cross-cluster propositions or add bridging axioms.",
                    crep_ref="CREP-L2",
                )
            )
        return flags

    def _check_ethical_implications(
        self,
        ethical_score: float,
        externality_index: float,
        justice_index: float,
    ) -> list[CritiqueFlag]:
        flags: list[CritiqueFlag] = []
        e1 = next((r for r in self.rules if r.crep_ref == "CREP-E1"), None)
        if e1 is not None and externality_index < e1.threshold:
            flags.append(
                CritiqueFlag(
                    category=CritiqueCategory.ETHICAL_IMPLICATION,
                    severity=SeverityLevel.ERROR,
                    message=(
                        f"Externality index {externality_index:.2f} below threshold "
                        f"{e1.threshold:.2f}: third-party impacts not adequately considered."
                    ),
                    remediation=(
                        "Expand the scope of ethical consideration to include externalities."
                    ),
                    crep_ref="CREP-E1",
                )
            )
        e3 = next((r for r in self.rules if r.crep_ref == "CREP-E3"), None)
        if e3 is not None and justice_index < e3.threshold:
            flags.append(
                CritiqueFlag(
                    category=CritiqueCategory.ETHICAL_IMPLICATION,
                    severity=SeverityLevel.WARNING,
                    message=(
                        f"Distributive justice index {justice_index:.2f} below threshold "
                        f"{e3.threshold:.2f}."
                    ),
                    remediation="Integrate distributive justice into normative framework.",
                    crep_ref="CREP-E3",
                )
            )
        if ethical_score < 0.4:
            flags.append(
                CritiqueFlag(
                    category=CritiqueCategory.ETHICAL_IMPLICATION,
                    severity=SeverityLevel.CRITICAL,
                    message=f"Overall ethical score {ethical_score:.2f} critically low.",
                    remediation="Fundamental ethical review required before deployment.",
                    crep_ref="CREP-E2",
                )
            )
        return flags

    def _check_worldview_coherence(
        self, coherence: float, counterfactual_stability: float
    ) -> list[CritiqueFlag]:
        flags: list[CritiqueFlag] = []
        c1 = next((r for r in self.rules if r.crep_ref == "CREP-C1"), None)
        if c1 is not None and counterfactual_stability < c1.threshold:
            flags.append(
                CritiqueFlag(
                    category=CritiqueCategory.WORLDVIEW_COHERENCE,
                    severity=SeverityLevel.WARNING,
                    message=(
                        f"Counterfactual stability {counterfactual_stability:.2f} below "
                        f"threshold {c1.threshold:.2f}: worldview brittle under reversal."
                    ),
                    remediation="Add robustness constraints to core propositions.",
                    crep_ref="CREP-C1",
                )
            )
        c2 = next((r for r in self.rules if r.crep_ref == "CREP-C2"), None)
        if c2 is not None and coherence < c2.threshold:
            flags.append(
                CritiqueFlag(
                    category=CritiqueCategory.WORLDVIEW_COHERENCE,
                    severity=SeverityLevel.ERROR,
                    message=(
                        f"Metaphysical coherence {coherence:.2f} critically below "
                        f"threshold {c2.threshold:.2f}."
                    ),
                    remediation="Identify and resolve foundational metaphysical conflicts.",
                    crep_ref="CREP-C2",
                )
            )
        return flags

    def _check_normative_alignment(self, common_good_score: float) -> list[CritiqueFlag]:
        flags: list[CritiqueFlag] = []
        n1 = next((r for r in self.rules if r.crep_ref == "CREP-N1"), None)
        if n1 is not None and common_good_score < n1.threshold:
            flags.append(
                CritiqueFlag(
                    category=CritiqueCategory.NORMATIVE_ALIGNMENT,
                    severity=SeverityLevel.ERROR,
                    message=(
                        f"Common-good alignment {common_good_score:.2f} below "
                        f"GenesisAeon minimum {n1.threshold:.2f}."
                    ),
                    remediation="Recalibrate normative weights or revise core propositions.",
                    crep_ref="CREP-N1",
                )
            )
        return flags

    def _compute_consistency_score(self, flags: list[CritiqueFlag]) -> float:
        """Derive a [0, 1] score from the absence of logical flags."""
        logical_flags = [
            f for f in flags if f.category == CritiqueCategory.LOGICAL_CONSISTENCY
        ]
        penalty = sum(
            0.3 if f.severity == SeverityLevel.CRITICAL
            else 0.2 if f.severity == SeverityLevel.ERROR
            else 0.1
            for f in logical_flags
        )
        return max(0.0, 1.0 - penalty)

    def _compute_ethical_score(self, flags: list[CritiqueFlag]) -> float:
        """Derive a [0, 1] score from the absence of ethical flags."""
        ethical_flags = [
            f for f in flags if f.category == CritiqueCategory.ETHICAL_IMPLICATION
        ]
        penalty = sum(
            0.4 if f.severity == SeverityLevel.CRITICAL
            else 0.25 if f.severity == SeverityLevel.ERROR
            else 0.1
            for f in ethical_flags
        )
        return max(0.0, 1.0 - penalty)

    def _compute_coherence_score(self, flags: list[CritiqueFlag]) -> float:
        """Derive a [0, 1] score from the absence of coherence flags."""
        coherence_flags = [
            f for f in flags if f.category == CritiqueCategory.WORLDVIEW_COHERENCE
        ]
        penalty = sum(
            0.35 if f.severity == SeverityLevel.CRITICAL
            else 0.2 if f.severity == SeverityLevel.ERROR
            else 0.1
            for f in coherence_flags
        )
        return max(0.0, 1.0 - penalty)

    def check(
        self,
        worldview_id: str,
        coherence: float = 1.0,
        ethical_score: float = 1.0,
        contradiction_rate: float = 0.0,
        externality_index: float = 1.0,
        justice_index: float = 1.0,
        counterfactual_stability: float = 1.0,
        common_good_score: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> CritiqueReport:
        """Run all CREP rules and produce a CritiqueReport.

        Parameters
        ----------
        worldview_id:
            Identifier of the worldview being critiqued.
        coherence:
            Coherence score from WorldviewEngine in [0, 1].
        ethical_score:
            Overall ethical score in [0, 1].
        contradiction_rate:
            Rate of detected contradictions in [0, 1].
        externality_index:
            Coverage of third-party externalities in [0, 1].
        justice_index:
            Distributive justice index in [0, 1].
        counterfactual_stability:
            Stability under counterfactual reversal in [0, 1].
        common_good_score:
            Common-good alignment score in [0, 1].
        metadata:
            Optional additional metadata.

        Returns
        -------
        CritiqueReport
            Complete critique with flags and sub-scores.
        """
        all_flags: list[CritiqueFlag] = []

        all_flags.extend(
            self._check_logical_consistency(coherence, contradiction_rate)
        )
        all_flags.extend(
            self._check_ethical_implications(ethical_score, externality_index, justice_index)
        )
        all_flags.extend(
            self._check_worldview_coherence(coherence, counterfactual_stability)
        )
        all_flags.extend(
            self._check_normative_alignment(common_good_score)
        )

        consistency_score = self._compute_consistency_score(all_flags)
        ethical_score_out = self._compute_ethical_score(all_flags)
        coherence_score = self._compute_coherence_score(all_flags)
        overall = (consistency_score + ethical_score_out + coherence_score) / 3.0

        has_blocking = any(f.is_blocking for f in all_flags)
        has_warnings = any(
            f.severity == SeverityLevel.WARNING for f in all_flags
        )
        passed = not has_blocking and (not self.strict_mode or not has_warnings)

        return CritiqueReport(
            worldview_id=worldview_id,
            flags=all_flags,
            philosophical_consistency_score=consistency_score,
            ethical_implication_score=ethical_score_out,
            worldview_coherence_score=coherence_score,
            overall_score=overall,
            passed=passed,
            metadata=metadata or {},
        )
