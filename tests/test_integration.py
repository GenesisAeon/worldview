"""Integration tests — WorldviewEngine + CriticalityChecker + AlignmentFramework."""

from __future__ import annotations

import pytest

from worldview.core.critique import CriticalityChecker
from worldview.core.worldview import (
    NormativeWeights,
    PropositionalCluster,
    WorldviewEngine,
)
from worldview.governance.alignment import AlignmentFramework, PersonhoodLevel

# ---------------------------------------------------------------------------
# Full pipeline: assess → critique → align
# ---------------------------------------------------------------------------


class TestFullPipeline:
    def setup_method(self) -> None:
        self.engine = WorldviewEngine()
        self.checker = CriticalityChecker()
        self.framework = AlignmentFramework()

    def test_full_pipeline_high_quality(self) -> None:
        assessment = self.engine.assess(
            worldview_id="pipeline-high",
            entropy=1.0,
            clusters=[
                PropositionalCluster("epistemology", internal_consistency=0.95),
                PropositionalCluster("ethics", internal_consistency=0.90),
                PropositionalCluster("ontology", internal_consistency=0.85),
            ],
            kl_divergence=0.1,
        )
        report = self.checker.check(
            worldview_id=assessment.worldview_id,
            coherence=assessment.metrics.coherence,
            ethical_score=0.9,
            externality_index=0.9,
            justice_index=0.9,
            common_good_score=assessment.metrics.common_good,
        )
        metric = self.framework.evaluate(
            entity_id="pipeline-agent",
            scores={"solidarity": 0.8, "justice": 0.85, "dignity": 0.9,
                    "sustainability": 0.75, "freedom": 0.7, "participation": 0.8},
            personhood_level=PersonhoodLevel.NORMATIVE,
        )
        assert report.passed
        assert metric.composite_score > 0.5
        assert assessment.is_coherent

    def test_full_pipeline_low_quality_fails(self) -> None:
        assessment = self.engine.assess(
            worldview_id="pipeline-low",
            entropy=8.0,
            clusters=[
                PropositionalCluster("epistemology", internal_consistency=0.1),
            ],
            kl_divergence=5.0,
            cross_contradiction_std=0.8,
        )
        report = self.checker.check(
            worldview_id=assessment.worldview_id,
            coherence=assessment.metrics.coherence,
            ethical_score=0.2,
            contradiction_rate=0.8,
            externality_index=0.1,
            justice_index=0.1,
            common_good_score=0.1,
        )
        assert not report.passed

    def test_assessment_feeds_critique_scores(self) -> None:
        assessment = self.engine.assess("feed-test", entropy=2.0)
        report = self.checker.check(
            worldview_id=assessment.worldview_id,
            coherence=assessment.metrics.coherence,
            common_good_score=assessment.metrics.common_good,
        )
        assert report.worldview_id == assessment.worldview_id

    def test_personhood_weight_scales_composite(self) -> None:
        w_low = AlignmentFramework.personhood_weight(PersonhoodLevel.REACTIVE)
        w_high = AlignmentFramework.personhood_weight(PersonhoodLevel.TRANSCENDENT)
        assert w_high > w_low

    def test_custom_weights_propagate_correctly(self) -> None:
        weights = NormativeWeights(
            coherence=0.5,
            resonance=0.1,
            emergence=0.1,
            poetics=0.1,
            criticality=0.2,
        )
        engine = WorldviewEngine(weights=weights)
        result = engine.assess("custom-w")
        assert result.weights.coherence == pytest.approx(0.5)

    def test_entropy_range_full_pipeline(self) -> None:
        for entropy in [0.0, 1.0, 5.0, 10.0]:
            result = self.engine.assess(f"entropy-{entropy}", entropy=entropy)
            assert 0.0 <= result.metrics.common_good <= 1.0

    def test_critique_flags_propagate_to_worldview(self) -> None:
        assessment = self.engine.assess("flag-prop")
        report = self.checker.check(
            worldview_id=assessment.worldview_id,
            ethical_score=0.1,
        )
        assessment.critique_flags = [f.crep_ref for f in report.flags]
        assert len(assessment.critique_flags) > 0

    def test_gap_analysis_reflects_low_scores(self) -> None:
        metric = self.framework.evaluate(
            "gap-test",
            {"solidarity": 0.2, "justice": 0.3},
        )
        gaps = self.framework.gap_analysis(metric)
        assert gaps["solidarity"] == pytest.approx(0.8, abs=1e-4)
        assert gaps["justice"] == pytest.approx(0.7, abs=1e-4)

    def test_dimension_entropy_increases_with_spread(self) -> None:
        concentrated = self.framework.evaluate(
            "concentrated",
            {"solidarity": 1.0, "sustainability": 0.0, "justice": 0.0,
             "freedom": 0.0, "dignity": 0.0, "participation": 0.0},
        )
        spread = self.framework.evaluate(
            "spread",
            dict.fromkeys(
                ["solidarity", "sustainability", "justice", "freedom", "dignity", "participation"],
                0.5,
            ),
        )
        h_conc = self.framework.dimension_entropy(concentrated)
        h_spread = self.framework.dimension_entropy(spread)
        assert h_spread >= h_conc

    def test_multiple_models_stored(self) -> None:
        result = self.engine.assess(
            "multi-model",
            model_names=["gpt-4o", "claude-3", "llama-3", "mistral"],
        )
        assert len(result.model_names) == 4

    def test_assessment_serialisable_to_dict(self) -> None:
        result = self.engine.assess("serial")
        d = result.model_dump()
        assert isinstance(d, dict)
        assert "metrics" in d

    def test_critique_report_serialisable_to_dict(self) -> None:
        report = self.checker.check("serial-report")
        d = report.model_dump()
        assert isinstance(d, dict)
        assert "flags" in d

    def test_common_good_metric_serialisable(self) -> None:
        metric = self.framework.evaluate("serial-metric", {"solidarity": 0.7})
        d = metric.model_dump()
        assert isinstance(d, dict)
        assert "dimensions" in d
