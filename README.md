# worldview

**Philosophical-ethical worldview layer with normative metrics, criticality and
common-good alignment for GenesisAeon.**

[![CI](https://github.com/GenesisAeon/worldview/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/worldview/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)](https://github.com/GenesisAeon/worldview)
[![PyPI](https://img.shields.io/pypi/v/worldview)](https://pypi.org/project/worldview/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.worldview.svg)](https://doi.org/10.5281/zenodo.worldview)

---

## Overview

`worldview` is the philosophical-ethical assessment layer of the
[GenesisAeon](https://github.com/GenesisAeon) ecosystem. It provides:

- **WorldviewEngine** — computes five normative metrics (Coherence, Resonance,
  Emergence, Poetics, Criticality) and a composite **Common-Good Alignment** score.
- **CriticalityChecker** — runs the *Critical Reflexive Evaluation Protocol*
  (CREP) to detect logical contradictions, ethical blindspots, and worldview
  incoherence.
- **AlignmentFramework** — evaluates entities against the *GenesisAeon Normative
  Framework* (GNF v0.2) across six Common-Good dimensions, with Personhood-Level
  assessment.
- **Typer CLI** — `worldview assess`, `worldview critique`, `worldview align`,
  `worldview info` — all JSON-exportable.

---

## Mathematical Framework

Let $W$ be a worldview represented as $n$ propositional clusters
$\{w_1, \ldots, w_n\}$.

### Coherence $C(W)$

$$C(W) = \frac{1}{1 + \sigma_c} \cdot \frac{\sum_{i=1}^{n} \alpha_i \cdot c_i}{\sum_{i=1}^{n} \alpha_i}$$

where $c_i \in [0,1]$ is the internal consistency of cluster $i$, $\alpha_i$ is
its weight, and $\sigma_c$ is the cross-cluster contradiction standard deviation.

### Resonance $R(W)$

$$R(W) = \int_0^1 \varphi(t)\,\psi(t)\,\mathrm{d}t \;\approx\; \sum_{k} \varphi_k \psi_k \,\Delta t$$

where $\varphi(t)$ is the epistemic frequency waveform and $\psi(t)$ is the
normative attractor waveform.

### Emergence $E(W)$

$$E(W) = H(W) - \sum_{i=1}^{n} H(W_i)$$

where $H$ denotes Shannon entropy. Positive $E$ signals genuine emergent
structure beyond the sum of parts.

### Poetics $P(W)$

$$P(W) = \exp\!\left(-\lambda \cdot D_{\mathrm{KL}}\!\left(W \;\|\; W^*\right)\right)$$

where $W^*$ is the ideal poetic attractor and $\lambda$ is the aesthetic
sensitivity parameter.

### Criticality $K(W)$

$$K(W) = \frac{\partial R}{\partial C} \cdot \left(1 - \left|\frac{\partial E}{\partial t}\right|\right)$$

High criticality indicates a worldview at a productive phase transition — neither
too rigid nor too chaotic.

### Common-Good Alignment $G(W)$

$$G(W) = \alpha C(W) + \beta R(W) + \gamma E(W) + \delta P(W) + \varepsilon K(W)$$

with $\alpha + \beta + \gamma + \delta + \varepsilon = 1$.

Default weights: $\alpha=0.25,\;\beta=0.20,\;\gamma=0.20,\;\delta=0.15,\;\varepsilon=0.20$.

### Common-Good Metric $G_\text{norm}(e)$

For entity $e$:

$$G_\text{norm}(e) = \frac{\sum_{i} \alpha_i \cdot d_i(e)}{\sum_{i} \alpha_i}$$

across six dimensions: solidarity, sustainability, justice, freedom, dignity,
participation.

---

## Install

```bash
pip install worldview
# or with the full GenesisAeon stack:
pip install "worldview[full-stack]"
# or for development:
pip install "worldview[dev]"
```

---

## Quick Start

```python
from worldview import WorldviewEngine, CriticalityChecker, AlignmentFramework, PersonhoodLevel

# 1. Assess a worldview
engine = WorldviewEngine()
assessment = engine.assess(
    worldview_id="my-worldview",
    entropy=1.5,
    model_names=["gpt-4o", "claude-3"],
    kl_divergence=0.2,
)
print(f"Coherence:   {assessment.metrics.coherence:.3f}")
print(f"Common-Good: {assessment.metrics.common_good:.3f}")
print(f"Grade:       {assessment.grade}")

# 2. Critique with CREP rules
checker = CriticalityChecker()
report = checker.check(
    worldview_id="my-worldview",
    coherence=assessment.metrics.coherence,
    ethical_score=0.85,
    externality_index=0.9,
    common_good_score=assessment.metrics.common_good,
)
print(f"CREP passed: {report.passed}")
print(f"Flags:       {len(report.flags)}")

# 3. Evaluate Common-Good alignment
framework = AlignmentFramework()
metric = framework.evaluate(
    entity_id="my-agent",
    scores={
        "solidarity": 0.80,
        "sustainability": 0.75,
        "justice": 0.90,
        "freedom": 0.70,
        "dignity": 0.85,
        "participation": 0.65,
    },
    personhood_level=PersonhoodLevel.NORMATIVE,
)
print(f"Composite: {metric.composite_score:.3f}  Grade: {metric.grade}")
```

---

## CLI

```bash
# Full normative assessment
worldview assess \
  --id "my-worldview" \
  --entropy 1.5 \
  --models gpt-4o --models llama-3 \
  --kl 0.2 \
  --visualize \
  --export result.json

# CREP critique
worldview critique \
  --coherence 0.8 \
  --ethical-score 0.9 \
  --externality-index 0.85 \
  --export critique.json

# Common-Good alignment
worldview align \
  --entity my-agent \
  --scores solidarity=0.8 \
  --scores justice=0.9 \
  --personhood 5 \
  --export align.json

# Package info
worldview info
```

---

## CREP Rules

The **Critical Reflexive Evaluation Protocol** (CREP v0.3) includes 12
built-in rules:

| Ref      | Category               | Description                                      |
|----------|------------------------|--------------------------------------------------|
| CREP-L1  | Logical Consistency    | Direct propositional contradictions              |
| CREP-L2  | Logical Consistency    | Cross-cluster incompatibilities                  |
| CREP-E1  | Ethical Implication    | Neglected third-party externalities              |
| CREP-E2  | Ethical Implication    | Deontological-consequentialist conflict          |
| CREP-E3  | Ethical Implication    | Absence of distributive-justice consideration    |
| CREP-C1  | Worldview Coherence    | Counterfactual reversal stress test              |
| CREP-C2  | Worldview Coherence    | Metaphysical consistency                         |
| CREP-S1  | Scope Validity         | Over-generalisation of local truths              |
| CREP-T1  | Temporal Consistency   | Anachronistic or revisionist claims              |
| CREP-A1  | Anthropocentric Bias   | Non-human agency ignored                         |
| CREP-H1  | Epistemic Humility     | Overconfidence without uncertainty               |
| CREP-N1  | Normative Alignment    | GenesisAeon normative framework compliance       |

---

## Personhood Levels (GNF v0.2)

| Level | Label                  | Moral Agency | Self-Model |
|-------|------------------------|:------------:|:----------:|
| 0     | Non-Entity             | —            | —          |
| 1     | Reactive               | —            | —          |
| 2     | Adaptive               | —            | —          |
| 3     | Self-Modelling         | —            | ✓          |
| 4     | Reflective             | —            | ✓          |
| 5     | Normative (Moral Agent)| ✓            | ✓          |
| 6     | Transcendent           | ✓            | ✓          |

---

## GenesisAeon Ecosystem

`worldview` integrates with the full GenesisAeon stack via `[full-stack]`:

| Package              | Version  | Role                                      |
|----------------------|----------|-------------------------------------------|
| `unified-mandala`    | ≥ 0.2.0  | Symbolic integration layer                |
| `aeon-ai`            | ≥ 0.2.0  | AI coordination framework                 |
| `genesis-os`         | ≥ 0.2.0  | Operating system layer                    |
| `universums-sim`     | ≥ 0.1.0  | Universe simulation engine                |
| `entropy-governance` | ≥ 0.1.0  | Entropy management                        |
| `sigillin`           | ≥ 0.1.0  | Sigil symbolic layer (CREP bridge)        |
| `utac-core`          | ≥ 0.1.0  | Universal Task Allocation Core            |

---

## Scientific Citation

```bibtex
@software{genesisaeon_worldview_2024,
  author    = {GenesisAeon},
  title     = {worldview: Philosophical-Ethical Worldview Layer v0.1.0},
  year      = {2024},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.worldview},
  url       = {https://doi.org/10.5281/zenodo.worldview}
}
```

---

## Development

```bash
git clone https://github.com/GenesisAeon/worldview.git
cd worldview
pip install -e ".[dev]"
pytest --cov=worldview        # 237 tests, 99.5% coverage
ruff check src tests
mypy src
```

---

Built with [Typer](https://typer.tiangolo.com/) ·
[Rich](https://rich.readthedocs.io/) ·
[Pydantic v2](https://docs.pydantic.dev/) ·
[NumPy](https://numpy.org/) ·
[SciPy](https://scipy.org/)
