# Changelog

All notable changes to this project will be documented in this file.

The format is based on *Keep a Changelog*, and this project adheres to *Semantic Versioning*.

## [Unreleased]
- (placeholder)

## [0.1.0] - 2026-01-22
### Added
- Initial public release of the repo2llm CLI.
- `.llmignore` support for per-project exclusions.
- Directory tree output + concatenated file contents output.
- Truncation for large/log-like files.
- Output safety: prevent self-inclusion when redirecting stdout to a file within the scanned root.
- ADRs for core architectural decisions.

## [0.1.1] - 2026-01-22
### Added
- Citable metadata files (CITATION.cff, codemeta.json, .zenodo.json) for scholarly citation and archival workflows.

## [0.1.2] - 2026-01-22
### Added
- Explicit reference to the Zenodo-minted DOI for the v0.1.1 archival release.
- Updated citation and metadata files to support formal academic referencing.
  
## [0.1.3] - 2026-01-22
### Changed
- Improved DOI/citation metadata for better compatibility with indexers (CITATION.cff, codemeta.json).
- No runtime, behavioral, or algorithmic changes.

## [0.1.4] - 2026-01-22
### Changed
- Aligned metadata version fields with the Git tag (CITATION.cff, codemeta.json).
- Clarified Zenodo DOI as the canonical archival citation target via `preferred-citation`.
- No runtime, behavioral, or algorithmic changes.
  
## [0.1.5] - 2026-01-22
### Changed
- Normalize changelog and citation metadata (no runtime changes).

## [0.1.6] - 2026-01-22
### Changed
- Align CITATION.cff and codemeta.json version fields with the release tag (no runtime changes).

## [0.1.7] - 2026-01-22
### Changed
- Added ready-to-copy citation formats (BibTeX and APA) in README for improved scholarly usability (no runtime changes).

