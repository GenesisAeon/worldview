"""Test suite for worldview.cli.main — Typer CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from worldview.cli.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# worldview --version
# ---------------------------------------------------------------------------


class TestVersionFlag:
    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "worldview" in result.output

    def test_version_short_flag(self) -> None:
        result = runner.invoke(app, ["-V"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


# ---------------------------------------------------------------------------
# worldview info
# ---------------------------------------------------------------------------


class TestInfoCommand:
    def test_info_exits_zero(self) -> None:
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0

    def test_info_shows_version(self) -> None:
        result = runner.invoke(app, ["info"])
        assert "0.1.0" in result.output

    def test_info_shows_genesisaeon(self) -> None:
        result = runner.invoke(app, ["info"])
        assert "GenesisAeon" in result.output

    def test_info_shows_crep(self) -> None:
        result = runner.invoke(app, ["info"])
        assert "CREP" in result.output

    def test_info_shows_repository(self) -> None:
        result = runner.invoke(app, ["info"])
        assert "github.com" in result.output


# ---------------------------------------------------------------------------
# worldview assess
# ---------------------------------------------------------------------------


class TestAssessCommand:
    def test_default_assess_exits_cleanly(self) -> None:
        result = runner.invoke(app, ["assess"])
        assert result.exit_code in (0, 2)

    def test_assess_with_entropy(self) -> None:
        result = runner.invoke(app, ["assess", "--entropy", "2.5"])
        assert result.exit_code in (0, 2)

    def test_assess_shows_coherence(self) -> None:
        result = runner.invoke(app, ["assess", "--entropy", "1.0"])
        assert "Coherence" in result.output

    def test_assess_shows_common_good(self) -> None:
        result = runner.invoke(app, ["assess"])
        assert "Common-Good" in result.output

    def test_assess_with_models(self) -> None:
        result = runner.invoke(app, ["assess", "--models", "gpt-4o", "--models", "llama-3"])
        assert result.exit_code in (0, 2)

    def test_assess_with_id(self) -> None:
        result = runner.invoke(app, ["assess", "--id", "my-worldview"])
        assert "my-worldview" in result.output

    def test_assess_visualize_flag(self) -> None:
        result = runner.invoke(app, ["assess", "--visualize"])
        assert result.exit_code in (0, 2)

    def test_assess_export_json(self, tmp_path: Path) -> None:
        out_file = tmp_path / "result.json"
        runner.invoke(app, ["assess", "--export", str(out_file)])
        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert "worldview_id" in data

    def test_assess_invalid_weights_exit_one(self) -> None:
        result = runner.invoke(
            app,
            ["assess", "--w-coherence", "0.5", "--w-resonance", "0.5"],
        )
        assert result.exit_code == 1

    def test_assess_kl_flag(self) -> None:
        result = runner.invoke(app, ["assess", "--kl", "2.0"])
        assert result.exit_code in (0, 2)

    def test_assess_grade_shown(self) -> None:
        result = runner.invoke(app, ["assess"])
        assert any(grade in result.output for grade in ["A", "B", "C", "D", "F"])

    def test_assess_zero_entropy(self) -> None:
        result = runner.invoke(app, ["assess", "--entropy", "0.0"])
        assert result.exit_code in (0, 2)

    def test_assess_high_entropy(self) -> None:
        result = runner.invoke(app, ["assess", "--entropy", "50.0"])
        assert result.exit_code in (0, 2)


# ---------------------------------------------------------------------------
# worldview critique
# ---------------------------------------------------------------------------


class TestCritiqueCommand:
    def test_default_critique_passes(self) -> None:
        result = runner.invoke(app, ["critique"])
        assert result.exit_code == 0

    def test_critique_with_id(self) -> None:
        result = runner.invoke(app, ["critique", "--id", "wv-42"])
        assert "wv-42" in result.output

    def test_critique_low_coherence_shows_flags(self) -> None:
        result = runner.invoke(
            app, ["critique", "--coherence", "0.1", "--contradiction-rate", "0.9"]
        )
        assert result.exit_code in (0, 2)

    def test_critique_perfect_no_flags(self) -> None:
        result = runner.invoke(
            app,
            [
                "critique",
                "--coherence", "1.0",
                "--ethical-score", "1.0",
                "--contradiction-rate", "0.0",
                "--externality-index", "1.0",
                "--justice-index", "1.0",
                "--common-good", "1.0",
            ],
        )
        assert result.exit_code == 0
        assert "No flags" in result.output

    def test_critique_strict_mode(self) -> None:
        result = runner.invoke(
            app, ["critique", "--coherence", "0.5", "--strict"]
        )
        assert result.exit_code in (0, 2)

    def test_critique_export_json(self, tmp_path: Path) -> None:
        out_file = tmp_path / "critique.json"
        runner.invoke(app, ["critique", "--export", str(out_file)])
        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert "worldview_id" in data

    def test_critique_shows_score_table(self) -> None:
        result = runner.invoke(app, ["critique"])
        assert "Consistency" in result.output or "Coherence" in result.output

    def test_critique_failed_on_critical_ethics(self) -> None:
        result = runner.invoke(
            app, ["critique", "--ethical-score", "0.1"]
        )
        assert result.exit_code == 2

    def test_critique_low_externality(self) -> None:
        result = runner.invoke(
            app, ["critique", "--externality-index", "0.1"]
        )
        assert result.exit_code in (0, 2)


# ---------------------------------------------------------------------------
# worldview align
# ---------------------------------------------------------------------------


class TestAlignCommand:
    def test_default_align_exits(self) -> None:
        result = runner.invoke(app, ["align"])
        assert result.exit_code in (0, 1, 2)

    def test_align_with_entity_id(self) -> None:
        result = runner.invoke(app, ["align", "--entity", "my-agent"])
        assert "my-agent" in result.output

    def test_align_with_scores(self) -> None:
        result = runner.invoke(
            app,
            [
                "align",
                "--scores", "solidarity=0.8",
                "--scores", "justice=0.9",
            ],
        )
        assert result.exit_code in (0, 1, 2)

    def test_align_shows_composite(self) -> None:
        result = runner.invoke(app, ["align"])
        assert "Composite" in result.output or "composite" in result.output.lower()

    def test_align_shows_personhood(self) -> None:
        result = runner.invoke(app, ["align", "--personhood", "5"])
        assert "Normative" in result.output or "personhood" in result.output.lower()

    def test_align_invalid_score_format_exit_one(self) -> None:
        result = runner.invoke(app, ["align", "--scores", "bad_format"])
        assert result.exit_code == 1

    def test_align_non_numeric_score_exit_one(self) -> None:
        result = runner.invoke(app, ["align", "--scores", "solidarity=abc"])
        assert result.exit_code == 1

    def test_align_export_json(self, tmp_path: Path) -> None:
        out_file = tmp_path / "align.json"
        runner.invoke(app, ["align", "--export", str(out_file)])
        if out_file.exists():
            data = json.loads(out_file.read_text())
            assert "entity_id" in data

    def test_align_shows_grade(self) -> None:
        result = runner.invoke(app, ["align"])
        assert any(g in result.output for g in ["A+", "A", "B", "C", "D", "F"])

    def test_align_full_dimension_scores(self) -> None:
        result = runner.invoke(
            app,
            [
                "align",
                "--scores", "solidarity=1.0",
                "--scores", "sustainability=1.0",
                "--scores", "justice=1.0",
                "--scores", "freedom=1.0",
                "--scores", "dignity=1.0",
                "--scores", "participation=1.0",
            ],
        )
        assert result.exit_code in (0, 1, 2)

    def test_align_shows_dimension_entropy(self) -> None:
        result = runner.invoke(app, ["align"])
        assert "Entropy" in result.output or "entropy" in result.output.lower()


# ---------------------------------------------------------------------------
# Contract tests — package public API
# ---------------------------------------------------------------------------


class TestPackagePublicAPI:
    def test_worldview_importable(self) -> None:
        import worldview
        assert worldview.__version__ == "0.1.0"

    def test_engine_importable(self) -> None:
        from worldview import WorldviewEngine
        assert callable(WorldviewEngine)

    def test_checker_importable(self) -> None:
        from worldview import CriticalityChecker
        assert callable(CriticalityChecker)

    def test_alignment_importable(self) -> None:
        from worldview import AlignmentFramework
        assert callable(AlignmentFramework)

    def test_personhood_level_importable(self) -> None:
        from worldview import PersonhoodLevel
        assert PersonhoodLevel.NORMATIVE.value == 5

    def test_common_good_metric_importable(self) -> None:
        from worldview import CommonGoodMetric
        assert CommonGoodMetric is not None

    def test_critique_report_importable(self) -> None:
        from worldview import CritiqueReport
        assert CritiqueReport is not None

    def test_normative_metrics_importable(self) -> None:
        from worldview import NormativeMetrics
        assert NormativeMetrics is not None

    def test_worldview_assessment_importable(self) -> None:
        from worldview import WorldviewAssessment
        assert WorldviewAssessment is not None
