# Advanced Usage

Deep dive into harness configuration, customization, and advanced workflows.

## CLI Reference

### `harness init`

```bash
harness init [PROJECT] [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `PROJECT` | `.` | Target directory |
| `--agent`, `-a` | `claude` | Agent to support (repeatable: `--agent claude --agent codex`) |
| `--profile`, `-p` | `brownfield` | Project profile: `brownfield` or `greenfield` |
| `--flow`, `-f` | `standard` | Default flow level: `quick`, `standard`, `full`, `epic` |
| `--lang` | auto-detect | Primary **programming** language: `auto`, `python`, `typescript`, `go`, `rust`, `java`, `polyglot` |
| `--output-lang` | `zh` | **Narrative** language for generated playbooks and docs: `zh` (Chinese, default) or `en` (English). Structural items stay English regardless — see [Output Language](#output-language). |
| `--script` | auto-detect | Script shell: `sh` or `ps` |
| `--preset` | none | Workflow preset (repeatable): `trunk-based`, `ddd`, `secure` |
| `--force` | false | Re-render the brain over an existing install |
| `--no-git` | false | Skip git initialization |
| `--dry-run` | false | Preview without writing files |

Language autodetect inspects marker files at the project root
(`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `pom.xml`,
`build.gradle*`, …). If nothing matches, `lang` stays `auto`; if more than
one language matches, it becomes `polyglot`.

### `harness doctor`

```bash
harness doctor [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `-v`, `--verbose` | false | Show every check, including OK rows |

`harness doctor` is the lightweight CLI sensor that verifies the layout is
intact. The deeper self-check (rule↔guardrail sync, eval regressions,
design-doc scoring) lives in the `/hx-doctor` playbook.

### Global Options

```bash
harness --version    # Show version
harness --help       # Show help
```

## Output Language

Harness separates **structural language** from **narrative language**, and narrative is selected at `harness init` time via `--output-lang`.

| Layer | Language | Reason |
|-------|----------|--------|
| Section headings (`## Purpose`, `## Steps`, etc.) | **English, always** | Agents pattern-match on stable headings; switching them breaks playbook parsing. |
| YAML frontmatter keys (`name`, `phase`, `flow`) | **English, always** | Machine-parsed. |
| Provenance blocks — both the `> Provenance` label AND the three content lines (`> - Authoritative paradigm:` / `> - Investigation protocol:` / `> - Output form:`) | **English, always** | Shared with agent-loaded prompts; keeps tokenization predictable and cross-team. |
| Stable IDs (`REQ-NNN`, `DEC-NNN`, `Q-NNN`, …), tags (`[enforceable]`, `[inferential]`, `[P]`), `/hx-*` command names, file paths, `path:line` citations, `⟨…⟩` placeholders, `{{ jinja_var }}`, code blocks, table column headers, proper nouns (C4, arc42, BIZBOK, MADR, Diátaxis, Tornhill, Böckeler, SDD, TDD, MCP, etc.) | **English, always** | Contractual / referenced by downstream tooling. |
| Narrative body paragraphs · bullet bodies · numbered step bodies (including the bold step label) · how-to recipe prose | **Follows `--output-lang`** (default `zh`) | Translated at render time by Jinja conditionals; pick the language your team reads most fluently. |

`config.toml`'s `lang` field is the **programming** language (python / typescript / …) — it does NOT control narrative language. The narrative language is `output_lang` and is independent.

### Setting narrative language at init

```bash
harness init --agent claude                       # 中文 narrative (default)
harness init --agent claude --output-lang en      # English narrative
harness init --agent claude --output-lang zh      # explicit Chinese
```

The value is persisted as `output_lang` in `.harness/config.toml`. A `--force` re-render reads the flag again (defaults to `zh` if omitted), so re-rendering with the wrong flag will silently switch languages — always pass `--output-lang` explicitly on `--force`.

### Switching narrative language after init

There is no in-place migration. Two paths:

1. **Re-render with `--force`** — `harness init --agent claude --output-lang en --force` regenerates every rendered file from the bundled templates in the new language. Manual edits under `.harness/playbooks/`, `AGENTS.md`, `CLAUDE.md`, the principle pack, and the `/hx-*` slash-command files will be overwritten — back them up or commit first.
2. **Translate in place** — open each file under `.harness/playbooks/`, `AGENTS.md`, `CLAUDE.md`, and `.harness/principle-packs/generic.md` and rewrite the narrative paragraphs. Keep all "always English" items from the table above intact. Do NOT re-run `harness init --force` afterwards or your edits will be lost.

### When narrative language matters

