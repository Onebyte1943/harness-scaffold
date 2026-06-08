---
name: hx-archive
phase: review
flow: [quick, standard, full, epic]
---
# /hx-archive

## Purpose

After the change is merged into main, refresh the **project knowledge
base** so it reflects the new code, and run the **reference validator**
so no dangling `path:line` citations remain. There is no separate merge
command — git / GitLab MR handles merging. There is no delta tree to fold in.

## Prerequisites

- The change is merged into main and deployed / verified in the target environment.
- `/hx-review` verdict was `ship`.
- All review must-fix items addressed.

## Inputs

- The merged change at `specs/<NNN>-<slug>/`.
- The new state of the codebase (it is now the source of truth).
- `.harness/knowledge/` (current; about to be refreshed).

## Steps

1. **Confirm the change is live.** Do not archive un-shipped work.
2. **Refresh affected knowledge docs.** For each of the 7 knowledge files,
   update sections impacted by this change so they describe the merged
   code (with `path:line` citations to the new locations):
   - `architecture.md` — modules / boundaries / data flow shifts.
   - `tech-stack.md` — new dependency, new pattern, deprecated usage.
   - `business.md` — only if business invariants actually changed (and
     cross-validated against a non-code source).
   - `conventions.md` — if a new canonical example was introduced.
   - `glossary.md` — if domain terms were added or renamed.
   - `setup-and-verify.md` — if commands or verify path changed.
   - `how-to/*` — refresh or add recipes affected by the change.
   - `product.md` — only if a capability was added / removed.
3. **Run the reference validator.** Every `path:line` and symbol
   citation in the refreshed docs and in `specs/<NNN>-<slug>/` must
   resolve. Failures block archive.
4. **Leave `specs/<NNN>-<slug>/` in place.** No tree move. Git history
   is the audit trail.
5. **Append an entry to `.agent/progress.md`** marking the change closed.

## Outputs

- Updated `.harness/knowledge/` files.
- Closed-out entry in `.agent/progress.md`.
- Reference validator clean.

## Exit Criteria

- Knowledge base reflects the merged code.
- No dangling `path:line` references.
- `specs/<NNN>-<slug>/` is the permanent record of the change.

## Gate

A new change cycle MAY start before archive completes, but the team
SHOULD NOT let unarchived changes accumulate — knowledge staleness
compounds.

---

## Appendix A — archive checklist (T11)

> Provenance
> - Authoritative paradigm: spec-kit "specs ship with the code" + citation fidelity — no delta tree, no separate merge command (GitLab MR handles merging); `specs/<NNN>-<slug>/` stays in place as the permanent record
> - Investigation protocol: only run on merged work; diff the merged code against the 7 knowledge docs and refresh affected sections with new `path:line` anchors; run the reference validator so no dangling citation survives in knowledge or active specs
> - Output form: post-merge checklist (deployed · knowledge refreshed · validator clean · progress.md closed · specs left in place) + a closing row appended to `.agent/progress.md`

```markdown
# Archive — ⟨id⟩  (run after merge to main via GitLab MR)

- [ ] Change deployed / verified
- [ ] Refresh affected `.harness/knowledge/` docs to reflect merged code
- [ ] Run reference validator (no dangling path:line)
- [ ] Append closed entry to `.agent/progress.md`
- [ ] Leave `specs/⟨NNN⟩-⟨slug⟩/` in place (git history = audit)
```
