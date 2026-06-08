---
name: hx-analyze
phase: change
flow: [full, epic]
---
# /hx-analyze

## Purpose

Cross-artifact consistency check. Verify that constitution, knowledge,
proposal, clarify, design, plan, and tasks all agree before any code is
written.

## Prerequisites

- `specs/<NNN>-<slug>/proposal.md`, `design.md`, `plan.md`, `tasks.md`
  all exist.
- `.harness/memory/constitution.md` loaded.

## Inputs

- `.harness/memory/constitution.md` — `[enforceable]` clauses are the
  hard gate.
- `.harness/knowledge/` — for ground-truth checks.
- All `specs/<NNN>-<slug>/*.md`.

## Steps

1. **REQ coverage**: every REQ-NNN in `design.md` is referenced by at
   least one task in `tasks.md` (and one test task).
2. **DEC coverage**: every DEC-NNN points to a real ADR file under
   `.harness/knowledge/adr/`.
3. **Constitution check**: cross-reference every `[enforceable]`
   constitution clause against plan and tasks. Any violation must be
   resolved (re-plan) or explicitly waived (proposal + ratify).
4. **Scope creep**: any task not traceable to a REQ in the proposal/design
   is a creep. Flag.
5. **Knowledge alignment**: claims in design about current architecture
   must match `.harness/knowledge/architecture.md`. If knowledge is wrong,
   open a follow-up to update via `/hx-archive` later.
6. **Conflict scan**: detect any place where two artifacts disagree on
   behavior, interface, or constraint.
7. **Write `specs/<NNN>-<slug>/analyze.md`** — report categorized as:
   - **CONFLICT** (must resolve before implement).
   - **GAP** (must fill before implement).
   - **WARNING** (review; may proceed with rationale).

## Outputs

- `specs/<NNN>-<slug>/analyze.md` — consistency report.

## Exit Criteria

- 0 unresolved CONFLICT.
- 0 unresolved GAP.
- Full traceability matrix: constitution ↔ knowledge ↔ proposal ↔ design ↔ tasks.

## Gate

`/hx-implement` MUST NOT run with any unresolved CONFLICT or GAP.

---

## Appendix A — analyze report block

> Provenance
> - Authoritative paradigm: spec-kit analyze + constitution `[enforceable]` cross-check
> - Investigation protocol: read `.harness/memory/constitution.md` + `.harness/knowledge/` + every `specs/<NNN>-<slug>/*.md`; check REQ coverage, DEC ↔ ADR coverage, constitution clause adherence, scope creep, knowledge alignment, inter-artifact conflicts
> - Output form: three-tier report — **CONFLICT** (must resolve) · **GAP** (must fill) · **WARNING** (may proceed with rationale) — plus a full traceability matrix `REQ ↔ Design ↔ Plan ↔ Task ↔ Test ↔ ADR ↔ Constitution`

```markdown
# Analyze — ⟨id⟩

## CONFLICT (must resolve before implement)
- ⟨artifact A ↔ artifact B⟩ — ⟨what disagrees⟩ — owner ⟨…⟩

## GAP (must fill before implement)
- REQ-NNN / DEC-NNN missing in ⟨tasks / ADR⟩ — owner ⟨…⟩

## WARNING (review, may proceed with rationale)
- ⟨…⟩

## Traceability matrix
| REQ | Design | Plan | Task | Test | ADR | Constitution |
| --- | ------ | ---- | ---- | ---- | --- | ------------ |
```