- **AGENTS.md / constitution.md** — keep agent-facing instructions in the language your agents respond best to. Claude and Codex handle both Chinese and English fluently; the choice is team-readability.
- **Knowledge base (`.harness/knowledge/*.md`)** — pick one language per repo. Mixing within a single doc loses search affordance and confuses agents that summarize across docs. `/hx-baseline` will write in your team's language (it reads `output_lang` at run-time but ultimately follows the prevailing language of citations and existing docs).
- **Specs (`specs/<NNN>-<slug>/*.md`)** — match the language of the team's day-to-day communication (PR / MR descriptions, RFC docs).

## Playbook Arguments

Some `/hx-*` playbooks take optional arguments you pass when invoking the slash command in your agent. They are **not** CLI flags on the `harness` binary — they live in the playbook frontmatter and are read by the agent at runtime.

### `/hx-baseline --depth L1|L2|L3`

Controls how deep the knowledge-base investigation goes. Default is `L2`.

| Tier | Use when | Adds beyond previous tier |
|------|----------|---------------------------|
| `L1` survey | quick onboarding read; spike before deciding to invest | manifest scan · file inventory · top-level architecture sketch · all 7 doc skeletons filled at least with Open Questions |
| `L2` standard (default) | normal baseline on an active project | `git churn` heatmap · dependency surface · existing sensors mapped · canonical exemplar per convention · internal-framework section with owner · runtime view for the single most critical flow |
| `L3` deep | high-stakes (security · regulatory · taking over an unfamiliar legacy) | AST/LSP module-graph extraction · public-API surface enumerated · DB schema reverse-engineered · IaC inventory · incident history & bus-factor analysis · arc42 quality scenarios · all how-to recipes complete |

Invoke as:

```text
/hx-baseline                # default L2
/hx-baseline --depth L1     # quick survey
/hx-baseline --depth L3     # deep investigation
```

The playbook records the tier at the top of each generated doc, runs a *Coverage self-audit* before exit, and refuses to declare done if any audit row falls below the chosen tier. See `.harness/playbooks/10-baseline.md` for the full per-doc methodology and the five-lens investigation toolbelt (static structure · historical · quality · domain triangulation · non-code triangulation).

## Flow Levels

Flow levels control how much ceremony each change goes through. Sensors
(`verify`, `review`) run at ALL levels — only the planning commands scale.

### Quick

For bug fixes, typos, and small scoped changes.

```
propose → implement → verify → review
```

4 commands. Minimal overhead. The fix is still proposed and reviewed, but
there's no separate design or planning phase.

### Standard (default)

For features and non-trivial changes.

```
propose → clarify → design → implement → verify → review → archive
```

7 commands. Adds clarification, design, and post-merge knowledge refresh.
Most day-to-day work uses this level.

### Full

For significant features, refactors, and architectural changes.

```
propose → clarify → design → plan → tasks → analyze → implement → verify → review → archive
```

10 commands. Adds detailed planning, TDD-ordered task breakdown, and the
`analyze` cross-artifact consistency gate. Use when the blast radius is
large.

### Epic

For multi-change initiatives spanning multiple cycles.

```
propose → [multiple W1 cycles] → review → archive
```

Orchestrates multiple standard/full cycles under a single initiative. Each
sub-change follows its own flow level.

Call `/hx-next` any time you're unsure which level fits — it suggests one
based on current state.

## Project Profiles

### Brownfield (default)

For existing codebases with established conventions.

- `AGENTS.md` emphasizes respecting existing patterns
- `/hx-constitution` includes a third "de-facto patterns" source — principles inferred from the codebase
- `/hx-baseline` builds the 7-doc knowledge base from real code (with `path:line` citations)

### Greenfield

For new projects starting from scratch.

- `AGENTS.md` emphasizes architecture-first design
- `/hx-constitution` synthesizes from universal SDD + principle packs only (no de-facto layer yet)
- `/hx-baseline` defines target architecture rather than analyzing existing code

```bash
harness init --profile greenfield --agent claude
```

## Presets

Presets add additional constraints and workflow modifications.

### trunk-based

Optimized for trunk-based development with short-lived branches.

```bash
harness init --preset trunk-based
```

- Changes are small and merge-ready
- No long-lived feature branches
- Verification runs on every commit via pre-commit + CI

### ddd

Domain-Driven Design emphasis.

```bash
harness init --preset ddd
```

- Design playbook emphasizes bounded contexts and ubiquitous language
- Glossary doc (`.harness/knowledge/glossary.md`) is treated as canonical

### secure

Enhanced security gates.

```bash
harness init --preset secure
```

- `/hx-review` adds a security checkpoint
- Dependency vulnerability scanning is added to `verify.sh`
- Sensitive-data handling checks added to the review playbook

Presets can be combined:

```bash
harness init --preset trunk-based --preset secure
```

## Spec Layout

Per-change artifacts live at the repo root in a flat directory structure
(spec-kit flat convention):

