---
name: hx-propose
phase: change
flow: [standard, full, epic]
---
# /hx-propose

## Purpose

Turn a requirement / tech-spec into a **proposal** — why it matters, what
will be built, what's out of scope, blast radius, and source references.
First file in `specs/NNN-<slug>/`.

## Prerequisites

- `/hx-constitution` complete.
- (Recommended) `/hx-baseline` complete so the knowledge base can ground claims.

## Inputs

- The requirement / tech-spec document the user provides.
- `.harness/knowledge/` — to ground the change in current architecture.
- `.harness/memory/constitution.md` — for inviolable constraints.

## Steps

1. **Pick the next NNN.** Scan `specs/` for the highest existing
   `NNN-` prefix and increment. Slug the change name (kebab-case,
   ≤ 30 chars).
2. **Create the spec folder.** `mkdir -p specs/<NNN>-<slug>/`.
3. **Create matching branch.** `git checkout -b <NNN>-<slug>` (skip if
   already on it). The branch and folder share the prefix so every
   later command can identify the active change.
4. **Write `specs/<NNN>-<slug>/proposal.md`** using *Appendix A*. Each
   section is required; "Sources" must list `path:line` or `doc§`
   references for every non-trivial claim.
5. **Stop at the gate.** Print the proposal and wait for human approval
   before any further command runs.

## Outputs

- `specs/<NNN>-<slug>/proposal.md` — single proposal file.

## Exit Criteria

- Scope is clear and reviewable (≤ 1 screen).
- Non-goals are stated explicitly.
- Every claim has a source.

## Gate

Proposal must be approved by a human before `/hx-clarify`, `/hx-design`,
or `/hx-plan` runs.

---

## Appendix A — proposal.md template (T3)

> Provenance
> - Authoritative paradigm: OpenSpec proposal (no diff/delta — only direction)
> - Investigation protocol: read the requirement / tech-spec doc + locate impact in `.harness/knowledge/architecture.md`; every non-trivial claim cites `path:line` or `doc§`; defer detail to `/hx-design`
> - Output form: a one-screen proposal with five sections — Why · What · Non-goals · Impact · Sources; reviewable by a human in under two minutes

```markdown
# Proposal — ⟨title⟩   (id: NNN-⟨slug⟩, flow: standard|full|epic)

## Why
⟨motivation, user value, business reason⟩

## What
⟨scope in one paragraph⟩

## Non-goals
⟨what is explicitly out of scope⟩

## Impact
⟨capabilities / modules touched · blast radius · breaking changes⟩

## Sources
⟨requirement / tech-spec links · path:line citations⟩
```
