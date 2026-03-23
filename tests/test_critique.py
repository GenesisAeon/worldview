"""Test suite for worldview.core.critique — CriticalityChecker and CritiqueReport."""

from __future__ import annotations

import pytest

from worldview.core.critique import (
    CREP_RULES,
    CheckerRule,
    CriticalityChecker,
    CritiqueCategory,
    CritiqueFlag,
    CritiqueReport,
    SeverityLevel,
)

# ---------------------------------------------------------------------------
# SeverityLevel
# ---------------------------------------------------------------------------


class TestSeverityLevel:
    def test_info_value(self) -> None:
        assert SeverityLevel.INFO.value == "info"

    def test_critical_value(self) -> None:
        assert SeverityLevel.CRITICAL.value == "critical"

    def test_ordering_by_name(self) -> None:
        levels = list(SeverityLevel)
        assert SeverityLevel.INFO in levels
        assert SeverityLevel.WARNING in levels

    def test_string_comparison(self) -> None:
        assert SeverityLevel.ERROR == "error"


# ---------------------------------------------------------------------------
# CritiqueCategory
# ---------------------------------------------------------------------------


class TestCritiqueCategory:
    def test_all_expected_categories_exist(self) -> None:
        expected = {
            "logical_consistency",
            "ethical_implication",
            "worldview_coherence",
            "scope_validity",
            "temporal_consistency",
            "anthropocentric_bias",
            "epistemic_humility",
            "normative_alignment",
        }
        actual = {c.value for c in CritiqueCategory}
        assert expected.issubset(actual)


# ---------------------------------------------------------------------------
# CritiqueFlag
# ---------------------------------------------------------------------------


class TestCritiqueFlag:
    def _make(
        self,
        severity: SeverityLevel = SeverityLevel.WARNING,
    ) -> CritiqueFlag:
        return CritiqueFlag(
            category=CritiqueCategory.LOGICAL_CONSISTENCY,
            severity=severity,
            message="Test flag.",
            crep_ref="CREP-TEST",
        )

    def test_info_not_blocking(self) -> None:
        assert self._make(SeverityLevel.INFO).is_blocking is False

    def test_warning_not_blocking(self) -> None:
        assert self._make(SeverityLevel.WARNING).is_blocking is False

    def test_error_is_blocking(self) -> None:
        assert self._make(SeverityLevel.ERROR).is_blocking is True

    def test_critical_is_blocking(self) -> None:
        assert self._make(SeverityLevel.CRITICAL).is_blocking is True

    def test_optional_fields_default_empty(self) -> None:
        flag = self._make()
        assert flag.evidence == ""
        assert flag.remediation == ""

    def test_full_flag_construction(self) -> None:
        flag = CritiqueFlag(
            category=CritiqueCategory.ETHICAL_IMPLICATION,
            severity=SeverityLevel.ERROR,
            message="Externalities ignored.",
            evidence="No third-party impact considered.",
            remediation="Expand scope.",
            crep_ref="CREP-E1",
        )
        assert flag.crep_ref == "CREP-E1"
        assert flag.evidence != ""


# ---------------------------------------------------------------------------
# CritiqueReport
# ---------------------------------------------------------------------------