```
specs/
├── 001-fix-login/
│   ├── proposal.md
│   ├── clarify.md
│   └── ...
├── 002-scheduled-dispatch/
│   ├── proposal.md
│   ├── design.md
│   └── tasks.md
└── 003-monitoring/
    └── ...
```

There is no separate `archive/` tree — git history is the audit trail.
After `/hx-archive`, the spec directory stays in place and serves as the
permanent record of the change.

## Incremental Agent Setup

Add agents to an existing harness project without regenerating the brain.

```bash
# Initial setup with Claude
harness init --agent claude

# Later, add Codex
harness init --agent codex

# Cursor / Copilot / Gemini are extensible via the registry — not bundled by default
```

Each call:
1. Detects the existing `.harness/` configuration
2. Adds only the new agent's adapter layer
3. Updates `config.toml` with the new agent
4. Preserves all existing files

Use `--force` if you need to re-render the brain on top of an existing
install (e.g., after a harness upgrade).

## Dry Run

Preview everything harness would generate without writing any files.

```bash
harness init --agent claude --dry-run
```

Output shows each file that would be created. Useful for understanding the
generated structure before committing to it.

## Force Overwrite

Regenerate the brain on top of an existing install.

```bash
harness init --agent claude --force
```

Use with caution — this overwrites manual edits under `.harness/`,
`AGENTS.md`, `CLAUDE.md`, `.claude/commands/`, the CI workflows, and the
pre-commit config. Typically only needed after a harness version upgrade.

## Customizing Playbooks

After initialization, playbooks in `.harness/playbooks/` are yours to edit.
Each playbook has this structure (design v3):

```markdown
---
name: hx-command-name
phase: bootstrap | change | review | steer
flow: [quick, standard, full, epic]
---
# /hx-command-name

## Purpose
What this command achieves.

## Prerequisites
What must be true before running.

## Inputs
What the agent reads from disk or the user.

## Steps
Numbered procedure the agent follows.

## Outputs
Files and artifacts produced.

## Exit Criteria
How to know the command succeeded.

## Gate
What MUST be true before downstream commands proceed.

---

## Appendix A — T_NN template
Embedded delivery artifact template (T1 constitution seed, T9 progress
log seed, etc.). Use these verbatim when bootstrapping the corresponding
output file.
```

Common customizations:
- **Add steps** to the `## Steps` section for project-specific procedures
- **Modify Gates** to enforce project-specific quality bars
- **Override the embedded T_NN template** in Appendix A to fit your team's preferred format

## Customizing the Constitution

`.harness/memory/constitution.md` defines your engineering principles. Run
`/hx-constitution` once to generate it from the three-source synthesis
(universal SDD + `.harness/principle-packs/` + de-facto patterns).

Each principle should be tagged:

- `[enforceable]` — a hard gate; `/hx-review` and `/hx-analyze` MUST fail on violation
- `[inferential]` — a judgement call; advisory only

Example:

```markdown
## 4. Database Safety  [enforceable]
All schema changes must be backward-compatible. No column drops without
a migration period. All migrations must be reversible.
**Why**: We've had two incidents from irreversible schema changes.

## 5. API Stability  [inferential]
Public API changes should follow a deprecation period of at least one release.
**Why**: External consumers depend on our API contracts.
```

The constitution is loaded by `/hx-analyze` and `/hx-review` and gates them.

## Verify Script Customization

`.harness/scripts/sh/verify.sh` auto-detects your stack and runs the
appropriate pipeline. Two modes:

- **`--fast`** — lint + typecheck only (used by pre-commit hooks)
- **default** — lint + typecheck + tests + test-honesty (used by CI and `/hx-verify`)

The same script is invoked by:
- Editor hooks (`.claude/hooks/`, if you wire them up)
- Pre-commit (`.pre-commit-config.yaml`)
- GitLab CI (`.gitlab-ci.yml`)

Pipeline order is strict: **lint → typecheck → tests → honesty**. Fast checks
run first, slow checks last.

To customize, edit `verify.sh` directly — for example, adding a security
scan after the test stage. **Never** weaken a check (skip a test, lower a
threshold, add `type: ignore`) to make it pass; doing so is forbidden by the
constitution and caught by `/hx-review`.

## Adapter Registry

`.harness/registry.toml` describes each agent's capabilities:

```toml
[adapters.claude]
type            = "cli"
config_dir      = ".claude"
context_file    = "CLAUDE.md"
commands_dir    = ".claude/commands"
command_format  = "/hx-{cmd}"
templates_dir   = "claude"

[adapters.claude.capabilities.slash_commands]
supported   = true
required    = false
degradation = "Reference playbooks directly from CLAUDE.md / AGENTS.md."

[adapters.claude.capabilities.hook]
supported   = true
required    = false
degradation = "Fall back to pre-commit + CI verify."
```

Capability matrix (§14.7):

