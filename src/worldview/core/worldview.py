"""WorldviewEngine — normative metrics for philosophical world-model assessment.

Implements the core mathematical framework for evaluating world-models across
five primary dimensions: Coherence, Resonance, Emergence, Poetics, Criticality,
and the composite Common-Good Alignment metric.

Mathematical Framework
----------------------
Let W be a worldview represented as a set of n propositional clusters {w₁,...,wₙ}.

Coherence:
    C(W) = (1/n) · Σᵢ wᵢ · cᵢ / (1 + σ_c)

where cᵢ is the internal consistency score of cluster i and σ_c is the
cross-cluster contradiction standard deviation.

Resonance:
    R(W) = ∫₀¹ φ(t) · ψ(t) dt  ≈  Σₖ φₖ · ψₖ · Δt

where φ(t) is the epistemic frequency and ψ(t) is the normative waveform.

Emergence:
    E(W) = H(W) - Σᵢ H(Wᵢ)

where H denotes Shannon entropy; positive E signals genuine emergent structure.

Criticality:
    K(W) = (∂R/∂C) · (1 - |∂E/∂t|)

Poetics:
    P(W) = exp(-λ · D_KL(W‖W*))

where W* is the ideal poetic attractor and λ is the aesthetic sensitivity.

Common-Good Alignment:
    G(W) = α·C(W) + β·R(W) + γ·E(W) + δ·P(W) + ε·K(W)
    with α+β+γ+δ+ε = 1
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from pydantic import BaseModel, Field, model_validator


class NormativeWeights(BaseModel):
    """Relative weights for the composite Common-Good Alignment metric.

    All weights must sum to 1.0.
    """

    coherence: float = Field(default=0.25, ge=0.0, le=1.0)
    resonance: float = Field(default=0.20, ge=0.0, le=1.0)
    emergence: float = Field(default=0.20, ge=0.0, le=1.0)
    poetics: float = Field(default=0.15, ge=0.0, le=1.0)
    criticality: float = Field(default=0.20, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> NormativeWeights:
        total = self.coherence + self.resonance + self.emergence + self.poetics + self.criticality
        if not math.isclose(total, 1.0, abs_tol=1e-6):
            msg = f"Weights must sum to 1.0, got {total:.6f}"
            raise ValueError(msg)
        return self


class NormativeMetrics(BaseModel):
    """Container for all computed normative metric scores.

    All scores are normalised to [0, 1].
    """

    coherence: float = Field(ge=0.0, le=1.0, description="Internal logical coherence C(W)")
    resonance: float = Field(ge=0.0, le=1.0, description="Normative resonance R(W)")
    emergence: float = Field(ge=0.0, le=1.0, description="Structural emergence E(W)")
    poetics: float = Field(ge=0.0, le=1.0, description="Aesthetic-poetic score P(W)")
    criticality: float = Field(ge=0.0, le=1.0, description="Philosophical criticality K(W)")
    common_good: float = Field(ge=0.0, le=1.0, description="Composite Common-Good G(W)")
    entropy: float = Field(ge=0.0, description="Shannon entropy of the worldview H(W)")


@dataclass
class PropositionalCluster:
    """A cluster of related propositions within a worldview.

    Attributes
    ----------
    name:
        Human-readable label for the cluster.
    propositions:
        List of propositional strings.
    weight:
        Relative importance weight in [0, 1].
    internal_consistency:
        Pre-computed internal consistency score in [0, 1].
    """

    name: str
    propositions: list[str] = field(default_factory=list)
    weight: float = 1.0
    internal_consistency: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.weight <= 1.0:
            msg = f"weight must be in [0, 1], got {self.weight}"
            raise ValueError(msg)
        if not 0.0 <= self.internal_consistency <= 1.0:
            msg = f"internal_consistency must be in [0, 1], got {self.internal_consistency}"
            raise ValueError(msg)


class WorldviewAssessment(BaseModel):
    """Full assessment result for a worldview.

    Attributes
    ----------
    worldview_id:
        Unique identifier string.
    metrics:
        Computed normative metrics.
    weights:
        Weights used for the composite score.
    model_names:
        Optional list of model names evaluated.
    critique_flags:
        List of critique flags raised during assessment.
    metadata:
        Arbitrary additional metadata.
    """

    worldview_id: str
    metrics: NormativeMetrics
    weights: NormativeWeights
    model_names: list[str] = Field(default_factory=list)
    critique_flags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_coherent(self) -> bool:
        """Return True when coherence exceeds 0.6."""
        return self.metrics.coherence >= 0.6

    @property
    def is_aligned(self) -> bool:
        """Return True when common-good alignment exceeds 0.5."""
        return self.metrics.common_good >= 0.5

    @property
    def grade(self) -> str:
        """Return letter grade based on common-good score."""
        score = self.metrics.common_good
        if score >= 0.9:
            return "A"
        if score >= 0.75:
            return "B"
        if score >= 0.60:
            return "C"
        if score >= 0.45:
            return "D"
        return "F"


class WorldviewEngine:
    """Engine for computing normative metrics on philosophical world-models.

    Parameters
    ----------
    weights:
        Custom normative weights; defaults to equal-ish distribution.
    aesthetic_sensitivity:
        λ parameter for the poetics score (KL-divergence sensitivity).
    entropy_scale:
        Normalisation factor applied to raw Shannon entropy.

    Examples
    --------
    >>> engine = WorldviewEngine()
    >>> assessment = engine.assess(worldview_id="demo", entropy=0.5)
    >>> assessment.metrics.common_good >= 0.0
    True
    """

    def __init__(
        self,
        weights: NormativeWeights | None = None,
        aesthetic_sensitivity: float = 1.0,
        entropy_scale: float = 10.0,
    ) -> None:
        self.weights = weights or NormativeWeights()
        self.aesthetic_sensitivity = aesthetic_sensitivity
        self.entropy_scale = entropy_scale

    def compute_coherence(
        self,
        clusters: list[PropositionalCluster] | None = None,
        cross_contradiction_std: float = 0.0,
    ) -> float:
        """Compute C(W) from propositional clusters.

        Parameters
        ----------
        clusters:
            List of propositional clusters; empty list yields 1.0.
        cross_contradiction_std:
            σ_c — standard deviation of cross-cluster contradictions.

        Returns
        -------
        float
            Coherence score in [0, 1].
        """
        if not clusters:
            return 1.0
        weighted_sum = sum(c.weight * c.internal_consistency for c in clusters)
        total_weight = sum(c.weight for c in clusters)
        raw = weighted_sum / total_weight if total_weight > 0 else 1.0
        return float(raw / (1.0 + cross_contradiction_std))

    def compute_resonance(
        self,
        epistemic_frequencies: list[float] | None = None,
        normative_waveform: list[float] | None = None,
    ) -> float:
        """Compute R(W) via discrete inner product approximation.

        Parameters
        ----------
        epistemic_frequencies:
            φ values sampled at uniform time steps.
        normative_waveform:
            ψ values sampled at the same time steps.

        Returns
        -------
        float
            Resonance score clipped to [0, 1].
        """
        if not epistemic_frequencies or not normative_waveform:
            return 0.5
        phi = np.array(epistemic_frequencies, dtype=float)
        psi = np.array(normative_waveform, dtype=float)
        min_len = min(len(phi), len(psi))
        dt = 1.0 / min_len
        raw = float(np.dot(phi[:min_len], psi[:min_len]) * dt)
        return float(np.clip(raw, 0.0, 1.0))

    def compute_emergence(
        self,
        cluster_entropies: list[float] | None = None,
        global_entropy: float | None = None,
    ) -> float:
        """Compute E(W) = H(W) - Σ H(Wᵢ), normalised to [0, 1].

        Parameters
        ----------
        cluster_entropies:
            Shannon entropies of individual clusters.
        global_entropy:
            H(W) — entropy of the full worldview.

        Returns
        -------
        float
            Normalised emergence score.
        """
        if cluster_entropies is None or global_entropy is None:
            return 0.5
        cluster_sum = sum(cluster_entropies)
        raw_emergence = global_entropy - cluster_sum
        if cluster_sum == 0:
            return 0.5
        normalised = (raw_emergence + cluster_sum) / (2.0 * max(cluster_sum, 1e-9))
        return float(np.clip(normalised, 0.0, 1.0))

    def compute_poetics(
        self,
        kl_divergence: float = 0.0,
    ) -> float:
        """Compute P(W) = exp(-λ · D_KL(W‖W*)).

        Parameters
        ----------
        kl_divergence:
            KL divergence from the ideal poetic attractor W*.

        Returns
        -------
        float
            Poetics score in (0, 1].
        """
        return float(math.exp(-self.aesthetic_sensitivity * max(0.0, kl_divergence)))

    def compute_criticality(
        self,
        delta_resonance: float = 0.0,
        delta_coherence: float = 1.0,
        delta_emergence_time: float = 0.0,
    ) -> float:
        """Compute K(W) = (∂R/∂C) · (1 - |∂E/∂t|).

        Parameters
        ----------
        delta_resonance:
            Incremental change in resonance ∂R.
        delta_coherence:
            Incremental change in coherence ∂C (must not be zero).
        delta_emergence_time:
            Rate of change of emergence over time ∂E/∂t.

        Returns
        -------
        float
            Criticality score clipped to [0, 1].
        """
        if delta_coherence == 0.0:
            delta_coherence = 1e-9
        sensitivity = delta_resonance / delta_coherence
        stability = 1.0 - abs(delta_emergence_time)
        raw = sensitivity * stability
        return float(np.clip(raw, 0.0, 1.0))

    def compute_common_good(self, metrics: dict[str, float]) -> float:
        """Compute G(W) as the weighted sum of all sub-metrics.

        Parameters
        ----------
        metrics:
            Dictionary with keys: coherence, resonance, emergence, poetics, criticality.

        Returns
        -------
        float
            Composite alignment score in [0, 1].
        """
        g = (
            self.weights.coherence * metrics.get("coherence", 0.0)
            + self.weights.resonance * metrics.get("resonance", 0.0)
            + self.weights.emergence * metrics.get("emergence", 0.0)
            + self.weights.poetics * metrics.get("poetics", 0.0)
            + self.weights.criticality * metrics.get("criticality", 0.0)
        )
        return float(np.clip(g, 0.0, 1.0))

    def _entropy_from_float(self, entropy_input: float) -> float:
        """Normalise a raw entropy value to [0, 1] using self.entropy_scale."""
        return float(np.clip(entropy_input / self.entropy_scale, 0.0, 1.0))

    def assess(
        self,
        worldview_id: str,
        entropy: float = 1.0,
        clusters: list[PropositionalCluster] | None = None,
        model_names: list[str] | None = None,
        epistemic_frequencies: list[float] | None = None,
        normative_waveform: list[float] | None = None,
        cluster_entropies: list[float] | None = None,
        kl_divergence: float = 0.0,
        cross_contradiction_std: float = 0.0,
        delta_resonance: float = 0.5,
        delta_coherence: float = 1.0,
        delta_emergence_time: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> WorldviewAssessment:
        """Perform a full normative assessment of a worldview.

        Parameters
        ----------
        worldview_id:
            Unique identifier string for the worldview.
        entropy:
            Raw Shannon entropy of the world-model (unnormalised).
        clusters:
            Propositional clusters; optional.
        model_names:
            Names of AI/philosophical models being evaluated.
        epistemic_frequencies:
            φ values for resonance computation.
        normative_waveform:
            ψ values for resonance computation.
        cluster_entropies:
            Entropies of individual clusters.
        kl_divergence:
            KL divergence for poetics computation.
        cross_contradiction_std:
            σ_c for coherence computation.
        delta_resonance:
            ∂R for criticality computation.
        delta_coherence:
            ∂C for criticality computation.
        delta_emergence_time:
            ∂E/∂t for criticality computation.
        metadata:
            Arbitrary additional metadata.

        Returns
        -------
        WorldviewAssessment
            Complete assessment with all normative metrics.
        """
        normalised_entropy = self._entropy_from_float(entropy)
        global_entropy = normalised_entropy * self.entropy_scale

        coherence = self.compute_coherence(clusters, cross_contradiction_std)
        resonance = self.compute_resonance(epistemic_frequencies, normative_waveform)
        emergence = self.compute_emergence(cluster_entropies, global_entropy)
        poetics = self.compute_poetics(kl_divergence)
        criticality = self.compute_criticality(
            delta_resonance, delta_coherence, delta_emergence_time
        )

        metric_dict = {
            "coherence": coherence,
            "resonance": resonance,
            "emergence": emergence,
            "poetics": poetics,
            "criticality": criticality,
        }
        common_good = self.compute_common_good(metric_dict)

        metrics = NormativeMetrics(
            coherence=coherence,
            resonance=resonance,
            emergence=emergence,
            poetics=poetics,
            criticality=criticality,
            common_good=common_good,
            entropy=entropy,
        )

        return WorldviewAssessment(
            worldview_id=worldview_id,
            metrics=metrics,
            weights=self.weights,
            model_names=model_names or [],
            metadata=metadata or {},
        )