class TestCritiqueReport:
    def _report(self, flags: list[CritiqueFlag] | None = None) -> CritiqueReport:
        return CritiqueReport(
            worldview_id="report-test",
            flags=flags or [],
            philosophical_consistency_score=0.9,
            ethical_implication_score=0.85,
            worldview_coherence_score=0.8,
            overall_score=0.85,
            passed=True,
        )

    def test_no_flags_empty_blocking(self) -> None:
        report = self._report()
        assert report.blocking_flags == []

    def test_blocking_flag_counted(self) -> None:
        flag = CritiqueFlag(
            category=CritiqueCategory.ETHICAL_IMPLICATION,
            severity=SeverityLevel.ERROR,
            message="blocking",
        )
        report = self._report([flag])
        assert len(report.blocking_flags) == 1

    def test_non_blocking_not_in_blocking(self) -> None:
        flag = CritiqueFlag(
            category=CritiqueCategory.EPISTEMIC_HUMILITY,
            severity=SeverityLevel.INFO,
            message="informational",
        )
        report = self._report([flag])
        assert report.blocking_flags == []

    def test_flag_count_by_severity_structure(self) -> None:
        counts = self._report().flag_count_by_severity
        assert "info" in counts
        assert "warning" in counts
        assert "error" in counts
        assert "critical" in counts

    def test_flag_count_accurate(self) -> None:
        flags = [
            CritiqueFlag(
                category=CritiqueCategory.LOGICAL_CONSISTENCY,
                severity=SeverityLevel.WARNING,
                message="w1",
            ),
            CritiqueFlag(
                category=CritiqueCategory.ETHICAL_IMPLICATION,
                severity=SeverityLevel.WARNING,
                message="w2",
            ),
            CritiqueFlag(
                category=CritiqueCategory.WORLDVIEW_COHERENCE,
                severity=SeverityLevel.ERROR,
                message="e1",
            ),
        ]
        report = self._report(flags)
        counts = report.flag_count_by_severity
        assert counts["warning"] == 2
        assert counts["error"] == 1

    def test_has_ethical_concerns_below_threshold(self) -> None:
        report = CritiqueReport(
            worldview_id="x",
            ethical_implication_score=0.5,
            overall_score=0.5,
        )
        assert report.has_ethical_concerns is True

    def test_no_ethical_concerns_above_threshold(self) -> None:
        report = CritiqueReport(
            worldview_id="x",
            ethical_implication_score=0.8,
            overall_score=0.8,
        )
        assert report.has_ethical_concerns is False


# ---------------------------------------------------------------------------
# CREP_RULES catalogue
# ---------------------------------------------------------------------------


class TestCREPRules:
    def test_rules_not_empty(self) -> None:
        assert len(CREP_RULES) > 0

    def test_all_rules_have_crep_ref(self) -> None:
        for rule in CREP_RULES:
            assert rule.crep_ref.startswith("CREP-")

    def test_expected_refs_present(self) -> None:
        refs = {r.crep_ref for r in CREP_RULES}
        for expected in ["CREP-L1", "CREP-E1", "CREP-C1", "CREP-N1"]:
            assert expected in refs

    def test_rules_have_valid_categories(self) -> None:
        valid_cats = set(CritiqueCategory)
        for rule in CREP_RULES:
            assert rule.category in valid_cats

    def test_rules_have_valid_severities(self) -> None:
        valid_sev = set(SeverityLevel)
        for rule in CREP_RULES:
            assert rule.severity in valid_sev

    def test_checker_rule_dataclass(self) -> None:
        rule = CheckerRule(
            crep_ref="CREP-X99",
            category=CritiqueCategory.SCOPE_VALIDITY,
            description="Custom rule.",
            threshold=0.3,
            severity=SeverityLevel.INFO,
        )
        assert rule.crep_ref == "CREP-X99"


# ---------------------------------------------------------------------------
# CriticalityChecker — clean worldview
# ---------------------------------------------------------------------------


class TestCriticalityCheckerClean:
    def setup_method(self) -> None:
        self.checker = CriticalityChecker()

    def test_perfect_worldview_passes(self) -> None:
        report = self.checker.check(
            worldview_id="perfect",
            coherence=1.0,
            ethical_score=1.0,
            contradiction_rate=0.0,
            externality_index=1.0,
            justice_index=1.0,
            counterfactual_stability=1.0,
            common_good_score=1.0,
        )
        assert report.passed is True

    def test_perfect_worldview_no_flags(self) -> None:
        report = self.checker.check(
            worldview_id="clean",
            coherence=1.0,
            ethical_score=1.0,
            contradiction_rate=0.0,
            externality_index=1.0,
            justice_index=1.0,
            counterfactual_stability=1.0,
            common_good_score=1.0,
        )
        assert len(report.flags) == 0

    def test_perfect_overall_score_near_one(self) -> None:
        report = self.checker.check(
            worldview_id="near-one",
            coherence=1.0,
            ethical_score=1.0,
        )
        assert report.overall_score == pytest.approx(1.0, abs=1e-6)


