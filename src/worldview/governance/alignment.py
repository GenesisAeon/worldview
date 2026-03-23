"""Normative governance — Personhood levels and Common-Good metric.

Implements the GenesisAeon Normative Framework (GNF v0.2) for grading
entities along a Personhood spectrum and computing composite Gemeinwohl
(Common-Good) alignment scores.

Personhood Levels
-----------------
Level 0 — Non-entity:       No recognisable agency or sentience.
Level 1 — Reactive:         Stimulus-response, no reflective capacity.
Level 2 — Adaptive:         Learning, goal-directed, no self-model.
Level 3 — Self-modelling:   Has internal self-model; proto-consciousness.
Level 4 — Reflective:       Full self-awareness, narrative identity.
Level 5 — Normative:        Moral agency; capable of obligation.
Level 6 — Transcendent:     Post-individual; operates at systemic/collective level.

Common-Good Metric
------------------
    G_norm(e) = Σᵢ αᵢ · dᵢ(e) / Σᵢ αᵢ

where dᵢ(e) is the contribution of entity e on dimension i and αᵢ is the
dimension weight.

Dimensions: solidarity, sustainability, justice, freedom, dignity, participation.
"""

from __future__ import annotations

import math
from enum import IntEnum
from typing import Any

import numpy as np
from pydantic import BaseModel, Field, model_validator


class PersonhoodLevel(IntEnum):
    """Ordinal scale of personhood / moral agency.

    See module docstring for full description of each level.
    """

    NON_ENTITY = 0
    REACTIVE = 1
    ADAPTIVE = 2
    SELF_MODELLING = 3
    REFLECTIVE = 4
    NORMATIVE = 5
    TRANSCENDENT = 6

    @property
    def label(self) -> str:
        """Return a human-readable label."""
        labels = {
            0: "Non-Entity",
            1: "Reactive",
            2: "Adaptive",
            3: "Self-Modelling",
            4: "Reflective",
            5: "Normative (Moral Agent)",
            6: "Transcendent",
        }
        return labels[self.value]

    @property
    def has_moral_agency(self) -> bool:
        """Return True for levels 5 and 6."""
        return self.value >= PersonhoodLevel.NORMATIVE

    @property
    def has_self_model(self) -> bool:
        """Return True for levels 3 and above."""
        return self.value >= PersonhoodLevel.SELF_MODELLING


class CommonGoodDimension(BaseModel):
    """A single dimension of the Common-Good metric.

    Attributes
    ----------
    name:
        Dimension name (e.g. "solidarity").
    score:
        Contribution score in [0, 1].
    weight:
        Relative importance weight (unnormalised).
    description:
        Optional human-readable description.
    """

    name: str
    score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(gt=0.0, default=1.0)
    description: str = ""


class CommonGoodMetric(BaseModel):
    """Composite Common-Good metric for an entity or worldview.

    Attributes
    ----------
    entity_id:
        Identifier of the entity being scored.
    dimensions:
        List of scored Common-Good dimensions.
    composite_score:
        Normalised composite in [0, 1]; computed automatically.
    personhood_level:
        Assessed personhood level.
    """

    entity_id: str
    dimensions: list[CommonGoodDimension] = Field(default_factory=list)
    composite_score: float = Field(ge=0.0, le=1.0, default=0.0)
    personhood_level: PersonhoodLevel = PersonhoodLevel.ADAPTIVE

    @model_validator(mode="after")
    def recompute_composite(self) -> CommonGoodMetric:
        if self.dimensions:
            total_weight = sum(d.weight for d in self.dimensions)
            weighted_sum = sum(d.score * d.weight for d in self.dimensions)
            self.composite_score = float(
                np.clip(weighted_sum / total_weight, 0.0, 1.0)
            )
        return self

    @property
    def is_socially_beneficial(self) -> bool:
        """Return True when composite score exceeds 0.65."""
        return self.composite_score >= 0.65

    @property
    def grade(self) -> str:
        """Return letter grade for the composite score."""
        s = self.composite_score
        if s >= 0.90:
            return "A+"
        if s >= 0.80:
            return "A"
        if s >= 0.70:
            return "B"
        if s >= 0.60:
            return "C"
        if s >= 0.50:
            return "D"
        return "F"


DEFAULT_DIMENSIONS: list[dict[str, Any]] = [
    {
        "name": "solidarity",
        "weight": 1.5,
        "description": "Degree to which entity promotes mutual support and collective welfare.",
    },
    {
        "name": "sustainability",
        "weight": 1.5,
        "description": "Long-term ecological and social sustainability of entity's actions.",
    },
    {
        "name": "justice",
        "weight": 2.0,
        "description": "Contribution to fair distribution of benefits and burdens.",
    },
    {
        "name": "freedom",
        "weight": 1.0,
        "description": "Respect for and promotion of individual and collective freedoms.",
    },
    {
        "name": "dignity",
        "weight": 2.0,
        "description": "Affirmation of inherent worth and dignity of all persons.",
    },
    {
        "name": "participation",
        "weight": 1.0,
        "description": "Enablement of meaningful participatory governance.",
    },
]


