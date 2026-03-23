"""Test suite for worldview.core.worldview — WorldviewEngine and NormativeMetrics."""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from worldview.core.worldview import (
    NormativeMetrics,
    NormativeWeights,
    PropositionalCluster,
    WorldviewAssessment,
    WorldviewEngine,
)

# ---------------------------------------------------------------------------
# NormativeWeights
# ---------------------------------------------------------------------------


class TestNormativeWeights:
    def test_default_weights_sum_to_one(self) -> None:
        w = NormativeWeights()
        total = w.coherence + w.resonance + w.emergence + w.poetics + w.criticality
        assert math.isclose(total, 1.0, abs_tol=1e-6)

    def test_custom_weights_valid(self) -> None:
        w = NormativeWeights(
            coherence=0.2, resonance=0.2, emergence=0.2, poetics=0.2, criticality=0.2
        )
        assert math.isclose(
            w.coherence + w.resonance + w.emergence + w.poetics + w.criticality,
            1.0,
            abs_tol=1e-6,
        )

    def test_weights_not_summing_to_one_raises(self) -> None:
        with pytest.raises(ValidationError):
            NormativeWeights(
                coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5, criticality=0.5
            )

    def test_negative_weight_raises(self) -> None:
        with pytest.raises(ValidationError):
            NormativeWeights(
                coherence=-0.1, resonance=0.3, emergence=0.3, poetics=0.25, criticality=0.25
            )

    def test_weight_above_one_raises(self) -> None:
        with pytest.raises(ValidationError):
            NormativeWeights(
                coherence=1.1, resonance=0.0, emergence=0.0, poetics=0.0, criticality=0.0
            )

    def test_weights_field_names(self) -> None:
        w = NormativeWeights()
        assert hasattr(w, "coherence")
        assert hasattr(w, "resonance")
        assert hasattr(w, "emergence")
        assert hasattr(w, "poetics")
        assert hasattr(w, "criticality")


# ---------------------------------------------------------------------------
# NormativeMetrics
# ---------------------------------------------------------------------------


class TestNormativeMetrics:
    def test_valid_metrics(self) -> None:
        m = NormativeMetrics(
            coherence=0.8,
            resonance=0.7,
            emergence=0.6,
            poetics=0.9,
            criticality=0.5,
            common_good=0.72,
            entropy=1.2,
        )
        assert m.coherence == pytest.approx(0.8)

    def test_score_below_zero_raises(self) -> None:
        with pytest.raises(ValidationError):
            NormativeMetrics(
                coherence=-0.1,
                resonance=0.5,
                emergence=0.5,
                poetics=0.5,
                criticality=0.5,
                common_good=0.5,
                entropy=1.0,
            )

    def test_score_above_one_raises(self) -> None:
        with pytest.raises(ValidationError):
            NormativeMetrics(
                coherence=1.1,
                resonance=0.5,
                emergence=0.5,
                poetics=0.5,
                criticality=0.5,
                common_good=0.5,
                entropy=1.0,
            )

    def test_entropy_zero_valid(self) -> None:
        m = NormativeMetrics(
            coherence=1.0,
            resonance=1.0,
            emergence=1.0,
            poetics=1.0,
            criticality=1.0,
            common_good=1.0,
            entropy=0.0,
        )
        assert m.entropy == 0.0

    def test_entropy_negative_raises(self) -> None:
        with pytest.raises(ValidationError):
            NormativeMetrics(
                coherence=0.5,
                resonance=0.5,
                emergence=0.5,
                poetics=0.5,
                criticality=0.5,
                common_good=0.5,
                entropy=-0.1,
            )


# ---------------------------------------------------------------------------
# PropositionalCluster
# ---------------------------------------------------------------------------


class TestPropositionalCluster:
    def test_default_values(self) -> None:
        c = PropositionalCluster(name="ontology")
        assert c.weight == 1.0
        assert c.internal_consistency == 1.0
        assert c.propositions == []

    def test_valid_cluster(self) -> None:
        c = PropositionalCluster(
            name="ethics",
            propositions=["Harm should be minimised."],
            weight=0.7,
            internal_consistency=0.9,
        )
        assert c.name == "ethics"
        assert len(c.propositions) == 1

    def test_invalid_weight_raises(self) -> None:
        with pytest.raises(ValueError, match="weight"):
            PropositionalCluster(name="bad", weight=1.5)

    def test_invalid_consistency_raises(self) -> None:
        with pytest.raises(ValueError, match="internal_consistency"):
            PropositionalCluster(name="bad", internal_consistency=-0.1)

    def test_zero_weight_valid(self) -> None:
        c = PropositionalCluster(name="zero", weight=0.0)
        assert c.weight == 0.0