# ---------------------------------------------------------------------------
# CriticalityChecker — logical consistency flags
# ---------------------------------------------------------------------------


class TestCriticalityCheckerLogical:
    def setup_method(self) -> None:
        self.checker = CriticalityChecker()

    def test_high_contradiction_rate_raises_error(self) -> None:
        report = self.checker.check(
            worldview_id="contradictions",
            contradiction_rate=0.9,
        )
        crep_l1_flags = [f for f in report.flags if f.crep_ref == "CREP-L1"]
        assert len(crep_l1_flags) > 0
        assert any(f.severity == SeverityLevel.ERROR for f in crep_l1_flags)

    def test_low_coherence_raises_cross_cluster_warning(self) -> None:
        report = self.checker.check(
            worldview_id="low-coherence",
            coherence=0.1,
        )
        crep_l2_flags = [f for f in report.flags if f.crep_ref == "CREP-L2"]
        assert len(crep_l2_flags) > 0

    def test_high_coherence_no_logical_flags(self) -> None:
        report = self.checker.check(
            worldview_id="coherent",
            coherence=0.9,
            contradiction_rate=0.0,
        )
        logical = [
            f for f in report.flags
            if f.category == CritiqueCategory.LOGICAL_CONSISTENCY
        ]
        assert logical == []

    def test_logical_error_blocks_report(self) -> None:
        report = self.checker.check(
            worldview_id="blocked",
            contradiction_rate=0.95,
        )
        assert report.passed is False


# ---------------------------------------------------------------------------
# CriticalityChecker — ethical flags
# ---------------------------------------------------------------------------


class TestCriticalityCheckerEthical:
    def setup_method(self) -> None:
        self.checker = CriticalityChecker()

    def test_low_externality_index_raises_error(self) -> None:
        report = self.checker.check(
            worldview_id="no-externality",
            externality_index=0.1,
        )
        crep_e1_flags = [f for f in report.flags if f.crep_ref == "CREP-E1"]
        assert len(crep_e1_flags) > 0

    def test_low_justice_index_raises_warning(self) -> None:
        report = self.checker.check(
            worldview_id="unjust",
            justice_index=0.1,
        )
        crep_e3_flags = [f for f in report.flags if f.crep_ref == "CREP-E3"]
        assert len(crep_e3_flags) > 0

    def test_critical_ethical_score_raises_critical_flag(self) -> None:
        report = self.checker.check(
            worldview_id="critical-ethics",
            ethical_score=0.1,
        )
        assert any(f.severity == SeverityLevel.CRITICAL for f in report.flags)

    def test_good_ethics_no_ethical_flags(self) -> None:
        report = self.checker.check(
            worldview_id="good-ethics",
            ethical_score=0.9,
            externality_index=0.9,
            justice_index=0.9,
        )
        ethical_flags = [
            f for f in report.flags
            if f.category == CritiqueCategory.ETHICAL_IMPLICATION
        ]
        assert ethical_flags == []


# ---------------------------------------------------------------------------
# CriticalityChecker — worldview coherence flags
# ---------------------------------------------------------------------------


class TestCriticalityCheckerCoherence:
    def setup_method(self) -> None:
        self.checker = CriticalityChecker()

    def test_low_counterfactual_stability_raises_warning(self) -> None:
        report = self.checker.check(
            worldview_id="brittle",
            counterfactual_stability=0.1,
        )
        crep_c1_flags = [f for f in report.flags if f.crep_ref == "CREP-C1"]
        assert len(crep_c1_flags) > 0

    def test_very_low_coherence_raises_metaphysical_error(self) -> None:
        report = self.checker.check(
            worldview_id="incoherent",
            coherence=0.1,
        )
        crep_c2_flags = [f for f in report.flags if f.crep_ref == "CREP-C2"]
        assert len(crep_c2_flags) > 0


