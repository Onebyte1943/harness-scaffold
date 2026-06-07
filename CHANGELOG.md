# Changelog

All notable changes to this project are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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

[Unreleased]: https://github.com/Onebyte1943/harness/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Onebyte1943/harness/releases/tag/v0.1.0
