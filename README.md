# Harness Scaffold

[![CI](https://github.com/Onebyte1943/harness-scaffold/actions/workflows/ci.yml/badge.svg)](https://github.com/Onebyte1943/harness-scaffold/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

> **Harness OS** scaffold for AI coding agents — five subsystems, one
> SDD workflow, every agent on the same contract.

Harness gives your team a Harness OS — five orthogonal subsystems for
running AI coding agents reliably across sessions — wrapped in a
spec-driven workflow that works the same way across Claude Code, Codex
CLI, and (via the adapter registry) Cursor / Copilot / Gemini.

## The 5 subsystems

The model is taken from [walkinglabs *learn-harness-engineering*](https://github.com/walkinglabs/learn-harness-engineering) (`skills/harness-creator`) and grounded in Anthropic's [*Effective Harnesses for Long-Running Agents*](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). Every artifact in a harness project belongs to exactly one subsystem.

| Subsystem | Minimum artifact | Purpose |
|---|---|---|
| **Instructions** | `AGENTS.md` | Entry, rules, definition of done |
| **State** | `feature_list.json` per spec | Current task, status, evidence |
| **Verification** | `init.sh` (calls `verify.sh`) | Commands the agent MUST run before claiming done |
| **Scope** | `depends_on` graph in `feature_list.json` | Boundaries and what blocks what |
| **Lifecycle** | `session-handoff.md` per spec | The next session can resume |

Every session passes through a **Resume → Advance → Handoff** loop:
read `AGENTS.md` + `init.sh` + `feature_list.json` + `session-handoff.md`,
pick one feature, verify, flip status, overwrite the handoff, commit.

## Why Harness?

AI coding agents are powerful but inconsistent. Different agents have different conventions, different context files, different ways of running commands. Teams end up with:

- **Fragmented workflows** — one process for Claude Code, another for Codex
- **No shared quality bar** — agents skip tests, ignore conventions, produce inconsistent output
- **Lost context** — decisions aren't recorded, specs aren't tracked, handoffs are lossy

Harness solves this with **5 subsystems → one brain, many frontends**:

```
┌──────────────────────────────────────────────────┐
│              .harness/ (the brain)               │
│  playbooks · scripts · registry · knowledge      │
├──────────────────────┬───────────────────────────┤
│      Claude          │        Codex              │
│      /hx-*           │        /hx-*              │
└──────────────────────┴───────────────────────────┘
  (Cursor / Copilot / Gemini extensible via registry)
```

## Core Concepts

- **Playbooks** — Tool-neutral step-by-step procedures for every engineering phase (14 commands from `constitution` to `doctor`)
- **Spec-Driven Development (SDD)** — Per-change artifacts live at `specs/<NNN>-<slug>/` (spec-kit flat convention)
- **Knowledge base** — Diátaxis + C4 + arc42 + BIZBOK + Tech Radar hybrid: 7 fixed docs + `how-to/` recipes + ADRs, all under `.harness/knowledge/`
- **Flow levels** — Scale ceremony to task size: `quick` (4 commands) → `standard` (7) → `full` (10+) → `epic` (multi-change)
- **Verify as invariant** — A single `verify.sh` script is invoked by editor hooks, pre-commit, and GitLab CI — so no two sensors can disagree about whether the build is green
- **Adapters** — Thin translation layers that map harness commands into each agent's native format (slash commands, rules, instructions)

## Quick Start

PyPI distribution name is **`harness-scaffold`** (the bare `harness` name was already taken). The import path and CLI binary stay `harness`.

### Install globally (recommended — gives you the `harness` command system-wide)

```bash
# With uv (recommended)
uv tool install harness-scaffold

# Or with pipx
pipx install harness-scaffold
```

`uv tool` / `pipx` install into an isolated environment and add the `harness` script to your PATH. Verify with `harness --version`.

### Install per-project (inside a virtualenv)

```bash
# uv-managed project
uv add harness-scaffold
uv run harness --version

# Plain venv + pip
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install harness-scaffold
harness --version
```

### Install from GitHub (track main, or before a release is cut)

```bash
uv tool install git+https://github.com/Onebyte1943/harness-scaffold.git
# or
pipx install git+https://github.com/Onebyte1943/harness-scaffold.git
```

> **`harness: command not found` after `pip install`?** Bare `pip install harness-scaffold` (no venv) installs the script to user-site bin (`~/.local/bin` on Linux, `~/Library/Python/3.X/bin` on macOS) which is often not on PATH; on Python 3.12+ PEP 668 blocks system installs entirely. Use `uv tool install` or `pipx` for global CLI use, or activate a venv first.

### Upgrade

Match the upgrade command to how you installed:

```bash
uv tool upgrade harness-scaffold              # uv tool install
pipx upgrade harness-scaffold                 # pipx install
pip install --upgrade harness-scaffold        # venv + pip (venv activated)
uv lock --upgrade-package harness-scaffold && uv sync   # uv project
```

Confirm with `harness --version`. See [docs/quick-start.md → Upgrading](docs/quick-start.md#upgrading) for pinning, version verification, and resolving "two `harness` on PATH" conflicts.

### Initialize in your project

```bash
cd your-project
harness init --agent claude
harness doctor
```

This generates the design-v3 footprint:

```
your-project/
├── .harness/                    # Brain (tool-neutral)
│   ├── config.toml
│   ├── registry.toml
│   ├── playbooks/               # 14 workflow playbooks
│   ├── scripts/sh/              # Single-source-of-truth verify
│   ├── memory/                  # L-RULE (constitution lives here)
│   ├── knowledge/               # 7 docs + how-to/ + adr/
│   ├── principle-packs/         # Seed principles for /hx-constitution
│   ├── evals/                   # Regression samples for /hx-doctor
│   └── templates/               # Project-local template overrides
├── AGENTS.md                    # Shared agent contract (T13)
├── CLAUDE.md                    # Claude Code entry point (imports @AGENTS.md)
├── .claude/commands/            # /hx-* slash commands for Claude
├── .codex/commands/             # /hx-* slash commands for Codex
├── .gitlab-ci.yml               # MR pipeline (verify + review) + scheduled drift
├── .pre-commit-config.yaml      # Same verify.sh, pre-commit
├── .agent/                      # Cross-session progress log
└── specs/                       # Per-change artifacts (lazy)
```

See [docs/quick-start.md](docs/quick-start.md) for the full walkthrough.

## The Workflow

Harness implements a four-phase engineering lifecycle:

| Phase | Commands | Purpose |
|-------|----------|---------|
| **W0 Bootstrap** | `constitution`, `baseline` | One-time project setup |
| **W1 Change** | `next` → `propose` → `clarify` → `design` → `plan` → `tasks` → `analyze` → `implement` → `verify` | SDD cycle per change |
| **W2 Review & Archive** | `review`, `archive` | Quality gate, post-merge knowledge refresh |
| **W3 Steer** | `doctor` | Self-check the harness itself |

`/hx-next` is the router — call it any time you're unsure what command (and flow level) is appropriate from current state.

Each command maps to a playbook in `.harness/playbooks/` and is invoked through the agent's native surface (e.g., `/hx-verify` in Claude Code or Codex).

## Baseline & Constitution Output Forms

Each command emits artifacts in **one authoritative form**, drawn from the de-facto standard for that artifact category. LLMs writing into a tightly-formed slot can't smuggle in abstract prose — `harness doctor` enforces the form (cite-density floor, required headings, table-vs-prose).

| Command | Artifact | Authoritative form |
|---|---|---|
| `/hx-constitution` | `.harness/memory/constitution.md` | [GitHub spec-kit](https://github.com/github/spec-kit) (Core Principles + 2 generic sections + Governance + version line + Sync Impact Report) |
| `/hx-baseline` | `architecture.md` | arc42 + C4 + Invariants table |
| `/hx-baseline` | `tech-stack.md` | Thoughtworks Tech Radar (Adopt / Trial / Assess / Hold) |
| `/hx-baseline` | `product.md` | Cohn user-story + Christensen Jobs-to-be-Done |
| `/hx-baseline` | `business.md` | **architecture-neutral** — BIZBOK + BABOK + OKR/SLO (works for traditional, CRUD, microservices, ML, data-pipeline projects equally) |
| `/hx-baseline` | `conventions.md` | Anchor file + GOOD/BAD pairs (Thoughtworks "Anchoring AI to a reference application") |
| `/hx-baseline` | `glossary.md` | Single ISO/IEC 11179 table |
| `/hx-baseline` | `setup-and-verify.md` | Google SRE runbook + Common Failures table + Environment Matrix |

`/hx-baseline` runs a **MEASURE → SYNTHESIZE → VERIFY** pipeline: deterministic tools (`pyreverse` / `madge` / `jdeps` / `cargo modules` / `go-callvis` / `syft` / `git churn`) gather ground truth before the LLM organises it into the templates above.

## Multi-Agent Support

```bash
# Initialize with multiple agents (defaults bundled)
harness init --agent claude --agent codex

# Add another agent later (Cursor / Copilot / Gemini extensible via registry)
harness init --agent codex
```

Each agent gets its own adapter layer while sharing the same brain. The registry tracks each agent's capabilities and provides graceful degradation paths. Cursor, Copilot and Gemini remain in the registry so a team can extend coverage without code changes — they are not promoted as the default bundle.

## Documentation

- [Quick Start](docs/quick-start.md) — Get up and running in 5 minutes
- [Use Cases](docs/use-cases.md) — Real-world scenarios and workflows
- [Advanced Usage](docs/advanced-usage.md) — Presets, flow levels, customization, narrative language switch

## Output language

Generated playbooks, `AGENTS.md`, `CLAUDE.md`, and the principle pack ship in two narrative languages — **Chinese (`zh`, default)** and **English (`en`)** — selected at init time via `--output-lang`:

```bash
harness init --agent claude              # 中文 narrative (default)
harness init --agent claude --output-lang en   # English narrative
```

Structural items always stay English regardless of the flag — section headings (`## Purpose`, `## Steps`, …), YAML frontmatter keys, Provenance blocks (label + 3 content lines), `⟨…⟩` placeholders, `{{ jinja_var }}` template variables, `/hx-*` command names, stable IDs (`REQ-NNN`, `DEC-NNN`, …), tags (`[enforceable]`, `[inferential]`, `[P]`), proper nouns (C4, arc42, BIZBOK, MADR, Diátaxis, …), and code blocks. Agents pattern-match on these — switching them would break playbook parsing. See [Advanced Usage → Output Language](docs/advanced-usage.md#output-language) for the full translation contract.

## Requirements

- Python >= 3.10
- Git (recommended)

## License

MIT
