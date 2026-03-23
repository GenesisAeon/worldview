# API Reference

## worldview.core.worldview

### `NormativeWeights`

Pydantic model for the composite score weights.

```python
NormativeWeights(
    coherence: float = 0.25,   # α — weight of C(W)
    resonance: float = 0.20,   # β — weight of R(W)
    emergence: float = 0.20,   # γ — weight of E(W)
    poetics: float = 0.15,     # δ — weight of P(W)
    criticality: float = 0.20, # ε — weight of K(W)
)
```

All weights must sum to `1.0` (validated by Pydantic `@model_validator`).

---

### `NormativeMetrics`

Computed normative metric scores, all in $[0, 1]$ except `entropy`.

| Field        | Type  | Description                      |
|--------------|-------|----------------------------------|
| `coherence`  | float | $C(W)$ — internal coherence      |
| `resonance`  | float | $R(W)$ — normative resonance     |
| `emergence`  | float | $E(W)$ — structural emergence    |
| `poetics`    | float | $P(W)$ — aesthetic-poetic score  |
| `criticality`| float | $K(W)$ — philosophical criticality |
| `common_good`| float | $G(W)$ — composite alignment     |
| `entropy`    | float | $H(W)$ — raw Shannon entropy     |

---

### `PropositionalCluster`

A cluster of related propositions with a weight and internal consistency score.

```python
@dataclass
class PropositionalCluster:
    name: str
    propositions: list[str] = field(default_factory=list)
    weight: float = 1.0              # ∈ [0, 1]
    internal_consistency: float = 1.0 # ∈ [0, 1]
```

---

### `WorldviewAssessment`

Full assessment result.

| Property      | Type        | Description                          |
|---------------|-------------|--------------------------------------|
| `worldview_id`| str         | Unique identifier                    |
| `metrics`     | NormativeMetrics | All computed scores             |
| `weights`     | NormativeWeights | Weights used                    |
| `model_names` | list[str]   | Models evaluated                     |
| `critique_flags` | list[str] | CREP flag references               |
| `is_coherent` | bool (prop) | `coherence >= 0.6`                   |
| `is_aligned`  | bool (prop) | `common_good >= 0.5`                 |
| `grade`       | str (prop)  | A / B / C / D / F                    |

---

### `WorldviewEngine`

```python
engine = WorldviewEngine(
    weights: NormativeWeights | None = None,
    aesthetic_sensitivity: float = 1.0,   # λ in P(W)
    entropy_scale: float = 10.0,
)
```

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `compute_coherence(clusters, cross_contradiction_std)` | float | $C(W)$ |
| `compute_resonance(epistemic_frequencies, normative_waveform)` | float | $R(W)$ |
| `compute_emergence(cluster_entropies, global_entropy)` | float | $E(W)$ |
| `compute_poetics(kl_divergence)` | float | $P(W)$ |
| `compute_criticality(delta_resonance, delta_coherence, delta_emergence_time)` | float | $K(W)$ |
| `compute_common_good(metrics: dict)` | float | $G(W)$ |
| `assess(worldview_id, entropy, ...)` | WorldviewAssessment | Full assessment |

---

## worldview.core.critique

### `SeverityLevel`

```
INFO < WARNING < ERROR < CRITICAL
```

`ERROR` and `CRITICAL` are *blocking* — they cause `CritiqueReport.passed = False`.

---

### `CritiqueCategory`

| Value | Description |
|-------|-------------|
| `logical_consistency` | Propositional and cross-cluster contradictions |
| `ethical_implication` | Externalities, justice, deontological conflicts |
| `worldview_coherence` | Metaphysical and counterfactual coherence |
| `scope_validity` | Over-generalisation |
| `temporal_consistency` | Historical revisionism |
| `anthropocentric_bias` | Ignoring non-human agency |
| `epistemic_humility` | Overconfidence |
| `normative_alignment` | GNF compliance |

---

### `CritiqueFlag`

```python
CritiqueFlag(
    category: CritiqueCategory,
    severity: SeverityLevel,
    message: str,
    evidence: str = "",
    remediation: str = "",
    crep_ref: str = "",
)
```

`is_blocking: bool` — `True` for ERROR and CRITICAL.

---

### `CritiqueReport`

| Field | Type | Description |
|-------|------|-------------|
| `worldview_id` | str | Worldview identifier |
| `flags` | list[CritiqueFlag] | All flags raised |
| `philosophical_consistency_score` | float | Logical sub-score |
| `ethical_implication_score` | float | Ethical sub-score |
| `worldview_coherence_score` | float | Coherence sub-score |
| `overall_score` | float | Mean of three sub-scores |
| `passed` | bool | No blocking flags (non-strict) |
| `blocking_flags` | list (prop) | ERROR + CRITICAL flags |
| `has_ethical_concerns` | bool (prop) | `ethical_implication_score < 0.7` |

---

### `CriticalityChecker`

