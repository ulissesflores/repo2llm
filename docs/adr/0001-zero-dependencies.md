# ADR 0001: Zero Dependencies Policy

- Status: Accepted
- Date: 2026-01-20
- Deciders: Ulisses Flores

## Context

repo2llm is a CLI tool intended to be run directly in arbitrary codebases and environments.
The primary use case is generating a single, token-efficient textual snapshot of a project for use in LLM prompts.

Most Python CLIs introduce dependency and environment friction (pip/venv/poetry/click/rich/etc.).
That friction directly harms portability, onboarding, and “copy → run” usability.

## Decision

repo2llm SHALL be implemented using only the Python standard library.

- No third-party packages.
- No runtime dependency installation steps.
- Python 3.8+ compatibility.

## Rationale

- Maximum portability across environments and CI systems.
- Deterministic execution without dependency resolution.
- Lower supply-chain and security risk (no transient dependencies).
- Better UX for the target audience (developers using the tool ad-hoc).

## Consequences

### Positive
- Simple installation: clone and run.
- Lower maintenance surface (no dependency updates).
- Predictable behavior across systems.

### Negative
- Some CLI ergonomics (colors, rich formatting, glob matching) must be implemented manually or avoided.
- Feature set is constrained by the standard library.

## Notes

This policy is foundational. Exceptions require a new ADR.