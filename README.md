auto-rebase — Automated Re-targeting of Feature Customizations

Overview

auto-rebase helps re-target feature customizations when a Base SW updates. Given base-OLD, base-NEW, and feature-OLD, it produces feature-NEW with re-applied customizations, machine-readable patchsets, and a human report with traceability and validation.

Quickstart (Engine CLI)

- Optional: `bash scripts/install_tools.sh`
- Run the demo on included sample data:

```
python -m engine.cli.auto_rebase init --old-base data/sample/base-1.0 --new-base data/sample/base-1.1 --feature data/sample/feature-5.0 --req-map data/sample/requirements_map.yaml --workdir artifacts/run1
python -m engine.cli.auto_rebase extract-feature --out artifacts/run1/feature_patch
python -m engine.cli.auto_rebase extract-base --out artifacts/run1/base_patch
python -m engine.cli.auto_rebase retarget --feature-patch artifacts/run1/feature_patch --base-patch artifacts/run1/base_patch --new-base data/sample/base-1.1 --out artifacts/run1/feature-5.1
python -m engine.cli.auto_rebase validate --path artifacts/run1/feature-5.1 --report artifacts/run1/report.html
python -m engine.cli.auto_rebase finalize --path artifacts/run1/feature-5.1 --tag v5.1 --trace artifacts/run1/trace.json
```

What You Get

- feature-NEW tree with applied changes
- Machine-readable ΔF and ΔB patchsets
- report.html and report.json (schema-validated)
- trace.json listing requirement IDs per patch unit
- Optional git tag and commit trailers

Monorepo Layout

See files under `engine/`, `server/`, `mcp-server/`, and `web/`. Adapters automatically detect external tools and fall back to robust text-based strategies if unavailable (e.g., difflib/comby heuristics).

Environment

- Python 3.11+ recommended
- Node 18+ for MCP server and Next.js app
- Optional external tools: git, difftastic, gumtree, clang-tidy, coccinelle, dtc, yq, comby

Development

- Formatting/lint: ruff, black, isort configured in `pyproject.toml`
- Tests: `pytest` (see `tests/`)
- CI: GitHub Actions in `.github/workflows/ci.yml`

Limitations & Fallbacks

- External binaries are detected at runtime. If missing, adapters degrade gracefully with warnings and use text merges.
- Sample adapters implement pragmatic heuristics sufficient for demo and unit tests.

Adding a New Adapter

- Implement the `Adapter` Protocol in `engine/adapters/*.py`.
- Register detection, extraction, retargeting, apply, and validate. Prefer semantic ops; provide text fallback.