```python
checker = CriticalityChecker(
    rules: list[CheckerRule] | None = None,  # defaults to CREP_RULES
    strict_mode: bool = False,               # WARNING also blocks when True
)

report = checker.check(
    worldview_id: str,
    coherence: float = 1.0,
    ethical_score: float = 1.0,
    contradiction_rate: float = 0.0,
    externality_index: float = 1.0,
    justice_index: float = 1.0,
    counterfactual_stability: float = 1.0,
    common_good_score: float = 1.0,
    metadata: dict | None = None,
) -> CritiqueReport
```

---

## worldview.governance.alignment

### `PersonhoodLevel`

`IntEnum` with values 0–6. Key properties:

| Property | Description |
|----------|-------------|
| `label` | Human-readable string |
| `has_moral_agency` | True for levels ≥ 5 |
| `has_self_model` | True for levels ≥ 3 |

---

### `CommonGoodDimension`

```python
CommonGoodDimension(
    name: str,
    score: float,     # ∈ [0, 1]
    weight: float,    # > 0
    description: str = "",
)
```

---

### `CommonGoodMetric`

Auto-computed `composite_score` via weighted average.

| Property | Description |
|----------|-------------|
| `is_socially_beneficial` | `composite_score >= 0.65` |
| `grade` | A+ / A / B / C / D / F |

---

### `AlignmentFramework`

```python
framework = AlignmentFramework(
    dimension_weights: dict[str, float] | None = None,
)
```

| Method | Returns | Description |
|--------|---------|-------------|
| `evaluate(entity_id, scores, personhood_level)` | CommonGoodMetric | Compute G_norm |
| `assess_personhood(...)` | PersonhoodLevel | Heuristic level assignment |
| `dimension_entropy(metric)` | float | Shannon entropy over dimension scores |
| `gap_analysis(metric)` | dict[str, float] | Distance to ideal (1.0) per dimension |
| `personhood_weight(level)` | float | $\max(0.1, \log_2(\text{level}+2))$ |

---

## CLI Reference

```
worldview [--version] COMMAND [OPTIONS]

Commands:
  assess    Compute normative metrics for a worldview
  critique  Run CREP rules against a worldview
  align     Evaluate Common-Good alignment for an entity
  info      Display package and ecosystem information
```

### `worldview assess`

| Flag | Default | Description |
|------|---------|-------------|
| `--id TEXT` | worldview-1 | Worldview identifier |
| `--entropy FLOAT` | 1.0 | Raw Shannon entropy $H(W)$ |
| `--models TEXT` | — | Model names (repeatable) |
| `--kl FLOAT` | 0.0 | KL divergence from poetic attractor |
| `--w-coherence FLOAT` | 0.25 | Weight for $C(W)$ |
| `--w-resonance FLOAT` | 0.20 | Weight for $R(W)$ |
| `--w-emergence FLOAT` | 0.20 | Weight for $E(W)$ |
| `--w-poetics FLOAT` | 0.15 | Weight for $P(W)$ |
| `--w-criticality FLOAT` | 0.20 | Weight for $K(W)$ |
| `--visualize / -v` | False | Show metric progress bars |
| `--export PATH` | — | Export JSON to file |

Exit codes: `0` = aligned, `1` = bad arguments, `2` = not aligned.

### `worldview critique`

| Flag | Default | Description |
|------|---------|-------------|
| `--id TEXT` | worldview-1 | Worldview identifier |
| `--coherence FLOAT` | 1.0 | Coherence score |
| `--ethical-score FLOAT` | 1.0 | Overall ethical score |
| `--contradiction-rate FLOAT` | 0.0 | Proportion of contradictions |
| `--externality-index FLOAT` | 1.0 | Third-party coverage |
| `--justice-index FLOAT` | 1.0 | Distributive justice coverage |
| `--common-good FLOAT` | 1.0 | Common-good alignment |
| `--strict / --no-strict` | False | Strict mode (WARNING = FAIL) |
| `--export PATH` | — | Export JSON to file |

Exit codes: `0` = passed, `2` = failed.

### `worldview align`

| Flag | Default | Description |
|------|---------|-------------|
| `--entity TEXT` | entity-1 | Entity identifier |
| `--scores TEXT` | — | `key=value` pairs (repeatable) |
| `--personhood INT` | 2 | PersonhoodLevel (0–6) |
| `--export PATH` | — | Export JSON to file |

---

## References

1. CREP v0.3 — Critical Reflexive Evaluation Protocol. GenesisAeon (2024).
2. GNF v0.2 — GenesisAeon Normative Framework. GenesisAeon (2024).
3. Sigillin v0.1.0 — Symbolic integration layer. GenesisAeon (2024).
4. Shannon, C.E. (1948). A Mathematical Theory of Communication.
   *Bell System Technical Journal*, 27(3), 379–423.
5. Kullback, S., & Leibler, R.A. (1951). On Information and Sufficiency.
   *Annals of Mathematical Statistics*, 22(1), 79–86.
