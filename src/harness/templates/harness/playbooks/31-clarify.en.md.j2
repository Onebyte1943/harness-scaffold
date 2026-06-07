---
name: hx-clarify
phase: change
flow: [standard, full, epic]
---
# /hx-clarify

## Purpose

Resolve every ambiguity that would block implementation. Independent and
**repeatable** — can run after `/hx-propose`, after `/hx-design`, or
between iterations until no blocker remains.

## Prerequisites

- Active change folder exists at `specs/<NNN>-<slug>/`.
- At least one of `proposal.md` or `design.md` is present.

## Inputs

- `specs/<NNN>-<slug>/proposal.md` (if present).
- `specs/<NNN>-<slug>/design.md` (if present).
- `.harness/knowledge/` for ground truth.
- `.harness/memory/constitution.md` for the rules.

## Steps

1. **Scan** the proposal/design for ambiguity, conflict, missing detail,
   implicit assumption.
2. **Generate clarification items.** Each item has: open question, why it
   blocks, options, suggested default, source citation, severity
   (`blocker | assumption`).
3. **Append to `clarify.md`** using *Appendix A*. Never overwrite — each
   round appends a new block so the history of asks is preserved.
4. **Wait for human.** They mark resolutions inline (who · date · decision).
5. **Loop.** If new ambiguity surfaces, re-run this command. Drop
   "assumption" items into `design.md` Assumptions section.

## Outputs

- `specs/<NNN>-<slug>/clarify.md` — cumulative Q&A log.

## Exit Criteria

- Zero `blocker`-severity items remain unresolved.
- Every resolution row has a decider and date.

## Gate

`/hx-implement` MUST NOT run while any `blocker` is open.

---

## Appendix A — clarify.md template (T4)

> Provenance
> - Authoritative paradigm: spec-kit clarify (independent, repeatable across rounds)
> - Investigation protocol: scan proposal / design for ambiguity, conflict, missing detail, implicit assumption; for each item record `source` citation and `severity` (`blocker` vs `assumption`); never overwrite — append a new dated round
> - Output form: cumulative Q&A table per round (Q-ID · open point · why blocking · options · suggested default · source · severity · resolution who/date/decision); `blocker` count must reach zero before `/hx-implement`

```markdown
# Clarifications — ⟨id⟩

> Append each round. Newest last. Blockers MUST reach zero before /hx-implement.

## Round 1 — ⟨YYYY-MM-DD⟩

| Q-ID | Open point | Why blocking | Options | Suggested default | Source | Severity | Resolution(who/date/decision) |
| ---- | ---------- | ------------ | ------- | ----------------- | ------ | -------- | ----------------------------- |
| Q001 | ⟨…⟩ | ⟨…⟩ | A / B | A | doc§ / path:line | blocker | ⟨…⟩ |
| Q002 | ⟨…⟩ | ⟨…⟩ | … | … | … | assumption | ⟨…⟩ |

## Round 2 — ⟨YYYY-MM-DD⟩

| Q-ID | … | … | … | … | … | … | … |
```
