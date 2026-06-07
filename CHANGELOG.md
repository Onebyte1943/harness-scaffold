# Changelog

All notable changes to this project are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-06-07

Initial public release on PyPI as **`harness-scaffold`**.

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
- `.github/workflows/release.yml` — builds sdist + wheel on tag push,
  verifies the tag matches `pyproject.toml`, runs `twine check`,
  publishes to PyPI via trusted publishing, and attaches dists to the
  GitHub release.
- `[project.urls]`, `keywords`, and PEP 639 classifier set in
  `pyproject.toml` for richer PyPI metadata.
- Install paths documented for both PyPI (`pip install
  harness-scaffold`) and `git+https://github.com/Onebyte1943/harness-scaffold.git`.

### Notes

- PyPI distribution name is **`harness-scaffold`** because the bare
  `harness` name was already taken on PyPI by an unrelated project.
  `[tool.uv.build-backend]` pins `module-name = "harness"` so the
  wheel still ships `src/harness/` and `import harness` /
  `harness <cmd>` continue to work unchanged.
- `importlib.metadata.version()` looks up the distribution name
  `harness-scaffold`, not the module name; `harness --version` reports
  `0.1.0` (not `0.0.0+unknown`).
- Minor robustness fixes in `harness init` and `ScaffoldEngine` —
  narrower exception handling around `questionary`, `sys.stdin`, and
  Jinja `TemplateNotFound`.

[Unreleased]: https://github.com/Onebyte1943/harness-scaffold/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Onebyte1943/harness-scaffold/releases/tag/v0.1.0
