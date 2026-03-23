"""Test suite for worldview.governance.alignment — AlignmentFramework and metrics."""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from worldview.governance.alignment import (
    DEFAULT_DIMENSIONS,
    AlignmentFramework,
    CommonGoodDimension,
    CommonGoodMetric,
    PersonhoodLevel,
)

# ---------------------------------------------------------------------------
# PersonhoodLevel
# ---------------------------------------------------------------------------


class TestPersonhoodLevel:
    def test_values_range_0_to_6(self) -> None:
        assert min(PersonhoodLevel) == 0
        assert max(PersonhoodLevel) == 6

    def test_non_entity_label(self) -> None:
        assert "Non" in PersonhoodLevel.NON_ENTITY.label

    def test_transcendent_label(self) -> None:
        assert "Transcendent" in PersonhoodLevel.TRANSCENDENT.label

    def test_moral_agency_level_5_and_6(self) -> None:
        assert PersonhoodLevel.NORMATIVE.has_moral_agency is True
        assert PersonhoodLevel.TRANSCENDENT.has_moral_agency is True

    def test_no_moral_agency_below_5(self) -> None:
        for level in [
            PersonhoodLevel.NON_ENTITY,
            PersonhoodLevel.REACTIVE,
            PersonhoodLevel.ADAPTIVE,
            PersonhoodLevel.SELF_MODELLING,
            PersonhoodLevel.REFLECTIVE,
        ]:
            assert level.has_moral_agency is False

    def test_has_self_model_from_level_3(self) -> None:
        assert PersonhoodLevel.SELF_MODELLING.has_self_model is True
        assert PersonhoodLevel.NORMATIVE.has_self_model is True

    def test_no_self_model_below_3(self) -> None:
        assert PersonhoodLevel.REACTIVE.has_self_model is False
        assert PersonhoodLevel.ADAPTIVE.has_self_model is False

    def test_integer_comparison(self) -> None:
        assert PersonhoodLevel.NORMATIVE > PersonhoodLevel.ADAPTIVE
        assert PersonhoodLevel.NON_ENTITY < PersonhoodLevel.REFLECTIVE

    def test_all_labels_non_empty(self) -> None:
        for level in PersonhoodLevel:
            assert len(level.label) > 0


# ---------------------------------------------------------------------------
# CommonGoodDimension
# ---------------------------------------------------------------------------


class TestCommonGoodDimension:
    def test_valid_dimension(self) -> None:
        d = CommonGoodDimension(name="solidarity", score=0.8, weight=1.5)
        assert d.score == pytest.approx(0.8)

    def test_score_below_zero_raises(self) -> None:
        with pytest.raises(ValidationError):
            CommonGoodDimension(name="x", score=-0.1)

    def test_score_above_one_raises(self) -> None:
        with pytest.raises(ValidationError):
            CommonGoodDimension(name="x", score=1.1)

    def test_zero_weight_raises(self) -> None:
        with pytest.raises(ValidationError):
            CommonGoodDimension(name="x", score=0.5, weight=0.0)

    def test_description_default_empty(self) -> None:
        d = CommonGoodDimension(name="x", score=0.5)
        assert d.description == ""

    def test_boundary_score_zero(self) -> None:
        d = CommonGoodDimension(name="x", score=0.0)
        assert d.score == 0.0

    def test_boundary_score_one(self) -> None:
        d = CommonGoodDimension(name="x", score=1.0)
        assert d.score == 1.0


# ---------------------------------------------------------------------------
# CommonGoodMetric — composite score
# ---------------------------------------------------------------------------


