# Changelog

All notable changes to this project are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.1] - 2026-06-08

### Fixed

- Two `E501` long lines (`doctor_cmd.py:337`, `init_cmd.py:440`) that
  slipped past local checks but failed CI lint on the 0.2.0 push.
- `ruff format` drift in `doctor_cmd.py`, `init_cmd.py`, `i18n.py`,
  `scaffold.py` — auto-reformatted to match repo style.

No behavior change vs 0.2.0 — pure source-hygiene release so the PyPI
artifact matches the post-0.2.0 main branch.

## [0.2.0] - 2026-06-08

A pivot on how the scaffold handles multilingual output. Instead of
generating per-locale template variants at `harness init` time, the
scaffold now produces a single English source-of-truth and lets each
`/hx-*` agent decide deliverable narrative language at runtime,
guided by an explicit Output Language Contract.

### Added

- **`harness.core.i18n`** — runtime message tables (zh / en) covering
  every CLI-emitted string: `harness init` progress prints, summary
  table headings and rows, the "Next steps" panel, the interactive
  `questionary` agent picker, and `harness doctor` diagnostics. CLI
  output now honors `--output-lang` (default `zh`) and `doctor`
  reads it from `.harness/config.toml`.
- **`## Output Language Contract`** — new top-of-AGENTS.md section,
  rendered with the live `output_lang` value, that tells every
  `/hx-*` agent how to write deliverables: prose follows
  `output_lang`; headings, frontmatter, Provenance blocks, RFC 2119
  keywords (MUST / MUST NOT / SHOULD / SHOULD NOT / MAY), stable IDs
  (REQ-NNN, DEC-NNN, ADR-NNNN, P1–P5, T1–T16, US-N, …), methodology
  names (Saga, TCC, Outbox, Redlock, fencing token, C4, arc42, MADR,
  BIZBOK, 12-Factor, OWASP, AIP, AAA, Expand → Contract, Diátaxis),
  code identifiers, file paths, structural labels, and the verbatim
  content of any ``` fenced seed block stay English.
- Adapter slash-command files (Claude + Codex) now explicitly point
  to the Output Language Contract so it is re-loaded on every
  `/hx-*` invocation.

### Changed

- **Templates collapsed to single English source.** Removed the
  `.zh.*.j2` / `.en.*.j2` template pairing; each artifact now has one
  canonical template (`playbooks/*.md.j2`, `AGENTS.md.j2`, etc.).
  Eliminates drift between language variants and protects AI
  pattern-match accuracy — the agent's contract surface is one
  language by construction.
- Adding a new output language now requires zero scaffold work; only
  add a `Messages` literal in `i18n.py` for CLI runtime strings.

### Removed

- ~22 `.zh.*.j2` template variants (playbooks, principle pack, evals
  README, AGENTS.md, CLAUDE.md, slash commands, scripts, CI / TOML /
  gitignore).
- `ScaffoldEngine.render_localized()` — no remaining callers; the
  public scaffold API is now `render_file` / `render_static` /
  `ensure_dir` only.
- `tests/templates/test_localization_parity.py` and
  `tests/templates/test_seed_contract.py` — both assumed zh/en
  template pairs that no longer exist.
- Per-locale skill-description dicts in claude / codex adapters
  (`_SKILL_DESCRIPTIONS_ZH`).

### Migration notes

- Projects scaffolded with 0.1.0 keep their existing files. To pick
  up the new English templates + Output Language Contract, run
  `harness init --force` in the project root.
- The `--output-lang` flag and `.harness/config.toml#output_lang`
  field are unchanged on the wire. What changed is *when* they're
  consumed: previously at scaffold time, now at `/hx-*` runtime.
- Net diff: −3,552 / +171 lines.

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
