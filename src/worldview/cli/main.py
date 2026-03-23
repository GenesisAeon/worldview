"""Worldview CLI — normative assessment from the command line.

Usage
-----
    worldview assess --entropy 0.5 --models gpt-4o llama-3 --visualize
    worldview critique --coherence 0.8 --ethical-score 0.9
    worldview align --entity my-agent --scores solidarity=0.8 justice=0.9
    worldview info
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from worldview import __version__
from worldview.core.critique import CriticalityChecker
from worldview.core.worldview import NormativeWeights, WorldviewEngine
from worldview.governance.alignment import AlignmentFramework, PersonhoodLevel

app = typer.Typer(
    name="worldview",
    help="Philosophical-ethical worldview assessment CLI (GenesisAeon v0.1.0).",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()
err_console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"worldview {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", "-V", callback=_version_callback, is_eager=True),
    ] = None,
) -> None:
    """Worldview — normative metrics for philosophical world-models."""


@app.command()
def assess(
    worldview_id: Annotated[
        str, typer.Option("--id", help="Worldview identifier.")
    ] = "worldview-1",
    entropy: Annotated[
        float, typer.Option("--entropy", "-e", help="Raw Shannon entropy H(W).", min=0.0)
    ] = 1.0,
    models: Annotated[
        list[str] | None, typer.Option("--models", "-m", help="Model names to evaluate.")
    ] = None,
    kl_divergence: Annotated[
        float, typer.Option("--kl", help="KL divergence from poetic attractor.", min=0.0)
    ] = 0.0,
    coherence_weight: Annotated[
        float, typer.Option("--w-coherence", help="Coherence weight.", min=0.0, max=1.0)
    ] = 0.25,
    resonance_weight: Annotated[
        float, typer.Option("--w-resonance", help="Resonance weight.", min=0.0, max=1.0)
    ] = 0.20,
    emergence_weight: Annotated[
        float, typer.Option("--w-emergence", help="Emergence weight.", min=0.0, max=1.0)
    ] = 0.20,
    poetics_weight: Annotated[
        float, typer.Option("--w-poetics", help="Poetics weight.", min=0.0, max=1.0)
    ] = 0.15,
    criticality_weight: Annotated[
        float, typer.Option("--w-criticality", help="Criticality weight.", min=0.0, max=1.0)
    ] = 0.20,
    visualize: Annotated[
        bool, typer.Option("--visualize", "-v", help="Render metric bars.")
    ] = False,
    export: Annotated[
        Path | None, typer.Option("--export", "-o", help="Export JSON result to file.")
    ] = None,
) -> None:
    """[bold]Assess[/bold] a worldview's normative metrics.

    Computes Coherence, Resonance, Emergence, Poetics, Criticality, and
    Common-Good Alignment scores.
    """
    total_weight = (
        coherence_weight + resonance_weight + emergence_weight + poetics_weight + criticality_weight
    )
    if abs(total_weight - 1.0) > 1e-4:
        err_console.print(
            f"[red]Error:[/red] weights must sum to 1.0, got {total_weight:.4f}. "
            "Adjust --w-* flags."
        )
        raise typer.Exit(code=1)

    weights = NormativeWeights(
        coherence=coherence_weight,
        resonance=resonance_weight,
        emergence=emergence_weight,
        poetics=poetics_weight,
        criticality=criticality_weight,
    )
    engine = WorldviewEngine(weights=weights)
    assessment = engine.assess(
        worldview_id=worldview_id,
        entropy=entropy,
        model_names=models or [],
        kl_divergence=kl_divergence,
    )

    console.print(
        Panel(
            f"[bold cyan]Worldview Assessment[/bold cyan]  id=[yellow]{worldview_id}[/yellow]",
            subtitle=f"Grade: [bold]{assessment.grade}[/bold]",
            box=box.ROUNDED,
        )
    )

    table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
    table.add_column("Metric", style="cyan", width=24)
    table.add_column("Score", justify="right", width=8)
    table.add_column("Bar", width=42) if visualize else None

    m = assessment.metrics
    rows = [
        ("Coherence C(W)", m.coherence),
        ("Resonance R(W)", m.resonance),
        ("Emergence E(W)", m.emergence),
        ("Poetics P(W)", m.poetics),
        ("Criticality K(W)", m.criticality),
        ("Common-Good G(W)", m.common_good),
    ]

    for name, score in rows:
        color = "green" if score >= 0.7 else "yellow" if score >= 0.4 else "red"
        score_str = f"[{color}]{score:.4f}[/{color}]"
        if visualize:
            bar_filled = int(score * 40)
            bar = f"[{color}]{'█' * bar_filled}{'░' * (40 - bar_filled)}[/{color}]"
            table.add_row(name, score_str, bar)
        else:
            table.add_row(name, score_str)

    console.print(table)

    if models:
        console.print(f"[dim]Models evaluated: {', '.join(models)}[/dim]")

    aligned = "[green]YES[/green]" if assessment.is_aligned else "[red]NO[/red]"
    coherent = "[green]YES[/green]" if assessment.is_coherent else "[red]NO[/red]"
    console.print(f"  Aligned:  {aligned}   Coherent: {coherent}")

    result = assessment.model_dump()
    if export:
        export.write_text(json.dumps(result, indent=2, default=str))
        console.print(f"\n[green]Result exported to:[/green] {export}")

    if not assessment.is_aligned:
        raise typer.Exit(code=2)


@app.command()
def critique(
    worldview_id: Annotated[str, typer.Option("--id")] = "worldview-1",
    coherence: Annotated[float, typer.Option("--coherence", min=0.0, max=1.0)] = 1.0,
    ethical_score: Annotated[float, typer.Option("--ethical-score", min=0.0, max=1.0)] = 1.0,
    contradiction_rate: Annotated[
        float, typer.Option("--contradiction-rate", min=0.0, max=1.0)
    ] = 0.0,
    externality_index: Annotated[
        float, typer.Option("--externality-index", min=0.0, max=1.0)
    ] = 1.0,
    justice_index: Annotated[float, typer.Option("--justice-index", min=0.0, max=1.0)] = 1.0,
    common_good_score: Annotated[float, typer.Option("--common-good", min=0.0, max=1.0)] = 1.0,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = False,
    export: Annotated[Path | None, typer.Option("--export", "-o")] = None,
) -> None:
    """[bold]Critique[/bold] a worldview using CREP rules.

    Checks philosophical consistency, ethical implications, and worldview coherence.
    """
    checker = CriticalityChecker(strict_mode=strict)
    report = checker.check(
        worldview_id=worldview_id,
        coherence=coherence,
        ethical_score=ethical_score,
        contradiction_rate=contradiction_rate,
        externality_index=externality_index,
        justice_index=justice_index,
        common_good_score=common_good_score,
    )

    status = "[green]PASSED[/green]" if report.passed else "[red]FAILED[/red]"
    console.print(
        Panel(
            "[bold cyan]CREP Critique Report[/bold cyan]  "
            f"id=[yellow]{worldview_id}[/yellow]  {status}",
            subtitle=f"Overall: {report.overall_score:.4f}",
            box=box.ROUNDED,
        )
    )

    if not report.flags:
        console.print("[green]No flags raised — worldview passes all CREP rules.[/green]")
    else:
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        table.add_column("Ref", width=10)
        table.add_column("Severity", width=10)
        table.add_column("Category", width=26)
        table.add_column("Message")

        for flag in report.flags:
            sev_color = {
                "critical": "bold red",
                "error": "red",
                "warning": "yellow",
                "info": "blue",
            }.get(flag.severity.value, "white")
            table.add_row(
                flag.crep_ref,
                f"[{sev_color}]{flag.severity.value.upper()}[/{sev_color}]",
                flag.category.value,
                flag.message,
            )
        console.print(table)

    score_table = Table(show_header=False, box=box.SIMPLE)
    score_table.add_column("Label", style="cyan")
    score_table.add_column("Score", justify="right")
    score_table.add_row(
        "Philosophical Consistency",
        f"{report.philosophical_consistency_score:.4f}",
    )
    score_table.add_row("Ethical Implication", f"{report.ethical_implication_score:.4f}")
    score_table.add_row("Worldview Coherence", f"{report.worldview_coherence_score:.4f}")
    console.print(score_table)

    if export:
        export.write_text(json.dumps(report.model_dump(), indent=2, default=str))
        console.print(f"\n[green]Report exported to:[/green] {export}")

    if not report.passed:
        raise typer.Exit(code=2)


@app.command()
def align(
    entity_id: Annotated[str, typer.Option("--entity", "-e")] = "entity-1",
    scores: Annotated[
        list[str] | None,
        typer.Option(
            "--scores",
            "-s",
            help="Dimension scores as key=value pairs, e.g. solidarity=0.8.",
        ),
    ] = None,
    personhood: Annotated[
        int,
        typer.Option(
            "--personhood",
            "-p",
            help="PersonhoodLevel integer (0-6).",
            min=0,
            max=6,
        ),
    ] = 2,
    export: Annotated[Path | None, typer.Option("--export", "-o")] = None,
) -> None:
    """[bold]Align[/bold] an entity against the Common-Good metric.

    Evaluates solidarity, sustainability, justice, freedom, dignity, participation.
    """
    parsed_scores: dict[str, float] = {}
    if scores:
        for item in scores:
            if "=" not in item:
                err_console.print(
                    f"[red]Error:[/red] invalid score format '{item}'. Use key=value."
                )
                raise typer.Exit(code=1)
            key, _, val = item.partition("=")
            try:
                parsed_scores[key.strip()] = float(val.strip())
            except ValueError as exc:
                err_console.print(f"[red]Error:[/red] cannot parse '{val}' as float.")
                raise typer.Exit(code=1) from exc

    level = PersonhoodLevel(personhood)
    framework = AlignmentFramework()
    metric = framework.evaluate(
        entity_id=entity_id,
        scores=parsed_scores,
        personhood_level=level,
    )

    grade_color = {"A+": "bright_green", "A": "green", "B": "cyan", "C": "yellow"}.get(
        metric.grade, "red"
    )
    console.print(
        Panel(
            f"[bold cyan]Common-Good Alignment[/bold cyan]  entity=[yellow]{entity_id}[/yellow]",
            subtitle=(
                f"Grade: [bold {grade_color}]{metric.grade}[/bold {grade_color}]  "
                f"Personhood: [magenta]{level.label}[/magenta]"
            ),
            box=box.ROUNDED,
        )
    )

    table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
    table.add_column("Dimension", style="cyan", width=20)
    table.add_column("Score", justify="right", width=8)
    table.add_column("Weight", justify="right", width=8)
    table.add_column("Gap", justify="right", width=8)

    gaps = framework.gap_analysis(metric)
    for dim in metric.dimensions:
        gap = gaps[dim.name]
        gap_color = "green" if gap < 0.2 else "yellow" if gap < 0.5 else "red"
        table.add_row(
            dim.name,
            f"{dim.score:.3f}",
            f"{dim.weight:.1f}",
            f"[{gap_color}]{gap:.3f}[/{gap_color}]",
        )

    console.print(table)
    console.print(f"  Composite: [bold]{metric.composite_score:.4f}[/bold]")
    console.print(
        f"  Socially Beneficial: "
        f"{'[green]YES[/green]' if metric.is_socially_beneficial else '[red]NO[/red]'}"
    )

    entropy = framework.dimension_entropy(metric)
    console.print(f"  Dimension Entropy: {entropy:.4f} nats")

    if export:
        export.write_text(json.dumps(metric.model_dump(), indent=2, default=str))
        console.print(f"\n[green]Result exported to:[/green] {export}")


@app.command()
def info() -> None:
    """Display package information and GenesisAeon ecosystem links."""
    console.print(
        Panel(
            "[bold cyan]worldview[/bold cyan] — Philosophical-Ethical Worldview Layer",
            subtitle=f"v{__version__} · MIT License · GenesisAeon",
            box=box.DOUBLE_EDGE,
        )
    )
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Key", style="cyan", width=24)
    table.add_column("Value")
    table.add_row("Version", __version__)
    table.add_row("Author", "GenesisAeon")
    table.add_row("Repository", "https://github.com/GenesisAeon/worldview")
    table.add_row("Documentation", "https://genesisaeon.github.io/worldview")
    table.add_row("Zenodo DOI", "https://doi.org/10.5281/zenodo.worldview")
    table.add_row("CREP Reference", "Critical Reflexive Evaluation Protocol v0.3")
    table.add_row("Sigillin Layer", "sigillin >= 0.1.0")
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}+")
    console.print(table)


if __name__ == "__main__":
    app()