class TestCommonGoodMetric:
    def _metric(self, scores: list[tuple[str, float, float]]) -> CommonGoodMetric:
        dims = [
            CommonGoodDimension(name=n, score=s, weight=w)
            for n, s, w in scores
        ]
        return CommonGoodMetric(
            entity_id="test",
            dimensions=dims,
            personhood_level=PersonhoodLevel.ADAPTIVE,
        )

    def test_all_ones_composite_is_one(self) -> None:
        m = self._metric([("a", 1.0, 1.0), ("b", 1.0, 1.0)])
        assert m.composite_score == pytest.approx(1.0)

    def test_all_zeros_composite_is_zero(self) -> None:
        m = self._metric([("a", 0.0, 1.0), ("b", 0.0, 1.0)])
        assert m.composite_score == pytest.approx(0.0)

    def test_weighted_average(self) -> None:
        m = self._metric([("a", 1.0, 2.0), ("b", 0.0, 2.0)])
        assert m.composite_score == pytest.approx(0.5)

    def test_empty_dimensions_composite_zero(self) -> None:
        m = CommonGoodMetric(entity_id="empty")
        assert m.composite_score == pytest.approx(0.0)

    def test_socially_beneficial_true(self) -> None:
        m = self._metric([("a", 1.0, 1.0)])
        assert m.is_socially_beneficial is True

    def test_socially_beneficial_false(self) -> None:
        m = self._metric([("a", 0.5, 1.0)])
        assert m.is_socially_beneficial is False

    def test_grade_a_plus(self) -> None:
        m = self._metric([("a", 0.95, 1.0)])
        assert m.grade == "A+"

    def test_grade_a(self) -> None:
        m = self._metric([("a", 0.85, 1.0)])
        assert m.grade == "A"

    def test_grade_b(self) -> None:
        m = self._metric([("a", 0.75, 1.0)])
        assert m.grade == "B"

    def test_grade_c(self) -> None:
        m = self._metric([("a", 0.65, 1.0)])
        assert m.grade == "C"

    def test_grade_d(self) -> None:
        m = self._metric([("a", 0.55, 1.0)])
        assert m.grade == "D"

    def test_grade_f(self) -> None:
        m = self._metric([("a", 0.4, 1.0)])
        assert m.grade == "F"

    def test_composite_in_unit_interval(self) -> None:
        m = self._metric([("a", 0.7, 3.0), ("b", 0.3, 1.0)])
        assert 0.0 <= m.composite_score <= 1.0


# ---------------------------------------------------------------------------
# DEFAULT_DIMENSIONS
# ---------------------------------------------------------------------------


class TestDefaultDimensions:
    def test_six_dimensions(self) -> None:
        assert len(DEFAULT_DIMENSIONS) == 6

    def test_expected_names_present(self) -> None:
        names = {d["name"] for d in DEFAULT_DIMENSIONS}
        all_dims = [
            "solidarity", "sustainability", "justice", "freedom", "dignity", "participation"
        ]
        for expected in all_dims:
            assert expected in names

    def test_all_have_positive_weights(self) -> None:
        for d in DEFAULT_DIMENSIONS:
            assert d["weight"] > 0


# ---------------------------------------------------------------------------
# AlignmentFramework — evaluate
# ---------------------------------------------------------------------------


class TestAlignmentFrameworkEvaluate:
    def setup_method(self) -> None:
        self.framework = AlignmentFramework()

    def test_returns_common_good_metric(self) -> None:
        result = self.framework.evaluate("agent-1", {})
        assert isinstance(result, CommonGoodMetric)

    def test_entity_id_preserved(self) -> None:
        result = self.framework.evaluate("my-agent", {})
        assert result.entity_id == "my-agent"

    def test_missing_scores_default_to_zero(self) -> None:
        result = self.framework.evaluate("zeroes", {})
        for dim in result.dimensions:
            assert dim.score == pytest.approx(0.0)

    def test_full_scores_compute_high_composite(self) -> None:
        full = {d["name"]: 1.0 for d in DEFAULT_DIMENSIONS}
        result = self.framework.evaluate("perfect", full)
        assert result.composite_score == pytest.approx(1.0)

    def test_partial_scores(self) -> None:
        result = self.framework.evaluate("partial", {"solidarity": 0.8, "justice": 0.9})
        assert result.composite_score > 0.0

    def test_personhood_level_stored(self) -> None:
        result = self.framework.evaluate(
            "agent", {}, personhood_level=PersonhoodLevel.NORMATIVE
        )
        assert result.personhood_level == PersonhoodLevel.NORMATIVE

    def test_score_clamped_to_unit_interval(self) -> None:
        result = self.framework.evaluate("clamped", {"solidarity": 2.0})
        sol = next(d for d in result.dimensions if d.name == "solidarity")
        assert sol.score <= 1.0

    def test_custom_dimension_weights(self) -> None:
        fw = AlignmentFramework(dimension_weights={"justice": 10.0})
        result = fw.evaluate("weighted", {"justice": 1.0})
        justice_dim = next(d for d in result.dimensions if d.name == "justice")
        assert justice_dim.weight == pytest.approx(10.0)

    def test_six_dimensions_returned(self) -> None:
        result = self.framework.evaluate("six", {})
        assert len(result.dimensions) == 6

    def test_composite_monotone_with_scores(self) -> None:
        low = self.framework.evaluate("low", {d["name"]: 0.2 for d in DEFAULT_DIMENSIONS})
        high = self.framework.evaluate("high", {d["name"]: 0.8 for d in DEFAULT_DIMENSIONS})
        assert high.composite_score > low.composite_score


