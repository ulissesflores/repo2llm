# LLM Contextizer

**A zero-dependency Python CLI for turning a codebase into an LLM-ready text snapshot.**

<p align="center">
  <img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/dependencies-zero-brightgreen" alt="Dependencies">
  <img src="https://img.shields.io/badge/status-stable-green" alt="Status">
</p>

`LLM Contextizer` scans a project directory, prints a readable ASCII tree, and then emits a single concatenated text output of file contents. The result is designed for copy/paste into ChatGPT, Claude, Gemini, or any other LLM workflow where you need a fast, deterministic snapshot of a repository.

## At a glance

- Runtime: standard-library-only Python CLI
- Input: any local project directory
- Output: ASCII tree followed by concatenated file contents
- Safety model: default ignore rules, truncation for log-like files, and self-inclusion protection
- Configuration: optional per-project `.llmignore`
- Citation: Zenodo archival DOI available for research use

```bash
python3 src/contextizer.py /path/to/project > context.txt
```

## Why this exists

LLMs have limited context windows, and real repositories contain:

- dependency folders (`node_modules`, `venv`, etc.)
- build artifacts, caches, binaries
- large data and log files that explode token budgets

This tool aims to be:

- **portable**: standard library only
- **deterministic**: stable ordering makes runs predictable
- **safe-by-default**: avoids common footguns
- **LLM-friendly**: tree first, then contents

## Key features

- **Project tree visualization**
  - Prints an ASCII directory tree before the content dump.
- **Noise filtering by default**
  - Skips common junk folders and binary extensions such as `.git`, `node_modules`, `.venv`, images, and archives.
- **Truncation for large or log-like files**
  - Truncates selected file types such as `.csv`, `.log`, `.tsv`, `.jsonl`, and `.sql`.
- **Per-project `.llmignore`**
  - Supports lightweight per-project exclusions without introducing extra dependencies.
- **Output safety**
  - Detects redirected output files inside the scanned root and excludes them to avoid self-inclusion.

## Installation

Clone the repository. There are no runtime dependencies.

```bash
git clone https://github.com/ulissesflores/llm-contextizer.git
cd llm-contextizer
```

Optional: create a shell alias for faster local use.

```bash
alias llmctx='python3 /absolute/path/to/llm-contextizer/src/contextizer.py'
```

## Quick start

```bash
python3 src/contextizer.py . > context.txt
```

Run against the current directory:

```bash
python3 src/contextizer.py
# or, with the alias:
llmctx
```

Target another directory:

```bash
python3 src/contextizer.py ../some-project
```

Pipe to clipboard:

```bash
python3 src/contextizer.py . | pbcopy   # macOS
python3 src/contextizer.py . | xclip    # Linux
```

## Output format

The output has two parts:

1. `PROJECT STRUCTURE`
2. `PROJECT FILE CONTENTS` with file separators and relative paths

This consistent structure helps an LLM understand the repository before reading the code.

## Configuration

### `.llmignore`

Create a .llmignore file at the project root you are scanning.

Supported syntax is intentionally minimal:

- `dir/` ignores a directory by name
- `*.ext` ignores a file extension
- `filename` ignores a specific file name

Example:

```txt
# directories (by name)
dist/
build/
coverage/
__pycache__/

# secrets
.env
.env.*
*.pem
*.key

# large/noisy
*.log
*.csv
*.tsv
*.jsonl
```

Tip: the repository includes a ready-to-copy template in `.llmignore.example`.

## Architectural decisions

Core decisions are documented under docs/adr/:

- ADR 0001: Zero Dependencies Policy
- ADR 0002: Output Safety (Prevent self-inclusion on stdout redirect)

## Versioning

This project follows **Semantic Versioning** and maintains a human-readable changelog in CHANGELOG.md.

- Patch: bug fixes (`0.1.x`)
- Minor: backwards-compatible feature additions (`0.x.0`)
- Major: breaking changes (`x.0.0`)

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a branch from `main`
3. Keep changes focused
4. Add or update docs when behavior changes
5. Open a PR

## 📜 Citation

If you use this software in academic or research contexts, cite the Zenodo archival record below.

The repository continues beyond the archived runtime release through documentation and metadata maintenance, but the DOI remains the stable scholarly reference point.

- **Archival DOI:** https://doi.org/10.5281/zenodo.18343438
- **Archival runtime release:** `v0.1.1`
- **Latest GitHub release carrying the DOI reference:** `v0.1.2`

### BibTeX
```bibtex
@software{flores_2026_llm_contextizer,
  author       = {Flores, Carlos Ulisses},
  title        = {LLM Contextizer},
  year         = {2026},
  version      = {v0.1.1},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18343438},
  url          = {https://doi.org/10.5281/zenodo.18343438}
}
```

### APA
Flores, C. U. (2026). *LLM Contextizer* (v0.1.1) [Software]. Zenodo. https://doi.org/10.5281/zenodo.18343438

> For reproducibility and scholarly reference, prefer the Zenodo DOI rather than an unversioned repository URL.

## License

Licensed under the Apache License 2.0. See LICENSE.
