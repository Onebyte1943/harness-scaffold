# Quick Start

Get harness running in your project in under 5 minutes.

## Installation

PyPI distribution name is **`harness-scaffold`** (the bare `harness` name was already taken on PyPI by an unrelated project). The import path and CLI binary remain `harness`.

There are two install modes — pick based on whether you want `harness` available everywhere on your machine, or scoped to one project.

### Mode A — Global install (the `harness` command on your PATH)

This is what most users want. Use an isolated-environment installer so the script lands somewhere your shell can find it:

```bash
# With uv (recommended)
uv tool install harness-scaffold

# Or with pipx
pipx install harness-scaffold
```

Then verify:

```bash
harness --version
```

To install from GitHub instead of PyPI (track `main`, or before a release is cut):

```bash
uv tool install git+https://github.com/Onebyte1943/harness-scaffold.git
# or
pipx install git+https://github.com/Onebyte1943/harness-scaffold.git
```

### Mode B — Per-project install (inside a virtualenv)

Use this when you want harness pinned alongside your project's other Python tooling, or when you're embedding harness into an existing Python codebase.

**uv-managed project:**
```bash
uv add harness-scaffold
uv run harness --version
uv run harness init --agent claude
```

**Plain venv + pip:**
```bash
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install harness-scaffold
harness --version
```

### From source (development)

```bash
git clone https://github.com/Onebyte1943/harness-scaffold.git
cd harness-scaffold
uv sync
uv run harness --version
```

## Upgrading

Use the upgrade command that matches how you installed.

| Install path | Upgrade command |
|---|---|
| `uv tool install` | `uv tool upgrade harness-scaffold` |
| `pipx install` | `pipx upgrade harness-scaffold` |
| venv + `pip install` (venv activated) | `pip install --upgrade harness-scaffold` |
| `uv add` (uv project) | `uv lock --upgrade-package harness-scaffold && uv sync` |
| Source checkout | `git pull && uv sync` |

To pin a specific version, append `==<version>` (e.g. `uv tool install harness-scaffold==0.2.2`); `uv tool` and `pipx` will reinstall in place.

After upgrading, confirm:

```bash
harness --version
```

If the version printed isn't what you expected, you likely have **two `harness` scripts on PATH** — one from `uv tool` / `pipx` and another from a venv or user-site `pip install`. Run `which harness` (PowerShell: `Get-Command harness`) to see which one is winning, then either reorder PATH or remove the stale install.

### Troubleshooting: `harness: command not found`

If you ran `pip install harness-scaffold` outside a venv and the `harness` command isn't found, one of these is the cause:

- **Script directory not on PATH.** A bare `pip install --user` puts the entry-point script under `~/.local/bin` (Linux), `~/Library/Python/3.X/bin` (macOS), or `%APPDATA%\Python\Python3X\Scripts` (Windows). Run `python -m site --user-base` to find yours, then add `<that>/bin` to your PATH — or just use `uv tool install` / `pipx`, which handle PATH for you.
- **PEP 668 blocked the install** (Python 3.12+ on macOS / Debian / Ubuntu). The system Python refuses bare `pip install`. Use `uv tool install` / `pipx`, or install inside a venv.
- **Wrong Python.** `pip` and `python` may point to different interpreters. Try `python3 -m pip install harness-scaffold` and re-check.

## Initialize a Project

Navigate to your project root and run:

```bash
harness init --agent claude
```

This generates the design-v3 footprint, organized into three layers.

