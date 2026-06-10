---
name: hx-tasks
phase: change
flow: [standard, full, epic]
---
# /hx-tasks

## Purpose

Decompose the plan into **right-sized, self-contained, TDD-ordered tasks**
grouped by user story, with file paths and parallelism flags.

## Prerequisites

- `specs/<NNN>-<slug>/plan.md` approved.
- (Recommended) `design.md` for REQ-ID references.

## Inputs

- `specs/<NNN>-<slug>/plan.md`.
- `specs/<NNN>-<slug>/design.md` (REQ-IDs for acceptance traceability).
- `.harness/knowledge/architecture.md` — module sizing constraints.

## Steps

1. **Group by user story.** A user story is one observable outcome the
   user gets.
2. **Decompose** each story into the smallest **independently verifiable**
   tasks. Right-sized = one focused session each.
3. **Required fields per task**: ID, what to build, file path(s),
   REQ-ID(s) for acceptance, dependencies.
4. **Order TDD-style**: test task BEFORE the implementation task it
   covers.
5. **Mark `[P]`** on tasks that can run in parallel. Parallel ⇔ no
   shared mutable state and decoupled modules (per §11).
6. **Coverage check** — every REQ has at least one task; no dangling
   plan item.
7. **Cycle check** — no circular dependencies.
8. **Write `specs/<NNN>-<slug>/tasks.md`** (human narrative) using
   *Appendix A*.
9. **Write `specs/<NNN>-<slug>/feature_list.json`** (machine truth)
   using *Appendix B*. Both files MUST agree on task IDs;
   `harness doctor` checks parity. The JSON is what `/hx-implement`,
   `harness state`, and the agent's done check read at runtime —
   tasks.md is for humans.

## Outputs

- `specs/<NNN>-<slug>/tasks.md` — ordered, story-grouped task list.
- `specs/<NNN>-<slug>/feature_list.json` — machine-readable state
  (one entry per task, `status: "not-started"`, `evidence: ""`).

## Exit Criteria

- Every task self-contained (an agent can pick one without reading the rest).
- Every REQ covered.
- Tests precede implementations.
- No cycles.
- `[P]` only on truly decoupled tasks.

## Gate

`/hx-implement` runs against this file. Re-run `/hx-tasks` if scope
changes mid-flight.

---

## Appendix A — tasks.md template (T7)

> Provenance
> - Authoritative paradigm: spec-kit tasks (grouped by user story · `[P]` parallelism flag · file paths · TDD ordering)
> - Investigation protocol: derive from `plan.md` + `design.md`; every REQ-NNN covered by at least one test task **before** an implementation task; `[P]` only when truly decoupled (no shared mutable state, no module overlap) per §11; cycle-check the dependency graph
> - Output form: checkbox list grouped by user story (US-1, US-2, …); each task = ID + brief + file path(s) + REQ-ID + dependencies; tests precede implementations

```markdown
# Tasks — ⟨change⟩

## User story US-1 ⟨name⟩
- [ ] T1.1 [P] write test — covers REQ-001 — `tests/<area>/test_<unit>.py`
- [ ] T1.2 implement — `src/<area>/<file>.py` — depends on T1.1
- [ ] T1.3 e2e verify — exercise the real user path

## User story US-2 ⟨name⟩
- [ ] T2.1 [P] write test — covers REQ-002 — `tests/…`
- [ ] T2.2 implement — `src/…` — depends on T2.1

# Legend
# [P] = parallelizable (no shared mutable state, decoupled module)
# Each task: file path + REQ-ID + dependencies. Test-first.
```

---

## Appendix B — feature_list.json template (Subsystem 2 — State)

> Provenance
> - Authoritative paradigm: Anthropic *Effective Harnesses for Long-Running Agents* (2026) + walkinglabs harness-creator — JSON state is the contract because models are less likely to inappropriately edit JSON than Markdown
> - Investigation protocol: one entry per task in tasks.md; `id` MUST match (T1.1 ↔ feat-T1.1); `verification` is the exact command an agent runs before flipping `status` to `passing`; `depends_on` mirrors tasks.md dependencies; agents only flip `status` and write `evidence`, never edit other fields
> - Output form: a single JSON object with `spec_id`, `features` array; statuses `not-started` → `in-progress` → `passing`

```json
{
  "spec_id": "⟨NNN⟩",
  "features": [
    {
      "id": "T1.1",
      "name": "write test for REQ-001",
      "depends_on": [],
      "status": "not-started",
      "evidence": "",
      "verification": "uv run pytest tests/<area>/test_<unit>.py -v"
    },
    {
      "id": "T1.2",
      "name": "implement REQ-001",
      "depends_on": ["T1.1"],
      "status": "not-started",
      "evidence": "",
      "verification": "./init.sh"
    }
  ]
}
```

Hard rules for the agent (also in AGENTS.md § 2.2):

- **MUST NOT** edit `id`, `name`, `verification`, or `depends_on`
  on existing entries.
- **MUST** run `verification` and let it pass before flipping
  `status` from `in-progress` to `passing`.
- **MUST** record proof (commit SHA, test snippet, or `path:line`)
  in `evidence` when flipping to `passing`.
