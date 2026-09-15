# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.1] - 2026-09-15

### Fixed (test suite only, no behavior change)
- Removed `tests/test_preset.py`, `tests/test_validator.py`: unmodified
  copies of `diamond-setup`'s own test suite, exercising only
  `diamond_setup` internals, never `worldview` code.
- `tests/test_cli.py` had been mistakenly deleted in an earlier,
  uncommitted pass as suspected diamond-setup contamination — a search
  for `cli.py` missed it because this package's own CLI lives at
  `src/worldview/cli/main.py`, not `cli.py` directly. It is a complete,
  legitimate test suite for `worldview.cli.main.app`; restored (this
  also fixed an apparent "coverage below 99%" symptom, which was
  actually caused by the mistaken deletion, not a pre-existing gap).
- `TestVersionFlag::test_version_short_flag` asserted the version string
  directly against CLI output without accounting for rich's ANSI
  highlighting splitting the digits into separate escape sequences —
  fixed by stripping ANSI codes before the substring check.

## [1.0.0] - 2026
### Added
- Initial v1.0.0 release as part of the GenesisAeon ecosystem-wide 1.0.0
  milestone.
- Standardized release tooling: `.zenodo.json`, GitHub Actions release
  workflow (`.github/workflows/release.yml`), `RELEASE_GUIDE.md`,
  `CONTRIBUTING.md`, issue/PR templates.

### Changed
- Project metadata (`pyproject.toml`) normalized: version bumped to
  1.0.0, `requires-python`, and GenesisAeon-ecosystem dependency pins
  (`aeon-ai`, `entropy-governance`, `genesis-os`, `sigillin`,
  `unified-mandala`, `universums-sim`, `utac-core`) bumped to `>=1.0.0`.
- Relicensed: source code now under GPL-3.0-or-later (previously MIT);
  documentation now licensed separately under CC BY 4.0. See
  `LICENSE` and `LICENSE-DOCS.md`.