| Capability | Meaning |
|---|---|
| `slash_commands` | Native `/hx-<cmd>` invocation |
| `subagent` | Can dispatch sub-tasks to fresh sessions |
| `hook` | Hooks into save / commit / test events |
| `context_import` | Supports cross-file imports (e.g. Claude's `@AGENTS.md`) |
| `mcp` | Model Context Protocol tool access |
| `file_attach` | Can attach files to the prompt |

Each capability has `supported`, `required`, and `degradation` — the
degradation strategy describes how a playbook should fall back when an
agent doesn't support a given capability.

## Multi-Agent Workflow Patterns

### Primary + Secondary Agent

Use Claude Code for architecture and design, Codex for batch implementation:

```bash
# Claude handles W0 bootstrap and design
/hx-constitution
/hx-baseline
/hx-design

# Codex handles batch implementation from the design specs
/hx-implement
/hx-verify
```

Both use the same `/hx-<cmd>` surface.

### Parallel Agent Work

Multiple agents can work on different changes simultaneously because specs
are file-based and isolated by directory:

```
specs/
├── 001-auth-refactor/        # Agent A working on this
├── 002-add-monitoring/       # Agent B working on this
└── 003-fix-scheduler/        # Agent C working on this
```

Agents read the shared `.harness/knowledge/` for context but write only to
their own `specs/<NNN>-<slug>/` directory.

## Directory Structure Reference

Complete directory structure after `harness init --agent claude --agent codex`:

```
project-root/
├── .harness/                          # Brain (tool-neutral)
│   ├── config.toml                    # User-facing settings
│   ├── registry.toml                  # Adapter capability matrix
│   ├── playbooks/                     # 14 command playbooks
│   │   ├── 00-constitution.md
│   │   ├── 10-baseline.md
│   │   ├── 12-next.md
│   │   ├── 30-propose.md
│   │   ├── 31-clarify.md
│   │   ├── 32-design.md
│   │   ├── 33-plan.md
│   │   ├── 34-tasks.md
│   │   ├── 35-analyze.md
│   │   ├── 40-implement.md
│   │   ├── 41-verify.md
│   │   ├── 50-review.md
│   │   ├── 51-archive.md
│   │   └── 90-doctor.md
│   ├── scripts/sh/
│   │   ├── verify.sh                  # Single deterministic sensor
│   │   └── lib/common.sh
│   ├── memory/                        # L-RULE
│   │   └── constitution.md            # (lazy, created by /hx-constitution)
│   ├── knowledge/                     # L-STATE
│   │   ├── product.md                 # (lazy, created by /hx-baseline)
│   │   ├── architecture.md
│   │   ├── tech-stack.md
│   │   ├── business.md
│   │   ├── conventions.md
│   │   ├── glossary.md
│   │   ├── setup-and-verify.md
│   │   ├── how-to/                    # (lazy)
│   │   └── adr/                       # (lazy, created by /hx-plan)
│   ├── principle-packs/
│   │   └── generic.md                 # Seed pack; add more under this dir
│   ├── evals/
│   │   └── README.md                  # Sample format for /hx-doctor
│   └── templates/                     # Project-local overrides (optional)
├── AGENTS.md                          # T13: shared agent contract
├── CLAUDE.md                          # T14: @AGENTS.md + Claude-specific
├── .claude/
│   ├── commands/                      # 14 /hx-* slash commands
│   ├── hooks/                         # (empty; wire up if you want)
│   └── settings.json                  # Permissions for .harness/**, etc.
├── .codex/
│   └── commands/                      # 14 /hx-* slash commands
├── .gitlab-ci.yml                     # MR pipeline (verify + review) + scheduled drift
├── .pre-commit-config.yaml            # Calls verify.sh --fast
├── .agent/
│   └── progress.md                    # (lazy, created by /hx-implement)
└── specs/                             # (lazy, created by /hx-propose)
    └── <NNN>-<slug>/
        ├── proposal.md
        ├── clarify.md
        ├── design.md
        ├── plan.md
        ├── tasks.md
        └── analyze.md
```

## Migrating from v1

If you have a project on the v1 layout (`harness-artifacts/`, root
`memory/constitution.md`, `.claude/skills/`, etc.), design v3 deliberately
does **not** migrate it for you. Instead:

1. `harness doctor` will flag legacy paths as a non-blocking warning
2. Re-run `harness init --force` to drop the v2 footprint alongside
3. Manually move content from `memory/constitution.md` → `.harness/memory/constitution.md`
4. Manually move any `harness-artifacts/changes/<id>/` content into
   `specs/<NNN>-<slug>/` (numbering is up to you)
5. Delete the legacy directories once you've ported anything you want to keep

The legacy paths are intentionally surfaced (not auto-deleted) so you can
review them before discarding.
