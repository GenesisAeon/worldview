# Contributing

Thanks for your interest in contributing to `worldview`, part of the
GenesisAeon ecosystem!

## Getting started

1. Fork and clone the repository.
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
   (or `.venv\Scripts\activate` on Windows).
3. Install in editable mode with dev dependencies: `pip install -e ".[dev]"`.
4. Run the test suite: `pytest --cov=worldview`.

## Code style

- Format and lint with `ruff check src tests`.
- Type-check with `mypy src`.
- Keep functions documented with docstrings.

## Pull requests

- One logical change per PR.
- Add or update tests for any behavioral change.
- Update `CHANGELOG.md` under an `## [Unreleased]` section.
- Fill out the PR template (`.github/PULL_REQUEST_TEMPLATE.md`).

## Reporting issues

Please use the issue templates in `.github/ISSUE_TEMPLATE/` — they help us
triage bug reports vs. feature requests quickly.

## Licensing of contributions

By contributing code, you agree it will be licensed under
GPL-3.0-or-later (see `LICENSE`). By contributing documentation
(README, `docs/`), you agree it will be licensed under CC BY 4.0 (see
`LICENSE-DOCS.md`).

## Scientific claims

If your contribution touches the CREP rules, normative metrics, or
Personhood-Level framework, please:
- Cite the source (paper, dataset, or prior GenesisAeon Zenodo record).
- Clearly mark speculative vs. validated claims.