# ---------------------------------------------------------------------------
# WorldviewEngine — compute_coherence
# ---------------------------------------------------------------------------


class TestComputeCoherence:
    def setup_method(self) -> None:
        self.engine = WorldviewEngine()

    def test_no_clusters_returns_one(self) -> None:
        assert self.engine.compute_coherence() == pytest.approx(1.0)

    def test_empty_list_returns_one(self) -> None:
        assert self.engine.compute_coherence([]) == pytest.approx(1.0)

    def test_single_perfect_cluster(self) -> None:
        c = PropositionalCluster(name="A", internal_consistency=1.0, weight=1.0)
        result = self.engine.compute_coherence([c])
        assert result == pytest.approx(1.0)

    def test_single_imperfect_cluster(self) -> None:
        c = PropositionalCluster(name="A", internal_consistency=0.5, weight=1.0)
        result = self.engine.compute_coherence([c])
        assert result == pytest.approx(0.5)

    def test_contradiction_std_reduces_coherence(self) -> None:
        c = PropositionalCluster(name="A", internal_consistency=1.0, weight=1.0)
        no_std = self.engine.compute_coherence([c], cross_contradiction_std=0.0)
        with_std = self.engine.compute_coherence([c], cross_contradiction_std=1.0)
        assert with_std < no_std

    def test_multiple_clusters_weighted_average(self) -> None:
        c1 = PropositionalCluster(name="A", internal_consistency=1.0, weight=0.8)
        c2 = PropositionalCluster(name="B", internal_consistency=0.0, weight=0.8)
        result = self.engine.compute_coherence([c1, c2])
        assert result == pytest.approx(0.5)

    def test_zero_weight_cluster_ignored(self) -> None:
        c1 = PropositionalCluster(name="A", internal_consistency=0.8, weight=1.0)
        c2 = PropositionalCluster(name="B", internal_consistency=0.0, weight=0.0)
        result = self.engine.compute_coherence([c1, c2])
        assert result == pytest.approx(0.8)


# ---------------------------------------------------------------------------
# WorldviewEngine — compute_resonance
# ---------------------------------------------------------------------------


class TestComputeResonance:
    def setup_method(self) -> None:
        self.engine = WorldviewEngine()

    def test_no_inputs_returns_half(self) -> None:
        assert self.engine.compute_resonance() == pytest.approx(0.5)

    def test_empty_inputs_returns_half(self) -> None:
        assert self.engine.compute_resonance([], []) == pytest.approx(0.5)

    def test_uniform_unit_vectors(self) -> None:
        phi = [1.0] * 10
        psi = [1.0] * 10
        result = self.engine.compute_resonance(phi, psi)
        assert result == pytest.approx(1.0)

    def test_orthogonal_vectors(self) -> None:
        phi = [1.0, 0.0, 1.0, 0.0]
        psi = [0.0, 1.0, 0.0, 1.0]
        result = self.engine.compute_resonance(phi, psi)
        assert result == pytest.approx(0.0)

    def test_clipped_to_zero(self) -> None:
        phi = [-1.0, -1.0]
        psi = [1.0, 1.0]
        result = self.engine.compute_resonance(phi, psi)
        assert result == pytest.approx(0.0)

    def test_clipped_to_one(self) -> None:
        phi = [10.0] * 5
        psi = [10.0] * 5
        result = self.engine.compute_resonance(phi, psi)
        assert result == pytest.approx(1.0)

    def test_mismatched_lengths_uses_shorter(self) -> None:
        phi = [1.0, 1.0, 1.0]
        psi = [1.0, 1.0]
        result = self.engine.compute_resonance(phi, psi)
        assert 0.0 <= result <= 1.0


# ---------------------------------------------------------------------------
# WorldviewEngine — compute_emergence
# ---------------------------------------------------------------------------