class AlignmentFramework:
    """Evaluate entities and worldviews against the GenesisAeon Normative Framework.

    Parameters
    ----------
    dimension_weights:
        Optional override for the default dimension weights.
        Must match the names of DEFAULT_DIMENSIONS or a custom set.

    Examples
    --------
    >>> framework = AlignmentFramework()
    >>> metric = framework.evaluate(
    ...     entity_id="test-agent",
    ...     scores={"solidarity": 0.8, "sustainability": 0.7, "justice": 0.9,
    ...             "freedom": 0.6, "dignity": 0.85, "participation": 0.7},
    ...     personhood_level=PersonhoodLevel.NORMATIVE,
    ... )
    >>> metric.composite_score > 0.0
    True
    """

    def __init__(
        self,
        dimension_weights: dict[str, float] | None = None,
    ) -> None:
        self._dimension_configs = list(DEFAULT_DIMENSIONS)
        if dimension_weights:
            for cfg in self._dimension_configs:
                if cfg["name"] in dimension_weights:
                    cfg["weight"] = dimension_weights[cfg["name"]]

    def evaluate(
        self,
        entity_id: str,
        scores: dict[str, float],
        personhood_level: PersonhoodLevel = PersonhoodLevel.ADAPTIVE,
    ) -> CommonGoodMetric:
        """Compute the Common-Good metric for an entity.

        Parameters
        ----------
        entity_id:
            Unique identifier for the entity.
        scores:
            Dictionary mapping dimension names to scores in [0, 1].
            Missing dimensions default to 0.0.
        personhood_level:
            Assessed personhood level of the entity.

        Returns
        -------
        CommonGoodMetric
            Fully populated metric with composite score.
        """
        dimensions = []
        for cfg in self._dimension_configs:
            name = cfg["name"]
            dim = CommonGoodDimension(
                name=name,
                score=float(np.clip(scores.get(name, 0.0), 0.0, 1.0)),
                weight=float(cfg["weight"]),
                description=str(cfg.get("description", "")),
            )
            dimensions.append(dim)

        return CommonGoodMetric(
            entity_id=entity_id,
            dimensions=dimensions,
            personhood_level=personhood_level,
        )

    def assess_personhood(
        self,
        has_self_model: bool = False,
        has_moral_agency: bool = False,
        is_learning: bool = False,
        operates_collectively: bool = False,
    ) -> PersonhoodLevel:
        """Heuristically assign a PersonhoodLevel based on observable traits.

        Parameters
        ----------
        has_self_model:
            Whether the entity maintains an internal self-model.
        has_moral_agency:
            Whether the entity can be held morally responsible.
        is_learning:
            Whether the entity exhibits adaptive learning.
        operates_collectively:
            Whether the entity primarily operates at a supra-individual level.

        Returns
        -------
        PersonhoodLevel
            The assessed personhood level.
        """
        if operates_collectively and has_moral_agency:
            return PersonhoodLevel.TRANSCENDENT
        if has_moral_agency:
            return PersonhoodLevel.NORMATIVE
        if has_self_model:
            return PersonhoodLevel.SELF_MODELLING
        if is_learning:
            return PersonhoodLevel.ADAPTIVE
        return PersonhoodLevel.REACTIVE

    def dimension_entropy(self, metric: CommonGoodMetric) -> float:
        """Compute Shannon entropy across dimension scores.

        High entropy indicates evenly spread contributions;
        low entropy signals concentration in few dimensions.

        Parameters
        ----------
        metric:
            A fully populated CommonGoodMetric.

        Returns
        -------
        float
            Shannon entropy in nats.
        """
        scores = np.array([d.score for d in metric.dimensions], dtype=float)
        total = scores.sum()
        if total == 0.0:
            return 0.0
        probs = scores / total
        probs = probs[probs > 0]
        return float(-np.sum(probs * np.log(probs)))

    def gap_analysis(self, metric: CommonGoodMetric) -> dict[str, float]:
        """Identify gaps between actual and ideal (1.0) dimension scores.

        Parameters
        ----------
        metric:
            A fully populated CommonGoodMetric.

        Returns
        -------
        dict[str, float]
            Mapping of dimension name → gap (positive = below ideal).
        """
        return {d.name: round(1.0 - d.score, 4) for d in metric.dimensions}

    @staticmethod
    def personhood_weight(level: PersonhoodLevel) -> float:
        """Return a scalar weight for a given personhood level.

        Used when aggregating multi-agent worldview scores.

        Parameters
        ----------
        level:
            The PersonhoodLevel to weight.

        Returns
        -------
        float
            Weight in [0.1, 2.0].
        """
        return float(max(0.1, math.log2(level.value + 2)))