> **Narrative language.** Generated playbooks, `AGENTS.md`, `CLAUDE.md`, and the principle pack ship in **Chinese (`zh`) by default**. Pass `--output-lang en` if your team prefers English narrative. Structural items (section headings, YAML frontmatter, Provenance blocks, paths, IDs, `/hx-*` command names) stay English regardless — see [Advanced Usage → Output Language](advanced-usage.md#output-language).

### 1. The Brain (`.harness/`)

Tool-neutral core — playbooks, scripts, registry, the seed material agents need.

```
.harness/
├── config.toml               # User-facing settings (profile, flow, lang, agents)
├── registry.toml             # Adapter capability matrix
├── playbooks/                # 14 command playbooks
│   ├── 00-constitution.md
│   ├── 10-baseline.md
│   ├── 12-next.md
│   ├── 30-propose.md
│   ├── 31-clarify.md
│   ├── 32-design.md
│   ├── 33-plan.md
│   ├── 34-tasks.md
│   ├── 35-analyze.md
│   ├── 40-implement.md
│   ├── 41-verify.md
│   ├── 50-review.md
│   ├── 51-archive.md
│   └── 90-doctor.md
├── scripts/sh/
│   ├── verify.sh             # Single deterministic sensor
│   └── lib/common.sh
├── memory/                   # L-RULE — constitution.md lands here (lazy)
├── knowledge/                # L-STATE — 7 docs + how-to/ + adr/ (lazy)
├── principle-packs/
│   └── generic.md            # Seed principles for /hx-constitution
├── evals/
│   └── README.md             # Sample format for /hx-doctor regressions
└── templates/                # Project-local template overrides (optional)
```

### 2. The Shared Contract

Cross-agent files that define the engineering process.

```
AGENTS.md                     # Agent operating contract (T13 schema)
.gitlab-ci.yml                # MR pipeline (verify + review) + scheduled drift
.pre-commit-config.yaml       # Calls .harness/scripts/sh/verify.sh --fast
.agent/                       # Cross-session progress log (lazy: .agent/progress.md)
specs/                        # Per-change artifacts (lazy, flat NNN-slug layout)
```

### 3. The Adapter Layer

Per-agent translation of harness commands into native formats. Both Claude
and Codex use the same `/hx-<cmd>` surface in design v3.

**Claude Code:**
```
CLAUDE.md                     # @AGENTS.md import + thin Claude-specific block
.claude/
├── commands/                 # 14 /hx-* slash command files
│   ├── hx-constitution.md
│   ├── hx-baseline.md
│   ├── hx-next.md
│   └── ...
├── hooks/                    # Available for verify-on-save, etc.
└── settings.json             # Permissions for .harness/**, specs/**, .agent/**
```

**Codex CLI:**
```
.codex/
└── commands/                 # 14 /hx-* slash command files
    ├── hx-constitution.md
    └── ...
```

## Verify the Setup

```bash
harness doctor
```

Expected output:

```
Harness Doctor — checking your-project


All checks passed.
```

Add `-v` to see every check, including the lazy paths that are correctly
"not yet created" right after init.

## W0 Bootstrap — First Session

After initialization, open the project in your AI agent and run the bootstrap workflow.

### Step 1: Synthesize Engineering Principles

```
/hx-constitution
```

Three-source synthesis: universal SDD principles + principle packs under
`.harness/principle-packs/` + the team's de-facto patterns inferred from the
codebase. Each principle is tagged `[enforceable]` (a hard gate) or
`[inferential]` (judgement). The result is saved to
`.harness/memory/constitution.md`.

### Step 2: Build the Knowledge Base

```
/hx-baseline
```

The agent builds the 7-document knowledge base under `.harness/knowledge/`:
`product`, `architecture`, `tech-stack`, `business`, `conventions`,
`glossary`, `setup-and-verify`, plus a `how-to/` recipes folder. Every claim
must cite `path:line` from the real code.

Pass `--depth L1|L2|L3` to scale the investigation (default `L2`). Use
`L1` for a quick survey, `L3` for high-stakes / legacy takeover. See
[Advanced Usage → Playbook Arguments](advanced-usage.md#playbook-arguments)
for the per-tier coverage gates.

### Step 3: Route Your Next Move

```
/hx-next
```

If you're not sure what command and flow level to use, ask `/hx-next`. It
reads the current state (recent commits, open specs, missing knowledge docs,
ADR gaps, verify status) and suggests the next move with a one-line
rationale. It writes no files.

### Step 4: Verify Everything Works

```
/hx-verify
```

Runs the unified verification script (`.harness/scripts/sh/verify.sh`):
lint → typecheck → tests → test-honesty. The same script is invoked by
editor hooks, pre-commit, and CI — no two sensors can disagree about whether
the build is green.

## Next Steps

- [Use Cases](use-cases.md) — See how harness handles real engineering scenarios
- [Advanced Usage](advanced-usage.md) — Customize flow levels, presets, and multi-agent setups
