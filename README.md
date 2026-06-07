# Harness Scaffold

[![CI](https://github.com/Onebyte1943/harness-scaffold/actions/workflows/ci.yml/badge.svg)](https://github.com/Onebyte1943/harness-scaffold/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

> Unified AI agent engineering scaffold for teams.

Harness gives your team a **single engineering process** that works across every AI coding agent — Claude Code and Codex CLI by default, with Cursor / Copilot / Gemini extensible via the adapter registry. Instead of each agent inventing its own workflow, harness provides tool-neutral playbooks, a single deterministic verify script, and a Spec-Driven Development cycle, with thin adapter layers that translate them into each agent's native surface.

## Why Harness?

AI coding agents are powerful but inconsistent. Different agents have different conventions, different context files, different ways of running commands. Teams end up with:

- **Fragmented workflows** — one process for Claude Code, another for Codex
- **No shared quality bar** — agents skip tests, ignore conventions, produce inconsistent output
- **Lost context** — decisions aren't recorded, specs aren't tracked, handoffs are lossy

Harness solves this with a **one brain, many frontends** architecture:

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

```bash
# Install (PyPI — distribution name is harness-scaffold; import + CLI stay `harness`)
pip install harness-scaffold
# or with uv
uv tool install harness-scaffold

# Or install directly from GitHub (works before any PyPI release)
pip install git+https://github.com/Onebyte1943/harness-scaffold.git
# or
uv tool install git+https://github.com/Onebyte1943/harness-scaffold.git

# Initialize in your project
cd your-project
harness init --agent claude

# Check setup
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