class TestComputeEmergence:
    def setup_method(self) -> None:
        self.engine = WorldviewEngine()

    def test_none_inputs_returns_half(self) -> None:
        assert self.engine.compute_emergence() == pytest.approx(0.5)

    def test_zero_cluster_entropies_returns_half(self) -> None:
        result = self.engine.compute_emergence([0.0], 0.0)
        assert result == pytest.approx(0.5)

    def test_result_in_unit_interval(self) -> None:
        result = self.engine.compute_emergence([1.0, 2.0], 5.0)
        assert 0.0 <= result <= 1.0

    def test_high_global_entropy_boosts_emergence(self) -> None:
        low = self.engine.compute_emergence([1.0], 1.5)
        high = self.engine.compute_emergence([1.0], 3.0)
        assert high >= low


# ---------------------------------------------------------------------------
# WorldviewEngine — compute_poetics
# ---------------------------------------------------------------------------


class TestComputePoetics:
    def setup_method(self) -> None:
        self.engine = WorldviewEngine()

    def test_zero_kl_returns_one(self) -> None:
        assert self.engine.compute_poetics(0.0) == pytest.approx(1.0)

    def test_large_kl_approaches_zero(self) -> None:
        result = self.engine.compute_poetics(100.0)
        assert result < 0.01

    def test_negative_kl_treated_as_zero(self) -> None:
        assert self.engine.compute_poetics(-1.0) == pytest.approx(1.0)

    def test_sensitivity_parameter(self) -> None:
        engine_high = WorldviewEngine(aesthetic_sensitivity=5.0)
        engine_low = WorldviewEngine(aesthetic_sensitivity=0.1)
        assert engine_high.compute_poetics(1.0) < engine_low.compute_poetics(1.0)

    def test_monotone_decrease(self) -> None:
        results = [self.engine.compute_poetics(kl) for kl in [0.0, 0.5, 1.0, 2.0, 5.0]]
        assert all(results[i] >= results[i + 1] for i in range(len(results) - 1))


# ---------------------------------------------------------------------------
# WorldviewEngine — compute_criticality
# ---------------------------------------------------------------------------


class TestComputeCriticality:
    def setup_method(self) -> None:
        self.engine = WorldviewEngine()

    def test_stable_system_returns_half(self) -> None:
        result = self.engine.compute_criticality(0.5, 1.0, 0.0)
        assert result == pytest.approx(0.5)

    def test_zero_coherence_delta_uses_epsilon(self) -> None:
        result = self.engine.compute_criticality(0.0, 0.0, 0.0)
        assert 0.0 <= result <= 1.0

    def test_high_emergence_rate_reduces_criticality(self) -> None:
        stable = self.engine.compute_criticality(0.5, 1.0, 0.0)
        unstable = self.engine.compute_criticality(0.5, 1.0, 0.9)
        assert unstable < stable

    def test_clipped_to_unit_interval(self) -> None:
        result = self.engine.compute_criticality(100.0, 0.01, 0.0)
        assert result == pytest.approx(1.0)

    def test_negative_clipped_to_zero(self) -> None:
        result = self.engine.compute_criticality(-100.0, 1.0, 0.0)
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# WorldviewEngine — compute_common_good
# ---------------------------------------------------------------------------


class TestComputeCommonGood:
    def setup_method(self) -> None:
        self.engine = WorldviewEngine()

    def test_all_ones_returns_one(self) -> None:
        m = {
            "coherence": 1.0,
            "resonance": 1.0,
            "emergence": 1.0,
            "poetics": 1.0,
            "criticality": 1.0,
        }
        assert self.engine.compute_common_good(m) == pytest.approx(1.0)

    def test_all_zeros_returns_zero(self) -> None:
        m = {
            "coherence": 0.0,
            "resonance": 0.0,
            "emergence": 0.0,
            "poetics": 0.0,
            "criticality": 0.0,
        }
        assert self.engine.compute_common_good(m) == pytest.approx(0.0)

    def test_missing_key_defaults_to_zero(self) -> None:
        result = self.engine.compute_common_good({})
        assert result == pytest.approx(0.0)

    def test_partial_metrics(self) -> None:
        result = self.engine.compute_common_good({"coherence": 1.0})
        assert result == pytest.approx(self.engine.weights.coherence)


# ---------------------------------------------------------------------------
# WorldviewEngine — full assess()
# ---------------------------------------------------------------------------