# ---------------------------------------------------------------------------
# AlignmentFramework — assess_personhood
# ---------------------------------------------------------------------------


class TestAlignmentFrameworkAssessPersonhood:
    def setup_method(self) -> None:
        self.framework = AlignmentFramework()

    def test_collective_moral_agent_is_transcendent(self) -> None:
        level = self.framework.assess_personhood(
            has_moral_agency=True, operates_collectively=True
        )
        assert level == PersonhoodLevel.TRANSCENDENT

    def test_moral_agent_is_normative(self) -> None:
        level = self.framework.assess_personhood(has_moral_agency=True)
        assert level == PersonhoodLevel.NORMATIVE

    def test_self_model_is_self_modelling(self) -> None:
        level = self.framework.assess_personhood(has_self_model=True)
        assert level == PersonhoodLevel.SELF_MODELLING

    def test_learner_is_adaptive(self) -> None:
        level = self.framework.assess_personhood(is_learning=True)
        assert level == PersonhoodLevel.ADAPTIVE

    def test_bare_minimum_is_reactive(self) -> None:
        level = self.framework.assess_personhood()
        assert level == PersonhoodLevel.REACTIVE


# ---------------------------------------------------------------------------
# AlignmentFramework — dimension_entropy
# ---------------------------------------------------------------------------


class TestAlignmentFrameworkEntropy:
    def setup_method(self) -> None:
        self.framework = AlignmentFramework()

    def test_uniform_scores_maximum_entropy(self) -> None:
        scores = {d["name"]: 0.5 for d in DEFAULT_DIMENSIONS}
        metric = self.framework.evaluate("uniform", scores)
        entropy = self.framework.dimension_entropy(metric)
        assert entropy > 0.0

    def test_zero_scores_entropy_zero(self) -> None:
        metric = self.framework.evaluate("zeros", {})
        entropy = self.framework.dimension_entropy(metric)
        assert entropy == pytest.approx(0.0)

    def test_entropy_nonnegative(self) -> None:
        scores = {d["name"]: 0.3 for d in DEFAULT_DIMENSIONS}
        metric = self.framework.evaluate("pos", scores)
        assert self.framework.dimension_entropy(metric) >= 0.0


# ---------------------------------------------------------------------------
# AlignmentFramework — gap_analysis
# ---------------------------------------------------------------------------


class TestAlignmentFrameworkGapAnalysis:
    def setup_method(self) -> None:
        self.framework = AlignmentFramework()

    def test_perfect_scores_zero_gap(self) -> None:
        scores = {d["name"]: 1.0 for d in DEFAULT_DIMENSIONS}
        metric = self.framework.evaluate("perfect", scores)
        gaps = self.framework.gap_analysis(metric)
        for gap in gaps.values():
            assert gap == pytest.approx(0.0, abs=1e-4)

    def test_zero_scores_gap_is_one(self) -> None:
        metric = self.framework.evaluate("zeros", {})
        gaps = self.framework.gap_analysis(metric)
        for gap in gaps.values():
            assert gap == pytest.approx(1.0, abs=1e-4)

    def test_gap_keys_match_dimension_names(self) -> None:
        metric = self.framework.evaluate("keys", {})
        gaps = self.framework.gap_analysis(metric)
        dim_names = {d.name for d in metric.dimensions}
        assert set(gaps.keys()) == dim_names

    def test_partial_gap(self) -> None:
        metric = self.framework.evaluate("partial", {"solidarity": 0.6})
        gaps = self.framework.gap_analysis(metric)
        assert gaps["solidarity"] == pytest.approx(0.4, abs=1e-4)


# ---------------------------------------------------------------------------
# AlignmentFramework — personhood_weight
# ---------------------------------------------------------------------------


class TestPersonhoodWeight:
    def test_non_entity_positive_weight(self) -> None:
        w = AlignmentFramework.personhood_weight(PersonhoodLevel.NON_ENTITY)
        assert w > 0.0

    def test_transcendent_highest_weight(self) -> None:
        weights = [AlignmentFramework.personhood_weight(lvl) for lvl in PersonhoodLevel]
        assert weights[-1] == max(weights)

    def test_weight_monotone_increasing(self) -> None:
        weights = [AlignmentFramework.personhood_weight(lvl) for lvl in PersonhoodLevel]
        assert all(weights[i] <= weights[i + 1] for i in range(len(weights) - 1))

    def test_weight_uses_log2(self) -> None:
        w = AlignmentFramework.personhood_weight(PersonhoodLevel.NORMATIVE)
        expected = math.log2(PersonhoodLevel.NORMATIVE + 2)
        assert w == pytest.approx(expected)
