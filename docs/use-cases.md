# Use Cases

Real-world scenarios showing how harness structures AI-assisted engineering work.

## Scenario 1: Bug Fix (Quick Flow)

A bug report comes in: "Users can't log in after password reset."

**Flow level**: `quick` — fix is scoped, no separate design needed.

```
/hx-propose       # Create specs/NNN-fix-login/proposal.md
/hx-implement     # Agent fixes the bug following the proposal
/hx-verify        # Lint → typecheck → tests → honesty
/hx-review        # Self-review against the proposal
```

What harness adds:
- The fix is **proposed before coded** — even for a bug fix, the agent writes down what it plans to change
- `verify` is **not optional** — it runs at every flow level
- A lightweight review compares the implementation against the proposal

### Example output

```
specs/
└── 001-fix-login-after-reset/
    └── proposal.md
.agent/
└── progress.md                # Row appended after each task
```

After `/hx-review` returns `ship` and the change is merged, run `/hx-archive`
to refresh affected knowledge docs and validate references.

## Scenario 2: New Feature (Standard Flow)

Product wants a "scheduled dispatch" feature added to the system.

**Flow level**: `standard` — needs clarification and design, but not a full architectural review.

```
/hx-propose       # Write the feature proposal
/hx-clarify       # Multi-round questions, resolve ambiguities
/hx-design        # AI-friendly design with REQ/NFR/IF/DEC/RISK/Q IDs
/hx-implement     # Build it task by task (TDD ordering)
/hx-verify        # Full verification pipeline
/hx-review        # Correctness/consistency + Google/Alibaba code review
/hx-archive       # Refresh knowledge docs, run reference validator
```

What harness adds:
- **Clarify before design** — independent multi-round playbook; questions and answers are recorded in `clarify.md`
- **Design uses stable IDs** — REQ-NNN / NFR-NNN / IF-NNN / DEC-NNN / RISK-NNN / Q-NNN — so tasks and review can trace back to requirements
- **Archive refreshes knowledge** — affected docs in `.harness/knowledge/` are rewritten to reflect the merged code; no separate "fold delta" step

### Example output

```
specs/
└── 002-scheduled-dispatch/
    ├── proposal.md
    ├── clarify.md
    └── design.md

.harness/knowledge/
├── architecture.md            # Updated by /hx-archive
└── adr/
    └── 0007-scheduler-cron-format.md   # Created by /hx-plan if needed

.agent/progress.md             # Closed-out row appended by /hx-archive
```

## Scenario 3: Large Refactor (Full Flow)

Tech lead decides to migrate from a monolithic service layer to domain-driven design modules.

**Flow level**: `full` — requires analysis, detailed planning, and phased implementation.

```
/hx-propose       # Scope the refactoring
/hx-clarify       # Align on boundaries, migration strategy
/hx-design        # Domain model, module boundaries, interface contracts
/hx-plan          # Sequencing + ADRs for each significant decision
/hx-tasks         # TDD-ordered, user-story-grouped, [P] parallel markers
/hx-analyze       # Cross-artifact consistency: constitution ↔ knowledge ↔ proposal ↔ design ↔ tasks
/hx-implement     # Execute one task at a time
/hx-verify        # Verify after each task (not just the end)
/hx-review        # Full review with constitution check
/hx-archive       # Update knowledge + ADRs, run reference validator
```

What harness adds:
- **Plan and tasks** — large work is broken into ordered tasks before implementation starts; `[P]` markers identify safely-parallel tasks
- **Analyze gates implement** — `/hx-implement` MUST NOT run with any unresolved CONFLICT or GAP from `/hx-analyze`
- **Rollback / circuit-breaker** — if implementation reveals an upstream flaw (wrong design, missing requirement), `/hx-implement` flows back to `/hx-clarify` / `/hx-design` rather than patching forward; if `/hx-verify` fails three times in a row with no progress, it halts and asks for human input

## Scenario 4: Brownfield Onboarding

A new team member (or a new AI agent) joins an existing project.

```bash
harness init --agent claude --profile brownfield
```

```
# In the agent session:
/hx-constitution   # Synthesize principles from universal + packs + de-facto patterns
/hx-baseline       # Build the 8-doc knowledge base from real code (with path:line citations)
/hx-next           # Get a routing suggestion for the first real change
```

After W0 bootstrap:
- Engineering principles are documented in `.harness/memory/constitution.md`, each tagged `[enforceable]` or `[inferential]`
- The 8 knowledge docs under `.harness/knowledge/` give every agent the same grounded mental model of the codebase
- The agent can now follow the same workflow as every other team member / agent

## Scenario 5: Multi-Agent Team

The team uses Claude Code for complex architecture work and Codex CLI for batch tasks.

```bash
# Initial setup with Claude
harness init --agent claude

# Later, add Codex support
harness init --agent codex
```

Both agents share:
- The same `AGENTS.md` contract (CLAUDE.md imports it via `@AGENTS.md`)
- The same `.harness/memory/constitution.md` principles
- The same `specs/` and `.harness/knowledge/` directories
- The same `.harness/scripts/sh/verify.sh` script

Each agent gets:
- The same `/hx-<cmd>` command surface in its own commands directory (`.claude/commands/` vs `.codex/commands/`)
- Capability-appropriate behavior — `.harness/registry.toml` declares each agent's support for slash_commands / subagent / hook / context_import / mcp / file_attach, with a `degradation` strategy when a capability is missing (e.g., Codex has no hooks, so verify falls back to pre-commit + CI)

## Scenario 6: Greenfield Project

Starting a new project from scratch.

```bash
mkdir my-new-service
cd my-new-service
harness init --agent claude --profile greenfield
```

The `greenfield` profile:
- Emphasizes architecture-first framing in `AGENTS.md`
- `/hx-constitution` synthesizes principles from packs + intent (no de-facto patterns yet)
- `/hx-baseline` defines target architecture rather than analyzing existing code

## Scenario 7: CI/CD Integration

`harness init` already drops `.gitlab-ci.yml` plus a pre-commit config — both
call the same `verify.sh`:

```yaml
# .gitlab-ci.yml (excerpt, generated at init)
stages: [fast-verify, verify, review, scheduled-drift]

verify:
  stage: verify
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  script:
    - bash .harness/scripts/sh/verify.sh
```

The same script is invoked by:
- Editor hooks (`.claude/hooks/`)
- Pre-commit (`.pre-commit-config.yaml`, `--fast` mode: lint + typecheck only)
- GitLab CI (`.gitlab-ci.yml` MR pipeline, full mode)

No two sensors can disagree about whether the build is green.

The `scheduled-drift` stage runs on a scheduled pipeline (default daily) and is
the place to wire in the reference validator and knowledge ↔ code drift checks.

## Scenario 8: Self-Check the Harness

```
/hx-doctor
```

The doctor playbook (the `/hx-doctor` command, distinct from the
`harness doctor` CLI) is the W3 Steer sensor — it audits the harness mechanism
itself:

- **Rule ↔ guardrail sync** — every constitution principle should be referenced by at least one playbook step, lint rule, arch-test, or review check
- **Budgets** — `AGENTS.md < 32 KiB`, constitution ≤ one screen of principles
- **Drift indicators** — `.harness/knowledge/architecture.md` vs real module graph; constitution `[enforceable]` clauses vs lint/arch-test coverage
- **Reference validator** — every `path:line` citation in knowledge + active specs resolves
- **Eval regression gate** — re-runs `.harness/evals/` samples; any regression on a `.harness/**` or `AGENTS.md` change blocks
- **Legacy layout warning** — flags leftover `harness-artifacts/` or root `memory/` from v1