class TestWorldviewEngineAssess:
    def setup_method(self) -> None:
        self.engine = WorldviewEngine()

    def test_returns_assessment_type(self) -> None:
        result = self.engine.assess(worldview_id="test")
        assert isinstance(result, WorldviewAssessment)

    def test_worldview_id_preserved(self) -> None:
        result = self.engine.assess(worldview_id="my-worldview")
        assert result.worldview_id == "my-worldview"

    def test_model_names_stored(self) -> None:
        result = self.engine.assess(worldview_id="x", model_names=["gpt-4o", "llama-3"])
        assert "gpt-4o" in result.model_names
        assert "llama-3" in result.model_names

    def test_metrics_in_unit_interval(self) -> None:
        result = self.engine.assess(worldview_id="bounds-test", entropy=5.0)
        m = result.metrics
        for val in [m.coherence, m.resonance, m.emergence, m.poetics, m.criticality, m.common_good]:
            assert 0.0 <= val <= 1.0

    def test_entropy_stored(self) -> None:
        result = self.engine.assess(worldview_id="entropy-test", entropy=3.14)
        assert result.metrics.entropy == pytest.approx(3.14)

    def test_metadata_stored(self) -> None:
        result = self.engine.assess(worldview_id="meta", metadata={"source": "unit-test"})
        assert result.metadata["source"] == "unit-test"

    def test_zero_entropy(self) -> None:
        result = self.engine.assess(worldview_id="zero", entropy=0.0)
        assert result.metrics.entropy == pytest.approx(0.0)

    def test_high_entropy(self) -> None:
        result = self.engine.assess(worldview_id="high", entropy=100.0)
        assert 0.0 <= result.metrics.common_good <= 1.0

    def test_custom_weights_applied(self) -> None:
        w = NormativeWeights(
            coherence=0.5, resonance=0.1, emergence=0.1, poetics=0.1, criticality=0.2
        )
        engine = WorldviewEngine(weights=w)
        result = engine.assess("custom-weights")
        assert result.weights.coherence == pytest.approx(0.5)

    def test_clusters_influence_coherence(self) -> None:
        clusters = [
            PropositionalCluster(name="A", internal_consistency=0.1, weight=1.0)
        ]
        result_low = self.engine.assess("low", clusters=clusters)
        result_high = self.engine.assess("high")  # no clusters → coherence=1.0
        assert result_high.metrics.coherence >= result_low.metrics.coherence

    def test_kl_divergence_influence(self) -> None:
        r_low = self.engine.assess("kl-low", kl_divergence=0.0)
        r_high = self.engine.assess("kl-high", kl_divergence=10.0)
        assert r_low.metrics.poetics > r_high.metrics.poetics


# ---------------------------------------------------------------------------
# WorldviewAssessment — properties
# ---------------------------------------------------------------------------


class TestWorldviewAssessmentProperties:
    def _make(self, coherence: float = 0.8, common_good: float = 0.8) -> WorldviewAssessment:
        m = NormativeMetrics(
            coherence=coherence,
            resonance=0.7,
            emergence=0.6,
            poetics=0.8,
            criticality=0.7,
            common_good=common_good,
            entropy=1.0,
        )
        return WorldviewAssessment(
            worldview_id="prop-test",
            metrics=m,
            weights=NormativeWeights(),
        )

    def test_is_coherent_true(self) -> None:
        assert self._make(coherence=0.7).is_coherent is True

    def test_is_coherent_false(self) -> None:
        assert self._make(coherence=0.4).is_coherent is False

    def test_is_coherent_boundary(self) -> None:
        assert self._make(coherence=0.6).is_coherent is True

    def test_is_aligned_true(self) -> None:
        assert self._make(common_good=0.6).is_aligned is True

    def test_is_aligned_false(self) -> None:
        assert self._make(common_good=0.4).is_aligned is False

    def test_grade_a(self) -> None:
        assert self._make(common_good=0.95).grade == "A"

    def test_grade_b(self) -> None:
        assert self._make(common_good=0.8).grade == "B"

    def test_grade_c(self) -> None:
        assert self._make(common_good=0.65).grade == "C"

    def test_grade_d(self) -> None:
        assert self._make(common_good=0.5).grade == "D"

    def test_grade_f(self) -> None:
        assert self._make(common_good=0.3).grade == "F"

    def test_critique_flags_empty_by_default(self) -> None:
        assert self._make().critique_flags == []

    def test_model_names_list(self) -> None:
        a = self._make()
        assert isinstance(a.model_names, list)
