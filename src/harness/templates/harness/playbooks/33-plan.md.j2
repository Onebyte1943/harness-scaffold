---
name: hx-plan
phase: change
flow: [standard, full, epic]
---
# /hx-plan

## Purpose

Translate proposal / design into an **executable plan** plus formal
**ADRs** for every significant or hard-to-reverse decision.

## Prerequisites

- `specs/<NNN>-<slug>/proposal.md` exists.
- For `full`+ flows: `design.md` exists and is approved.

## Inputs

- `specs/<NNN>-<slug>/proposal.md` and (if present) `design.md`.
- `.harness/knowledge/` — current architecture and tech stack.
- `.harness/memory/constitution.md` — `[enforceable]` clauses are hard
  constraints.
- `.harness/knowledge/adr/` — existing ADRs (do not contradict without
  superseding).

## Steps

1. **Select technical path.** Identify approaches, weigh trade-offs,
   choose. Capture rejected alternatives — they are first-class content.
2. **Map module change points.** For each touched module, list the
   nature of the change and the dependency direction.
3. **Plan migration / rollback / canary** for any risky transition
   (schema, public API, runtime). State the rollback trigger and procedure.
4. **List risks and trade-offs.** Each risk gets `RISK-NNN`, severity,
   mitigation, owner.
5. **Identify decisions worth an ADR.** Significant trade-off, reversed
   default, irreversible cost, cross-module impact — all qualify.
6. **For each ADR**: assign next sequential `NNNN`, write under
   `.harness/knowledge/adr/NNNN-<slug>.md` using *Appendix B* (MADR /
   Nygard schema). Rejected alternatives are mandatory.
7. **Write `specs/<NNN>-<slug>/plan.md`** using *Appendix A*. Plan must
   reference every ADR by ID.
8. **Coverage check** — every design element has a plan item.

## Outputs

- `specs/<NNN>-<slug>/plan.md`.
- One or more `.harness/knowledge/adr/NNNN-<slug>.md`.

## Exit Criteria

- Plan covers every design element.
- Each significant decision has an ADR.
- Migration / rollback specified for risky steps.
- Plan approved (human or `/hx-analyze`).

## Gate

`/hx-tasks` MUST NOT run until plan is approved and every flagged
decision has an ADR.

---

## Appendix A — plan.md template (T6)

> Provenance
> - Authoritative paradigm: spec-kit plan + MADR-style decision records
> - Investigation protocol: read design + `.harness/knowledge/` to choose the technical path; every significant or hard-to-reverse decision spawns an ADR; migration / rollback / canary mandatory for risky transitions (schema · public API · runtime)
> - Output form: plan sections — Technical path · Module change points · Migration / rollback · Risks (RISK-NNN with severity + mitigation + owner) · Decisions (each linked to an `adr/NNNN-*.md`)

```markdown
# Implementation Plan — ⟨change⟩

## Technical path / choices
⟨approach; key decisions → ADR references⟩

## Module change points
⟨files / modules + nature of change⟩

## Migration / rollback
⟨data migration · compatibility · canary · rollback trigger and procedure⟩

## Risks & trade-offs
- RISK-001 ⟨…⟩ — severity ⟨low|med|high⟩ — mitigation ⟨…⟩ — owner ⟨…⟩

## Decisions
- DEC-001 → `.harness/knowledge/adr/NNNN-⟨slug⟩.md`
```

## Appendix B — ADR template (T8, MADR / Nygard)

> Provenance
> - Authoritative paradigm: Nygard ADR + MADR — **rejected alternatives are first-class content**, not an afterthought
> - Investigation protocol: capture the decision *at the time it is made*; document context · drivers · considered options · chosen option with reasoning · cross-link to the design `DEC-NNN` and plan `RISK-NNN` this ADR answers
> - Output form: standard ADR sections (Context · Decision Drivers · Considered Options · Decision Outcome · Consequences · Rejected Alternatives) + YAML frontmatter (`status` / `date` / `deciders` / `consulted` / `informed`)

```markdown
---
status: proposed | accepted | superseded
date: ⟨YYYY-MM-DD⟩
deciders: ⟨…⟩
consulted: ⟨…⟩
informed: ⟨…⟩
---
# NNNN. Use ⟨X⟩ for ⟨Y⟩

## Context and Problem Statement
⟨situation / problem / tension⟩

## Decision Drivers (optional)
⟨criteria any option must meet⟩

## Considered Options
- ⟨option A⟩
- ⟨option B⟩

## Decision Outcome
Chose ⟨option A⟩ because ⟨…⟩.

## Consequences
- Positive: ⟨…⟩
- Negative: ⟨…⟩
- Follow-ups: ⟨…⟩

## Rejected Alternatives
- ⟨option B⟩ — rejected because ⟨…⟩
```
