# Contributing to Harness

Thanks for considering a contribution. This project is an opinionated
tool — most successful PRs start with an issue describing the problem
you hit and the change you have in mind. That keeps everyone aligned
before code is written.

## Development setup

Harness uses [`uv`](https://docs.astral.sh/uv/) for dependency
management. A working Python 3.10+ is the only prerequisite.

```bash
# Install dependencies (creates .venv automatically)
uv sync --all-extras --dev

# Run the full local verify pipeline (same checks CI runs)
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
uv run pytest
```

If any of those fail locally, CI will fail too — fix them before
opening a PR.

## Project layout

```
src/harness/
  adapters/       per-agent surfaces (claude, codex, ...)
  cli/            click commands: init, doctor
  core/           config, layout, registry, scaffold engine
  templates/      Jinja2 templates rendered at scaffold time
tests/            mirrors src/ layout
```

The repository is organized around a **one-brain, many-frontends**
shape: `core/` and `templates/harness/` are tool-neutral; everything
under `adapters/` and `templates/adapters/` translates that brain into
one specific agent's surface.

## Templates: the localization contract

Every translatable template ships as a pair: `<stem>.zh.md.j2` and
`<stem>.en.md.j2`. Structural items — section headings, YAML
frontmatter, Provenance blocks, `/hx-*` command names, stable IDs,
paths — MUST be byte-identical between the two language variants;
only narrative prose differs.

`tests/templates/test_localization_parity.py` enforces this. If you
add a new translatable template, add its stem to `TRANSLATABLE_STEMS`
in that test file.

## Pull-request checklist

Before requesting review:

- [ ] An issue describes the motivation (skip only for typo / docs
      fixes)
- [ ] `uv run ruff check src tests` passes
- [ ] `uv run ruff format --check src tests` passes
- [ ] `uv run mypy src` passes (strict mode)
- [ ] `uv run pytest` passes (130+ tests including localization parity)
- [ ] New behavior has a test; new public surface has a docstring
- [ ] If you touched a `.zh.md.j2` template, you also touched the
      matching `.en.md.j2` (and vice versa)
- [ ] `CHANGELOG.md` has an entry under `## [Unreleased]`

## Commit messages

One-line summary in imperative mood, capped at 72 chars. Body
optional, wrapped at 72. Reference issues with `Fixes #N` /
`Refs #N`.

```
Fix scaffold engine swallowing missing-template errors

The previous behavior fell back to an empty render, which made it
easy to ship a broken adapter. Raise FileNotFoundError instead and
surface the path in the message.

Fixes #42
```

## Reporting bugs

Open a GitHub issue with: harness version (`harness --version`),
Python version, the command that failed, the full traceback. A
minimal reproduction (a fresh `harness init` in a temp dir) is the
fastest path to a fix.

## Security issues

Do NOT open a public issue for security vulnerabilities. See
[SECURITY.md](SECURITY.md) for the private disclosure path.