# ---------------------------------------------------------------------------
# CriticalityChecker — normative alignment flags
# ---------------------------------------------------------------------------


class TestCriticalityCheckerNormative:
    def setup_method(self) -> None:
        self.checker = CriticalityChecker()

    def test_low_common_good_raises_normative_error(self) -> None:
        report = self.checker.check(
            worldview_id="low-cg",
            common_good_score=0.1,
        )
        crep_n1_flags = [f for f in report.flags if f.crep_ref == "CREP-N1"]
        assert len(crep_n1_flags) > 0

    def test_high_common_good_no_normative_flags(self) -> None:
        report = self.checker.check(
            worldview_id="high-cg",
            common_good_score=0.9,
        )
        normative_flags = [
            f for f in report.flags
            if f.category == CritiqueCategory.NORMATIVE_ALIGNMENT
        ]
        assert normative_flags == []


# ---------------------------------------------------------------------------
# CriticalityChecker — strict mode
# ---------------------------------------------------------------------------


class TestCriticalityCheckerStrictMode:
    def test_strict_mode_warning_fails(self) -> None:
        checker = CriticalityChecker(strict_mode=True)
        report = checker.check(
            worldview_id="strict-warn",
            coherence=0.5,  # may produce WARNING
            counterfactual_stability=0.3,
        )
        if any(f.severity == SeverityLevel.WARNING for f in report.flags):
            assert report.passed is False

    def test_non_strict_warning_passes(self) -> None:
        checker = CriticalityChecker(strict_mode=False)
        report = checker.check(
            worldview_id="lenient",
            coherence=1.0,
            ethical_score=1.0,
            contradiction_rate=0.0,
            externality_index=1.0,
            justice_index=1.0,
            counterfactual_stability=1.0,
            common_good_score=1.0,
        )
        assert report.passed is True

    def test_custom_rules_respected(self) -> None:
        custom_rule = CheckerRule(
            crep_ref="CREP-CUSTOM",
            category=CritiqueCategory.SCOPE_VALIDITY,
            description="Always passes.",
            threshold=0.0,
            severity=SeverityLevel.INFO,
        )
        checker = CriticalityChecker(rules=[custom_rule])
        report = checker.check(worldview_id="custom-rules")
        assert all(f.crep_ref != "CREP-L1" for f in report.flags)


# ---------------------------------------------------------------------------
# CriticalityChecker — score sub-components
# ---------------------------------------------------------------------------


class TestCriticalityCheckerScores:
    def setup_method(self) -> None:
        self.checker = CriticalityChecker()

    def test_sub_scores_in_unit_interval(self) -> None:
        report = self.checker.check(
            worldview_id="scores",
            coherence=0.5,
            ethical_score=0.5,
            contradiction_rate=0.2,
        )
        assert 0.0 <= report.philosophical_consistency_score <= 1.0
        assert 0.0 <= report.ethical_implication_score <= 1.0
        assert 0.0 <= report.worldview_coherence_score <= 1.0
        assert 0.0 <= report.overall_score <= 1.0

    def test_overall_is_mean_of_sub_scores(self) -> None:
        report = self.checker.check(worldview_id="mean-check")
        expected = (
            report.philosophical_consistency_score
            + report.ethical_implication_score
            + report.worldview_coherence_score
        ) / 3.0
        assert report.overall_score == pytest.approx(expected, abs=1e-6)

    def test_metadata_stored(self) -> None:
        report = self.checker.check(
            worldview_id="meta",
            metadata={"run": "test-suite"},
        )
        assert report.metadata["run"] == "test-suite"

    def test_worldview_id_preserved(self) -> None:
        report = self.checker.check(worldview_id="my-id-42")
        assert report.worldview_id == "my-id-42"
