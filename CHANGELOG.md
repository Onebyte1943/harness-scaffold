# Changelog

All notable changes to this project are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- **Architecture pivot — single-source-of-truth English templates with
  runtime-decided deliverable language.** Templates no longer ship as
  `.zh.*.j2` / `.en.*.j2` pairs; `harness init` always renders the same
  English playbooks, AGENTS.md, CLAUDE.md, slash-command files,
  `verify.sh`, `registry.toml`, etc. The `output_lang` config field is
  persisted to `.harness/config.toml` and consumed at `/hx-*` runtime
  by the AI agent — the agent reads the new **Output Language
  Contract** section at the top of AGENTS.md and writes deliverables
  (specs/, knowledge/, constitution.md, progress.md, review reports,
  ADRs) in `output_lang`, while keeping headings, frontmatter,
  Provenance, RFC 2119 keywords, stable IDs (REQ/DEC/T/P), methodology
  names (Saga, TCC, Outbox, Redlock, fencing token, …), code
  identifiers, file paths, and ``` fenced seed contents in English.
- Why: prevents translation drift, eliminates per-locale maintenance
  cost, and protects AI pattern-match accuracy (the agent's contract
  surface stays in one canonical language). Adding new output
  languages now requires zero scaffold work — only an addition to
  `i18n.py` for CLI runtime strings.
- CLI runtime output (init progress / summary table / Next steps panel
  / doctor diagnostics) is still localized per `--output-lang` via
  `harness.core.i18n.messages()`. This concern is orthogonal to the
  template layer.

### Removed

- All `.zh.*.j2` template variants (~22 files).
- `ScaffoldEngine.render_localized()` — no remaining callers; the
  public scaffold API is now `render_file` / `render_static` /
  `ensure_dir` only.
- `tests/templates/test_localization_parity.py` and
  `tests/templates/test_seed_contract.py` — both assumed zh/en
  template pairs that no longer exist.
- Per-locale skill-description dicts in claude / codex adapters
  (`_SKILL_DESCRIPTIONS_ZH`).

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
