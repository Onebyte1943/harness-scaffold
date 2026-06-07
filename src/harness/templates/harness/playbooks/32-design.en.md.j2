---
name: hx-design
phase: change
flow: [full, epic]
---
# /hx-design

## Purpose

Produce an **AI-friendly detailed design** — a self-contained, evidence-cited,
stable-ID document that a clean-context agent can read once and implement
without further questions.

## Prerequisites

- `specs/<NNN>-<slug>/proposal.md` exists (or design-first: a tech spec).
- `/hx-clarify` has driven blockers to zero (or this run will surface new ones).

## Inputs

- The proposal + any tech spec / requirement doc.
- `.harness/knowledge/` — for grounding (architecture, conventions, tech).
- `.harness/memory/constitution.md` — `[enforceable]` clauses become hard
  constraints.
- `specs/<NNN>-<slug>/clarify.md` — resolved decisions to fold in.

## Steps

1. **Ingest and ground.** Walk every requirement, citing `path:line` or
   `doc§` evidence for each non-trivial claim.
2. **Write `specs/<NNN>-<slug>/design.md`** using the T5 template in
   *Appendix A*. Honor the 10 attributes:
   - Self-contained · unambiguous & testable (Given/When/Then) · right-sized
     with progressive disclosure (~250 lines per capability) · explicit
     contracts (signatures / OpenAPI / data model / error edges as code blocks) ·
     traceable (REQ ↔ design ↔ test, stable IDs) · machine-parseable
     structure · focused on "what / how to build" · explicit assumptions ·
     sourced (every claim cites or is flagged assumption) · controllable
     blast radius.
3. **Stable IDs**: `REQ-NNN` · `NFR-NNN` · `IF-NNN` · `DEC-NNN` · `RISK-NNN` · `Q-NNN`.
4. **Modules & blast radius.** Apply §11 rules: cohesion-first sizing,
   stable narrow contracts, acyclic dependencies. Run the size self-check.
5. **Surface unresolved items** → trigger `/hx-clarify` rather than guess.
6. **Self-score** against the §12.4 A checklist; iterate until it passes.

## Outputs

- `specs/<NNN>-<slug>/design.md`.
- `specs/<NNN>-<slug>/contracts/` (optional) — OpenAPI / schemas / data models.

## Exit Criteria

- Structure score (§12.4 A) passes.
- Zero `blocker` items in `clarify.md`.
- Every REQ has Given/When/Then acceptance.
- Every IF has a code-block contract.
- Traceability matrix at the end is complete.

## Gate

A clean-context agent must be able to read this design and implement it
**without asking questions**. If not, re-run `/hx-clarify`.

---

## Appendix A — design.md template (T5)

> Provenance
> - Authoritative paradigm: SCOPE (Spec-driven · Contract-first · Observable · Progressive · Evidence-cited) + Agent-Experience design (Addy Osmani) + BDD / Gherkin
> - Investigation protocol: ground every claim against code / knowledge / constraints with `path:line` or `doc§`; stable IDs `REQ-NNN / NFR-NNN / IF-NNN / DEC-NNN / RISK-NNN / Q-NNN` for cross-artifact traceability; unresolved items go back to `/hx-clarify` (do not guess)
> - Output form: self-contained document a clean-context agent can implement without further questions — contracts as code blocks, REQs as Given/When/Then, traceability matrix at the end

```markdown
# Detailed Design — ⟨capability / change⟩
> id: ⟨NNN-slug⟩ · owner: ⟨…⟩ · status: draft|review|approved
> flow: ⟨standard|full|epic⟩ · sources: ⟨doc§ / path:line⟩

## 1 Purpose & Scope · Non-goals
⟨…⟩

## 2 Context & Grounding
⟨related code / knowledge / constraints, each with path:line or doc§⟩

## 3 Functional Requirements
### REQ-001 ⟨name⟩
Given ⟨context⟩
When ⟨action⟩
Then ⟨observable outcome⟩
Example test: ⟨one concrete test case⟩

## 4 Non-functional Requirements
NFR-001 ⟨measurable: latency / throughput / availability / security⟩

## 5 Modules & Boundaries
- Module ⟨A⟩ — responsibility — stable contract — dependency direction
- Blast radius: ⟨files / public symbols this change can touch⟩
- Size self-check: ⟨LOC / public-API symbol counts vs project thresholds⟩

## 6 Interfaces & Data Contracts
### IF-001 ⟨name⟩
```code
⟨signature / OpenAPI / data model / error edges⟩
```

## 7 Design Decisions
- DEC-001 → ADR `.harness/knowledge/adr/NNNN-⟨slug⟩.md`
  - Chosen: ⟨…⟩
  - Rejected: ⟨option + why⟩

## 8 Test Strategy
- Sample test cases (REQ → test name / file).
- Definition of done: ⟨observable user-visible behavior⟩.

## 9 Task Seeds
⟨high-level decomposition, right-sized → /hx-tasks⟩

## 10 Assumptions
⟨explicit, flagged; unconfirmed assumptions become RISK-NNN⟩

## 11 Traceability
| REQ | Design element | Test | Source |
| --- | -------------- | ---- | ------ |
| REQ-001 | §5 / §6 IF-001 | tests/… | path:line / doc§ |
```
