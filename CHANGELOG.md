# Changelog

All notable changes to this project are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- **Project renamed to `harness-scaffold`.** GitHub repo, local
  directory, documentation titles, and all `[project.urls]` now use
  `harness-scaffold`. The Python package, the `import harness`
  module path, the `.harness/` brain directory in scaffolded projects,
  and the `harness` CLI binary are all unchanged.
- PyPI distribution name is now **`harness-scaffold`** (the bare
  `harness` name was already taken on PyPI by an unrelated project).
  Configured via `[tool.uv.build-backend]` `module-name = "harness"`
  so the wheel still ships `src/harness/`.

### Added

- `[project.urls]`, `keywords`, and the PEP 639 classifier set in
  `pyproject.toml` for richer PyPI metadata.
- `.github/workflows/release.yml` — builds sdist + wheel on tag push,
  verifies the tag matches `pyproject.toml`, runs `twine check`,
  publishes to PyPI via trusted publishing, and attaches dists to the
  GitHub release.
- Documented `pip install git+https://...` / `uv tool install
  git+https://...` as the immediate-works install path alongside the
  PyPI install.

### Fixed

- `_prompt_agents()` in `harness init` no longer collapses every
  exception (including `ImportError + Exception` duplication) into the
  default agent list — only the relevant `ImportError` /
  `KeyboardInterrupt` / `EOFError` are caught.
- `ScaffoldEngine.has_template()` now catches `TemplateNotFound`
  specifically instead of bare `Exception`, so real Jinja errors
  surface.
- `_is_interactive()` no longer shadows the module-level `sys` import.

## [0.1.0] - 2026-06-07

Initial public release.

### Added

- `harness init` command — scaffold a new harness-managed repo with
  `.harness/` brain, per-agent adapters, and shared CI/pre-commit
  configuration. Supports `--profile`, `--flow`, `--lang`,
  `--output-lang`, `--preset`, `--agent` flags.
- `harness doctor` command — self-check for rule/guardrail sync,
  drift, and dead rules.
- 14 tool-neutral playbooks covering the SDD cycle: constitution,
  baseline, next, propose, clarify, design, plan, tasks, analyze,
  implement, verify, review, archive, doctor.
- Adapter registry pattern. Bundled adapters: Claude Code, Codex
  CLI. Cursor / Copilot / Gemini stubs in the registry for future
  extension.
- Bilingual templates (zh / en) with a structural-parity test
  (`tests/templates/test_localization_parity.py`) that prevents
  drift in headings, frontmatter, and Provenance blocks.
- Single deterministic `verify` script shared by hooks, pre-commit,
  and CI.
- Test suite: 130 tests including 60 localization-parity assertions.
- GitHub Actions CI: matrix over Python 3.10–3.13, with ruff,
  ruff format, mypy strict, and pytest + coverage.

[Unreleased]: https://github.com/Onebyte1943/harness-scaffold/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Onebyte1943/harness-scaffold/releases/tag/v0.1.0
