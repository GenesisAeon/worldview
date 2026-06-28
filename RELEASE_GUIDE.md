# Release Guide

This package follows the GenesisAeon ecosystem release process.

## Versioning

We use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

- **MAJOR** — breaking changes to the public API (`WorldviewEngine`,
  `CriticalityChecker`, `AlignmentFramework`) or the CLI.
- **MINOR** — new features, backwards-compatible.
- **PATCH** — bug fixes, documentation, dependency bumps.

## Release types

| Tag pattern | Channel | Where it publishes |
|---|---|---|
| `vX.Y.Z` | Production | PyPI, GitHub Release, Zenodo (if integration enabled) |
| `vX.Y.Z-rc.N`, `-alpha.N`, `-beta.N` | Canary | TestPyPI, GitHub pre-release |

## How to cut a release

1. Ensure `CHANGELOG.md` has an entry for the new version under
   `## [X.Y.Z]`.
2. Ensure `pyproject.toml`'s `[project].version` matches.
3. Ensure `.zenodo.json`'s `"version"` field matches.
4. Commit these changes (if any) to `main`.
5. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
6. The `.github/workflows/release.yml` workflow builds, tests, and
   publishes automatically.
7. For production releases, Zenodo mints/updates a DOI version
   automatically from the GitHub Release using `.zenodo.json` metadata
   (worldview already has Zenodo-GitHub integration enabled — DOI
   10.5281/zenodo.19191015).

## Dependency pins within the GenesisAeon ecosystem

`worldview` depends on `aeon-ai`, `entropy-governance`, `genesis-os`,
`sigillin`, `unified-mandala`, `universums-sim`, and `utac-core` via the
`[full-stack]` extra. Pin these with `>=` lower bounds matching the
minimum version that provides the API this package relies on. Do not pin
exact versions (`==`) for ecosystem dependencies.

`worldview` sits late in the GenesisAeon release dependency chain (tier
T15) — do not tag a new `worldview` release until `universums-sim` (tier
T14) has an actual published release matching the pin above.
