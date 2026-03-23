# worldview

**Philosophical-ethical worldview layer with normative metrics, criticality and
common-good alignment for GenesisAeon.**

## What is worldview?

`worldview` provides a rigorous mathematical and philosophical framework for
assessing, critiquing, and aligning world-models in the context of AI systems,
ethical reasoning, and collective intelligence.

It is the normative layer of the [GenesisAeon](https://github.com/GenesisAeon)
ecosystem and integrates tightly with **Sigillin** (symbolic layer) and the
**CREP** (Critical Reflexive Evaluation Protocol).

## Core Components

| Component | Module | Purpose |
|-----------|--------|---------|
| **WorldviewEngine** | `worldview.core.worldview` | Normative metric computation |
| **CriticalityChecker** | `worldview.core.critique` | CREP rule evaluation |
| **AlignmentFramework** | `worldview.governance.alignment` | Common-Good assessment |
| **CLI** | `worldview.cli.main` | `worldview assess / critique / align` |

## Quick Navigation

- [API Reference](reference.md) — full class and method documentation
- [GitHub Repository](https://github.com/GenesisAeon/worldview)
- [PyPI Package](https://pypi.org/project/worldview/)
- [Zenodo DOI](https://doi.org/10.5281/zenodo.worldview)

## Mathematical Foundation

$$G(W) = \alpha C(W) + \beta R(W) + \gamma E(W) + \delta P(W) + \varepsilon K(W)$$

where:

- $C(W)$ — Coherence: internal logical consistency
- $R(W)$ — Resonance: epistemic-normative alignment
- $E(W)$ — Emergence: entropy surplus $H(W) - \sum_i H(W_i)$
- $P(W)$ — Poetics: $\exp(-\lambda D_{KL}(W \| W^*))$
- $K(W)$ — Criticality: $(\partial R / \partial C)(1 - |\partial E / \partial t|)$

See [Reference](reference.md) for the full derivation.
