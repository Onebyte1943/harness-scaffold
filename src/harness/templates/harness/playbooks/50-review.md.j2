---
name: hx-review
phase: review
flow: [quick, standard, full, epic]
---
# /hx-review

## Purpose

Inferential sensor with **two jobs**:
- **A. Correctness & Consistency** — does the implementation match the
  proposal / clarify / design / constitution?
- **B. Code Review** — Google's "What to look for" dimensions plus the
  Alibaba Java Development Manual where applicable. Standard: **code
  health only goes up**.

## Prerequisites

- `/hx-verify` passed on a clean tree.
- `specs/<NNN>-<slug>/` artifacts present (proposal at minimum; design
  for `full`+).

## Inputs

- Code diff (`git diff main...HEAD`).
- `specs/<NNN>-<slug>/{proposal,clarify,design,tasks}.md`.
- `.harness/memory/constitution.md` — `[enforceable]` clauses are
  must-fix gates.
- `.harness/knowledge/conventions.md` — naming / style / patterns.
- `AGENTS.md` — boundaries (Always / Ask / Never).

## Steps

### A. Correctness & Consistency

1. **Coverage** — every REQ-NNN is implemented and has a real test.
   Missing or stubbed → **must-fix gap**.
2. **Design alignment** — implementation matches `design.md` (interfaces,
   data models, behavior). Drift → must-fix or explicit deviation note.
3. **Constitution** — no `[enforceable]` clause is violated. Violation
   → must-fix.
4. **Boundaries** — no AGENTS.md "Never" was crossed. Crossings → must-fix.
5. **Scope** — no work added outside the proposal. Surprise additions
   need approval or removal.

### B. Code Review (Google dims + Alibaba spec)

6. **Design** — right abstractions, fits the system. *Most important.*
7. **Functionality** — does what it claims; edge cases handled.
8. **Complexity** — guard against premature abstraction and speculative generality.
9. **Tests** — verify behavior, not implementation. Did the MR weaken
   or delete tests? → must-fix.
10. **Naming** — clear, consistent, matches `.harness/knowledge/conventions.md`.
11. **Comments** — explain *why*, not *what*.
12. **Style / Consistency** — matches established patterns; tool-enforceable
    items should already be caught by lint (if not, file a doctor finding).
13. **Documentation** — public APIs and READMEs updated where needed.
14. **Context** — review the whole CL, not lines in isolation.
15. **Good things** — call out wins explicitly. Tone matters.
16. **Alibaba spec** (when applicable): naming / constants / OOP / concurrency
    / exception & logging / MySQL / index / security — graded
    **Blocker / Critical / Major**.

### Standards

17. **Code health only goes up.** A CL that lowers health is not
    acceptable even if "it works."
18. **`Nit:` prefix** for non-blocking style / preference items.
19. Must-fix is reserved for: correctness, requirement violation,
    health regression.

### Report

20. Write a structured report using *Appendix A*. Verdict:
    `ship` (no must-fix) or `fix-then-ship`.

## Outputs

- Review report (returned to the agent / posted as MR comment).

## Exit Criteria

- 0 must-fix gaps.
- 0 must-fix code-review findings.
- Code health not degraded.

## Gate

Merge MUST NOT happen with verdict `fix-then-ship`.

---

## Appendix A — review report template (T10)

> Provenance
> - Authoritative paradigm: Google "What to look for in a code review" (Design · Functionality · Complexity · Tests · Naming · Comments · Style · Docs · Context · Good things) + Alibaba Java Development Manual (Blocker / Critical / Major) + Anthropic gap-style review — code health only goes up
> - Investigation protocol: run as an isolated sub-agent against `git diff main...HEAD` with proposal / clarify / design / constitution / conventions in scope; verify every REQ-NNN is implemented with a real test; flag any weakened or deleted test; gaps and findings are flowed back, not merged through
> - Output form: sectioned report — **CORRECTNESS & CONSISTENCY (must-fix)** · **CODE REVIEW (Google dims + Alibaba spec)** · **GOOD** · **VERDICT** (`ship` | `fix-then-ship`); non-blocking items prefixed `Nit:`

```markdown
# Review — ⟨id / MR⟩

## CORRECTNESS & CONSISTENCY (must-fix)
- ⟨path:line⟩ — ⟨what is missing or wrong⟩ — violates ⟨REQ-NNN / clause / boundary⟩

## CODE REVIEW (Google dims + Alibaba spec; Nit: = non-blocking)
- Design: ⟨…⟩
- Functionality / edges: ⟨…⟩
- Complexity / over-eng: ⟨…⟩
- Tests (verify behavior? weakened?): ⟨…⟩
- Naming / Comments / Consistency: Nit: ⟨…⟩
- Alibaba spec (Blocker / Critical / Major): ⟨…⟩

## GOOD
- ⟨…⟩

## VERDICT: ship | fix-then-ship
```
