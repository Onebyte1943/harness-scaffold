# Harness Eval Samples

> Regression samples drawn from real MRs / issues. Give harness its
> own CI: any mechanism / contract change must rerun these and must
> not regress the gold metrics.

> Provenance (T16)
> - Authoritative paradigm: Anthropic eval-driven self-regression + Böckeler "keep quality left" — the harness is part of CI too
> - Investigation protocol: sample real MRs / issues; replay each sample in a clean-context run; record four gold metrics (first-try-pass · clarify-questions · review must-fix · rework); any change under `.harness/**` or `AGENTS.md` reruns the samples
> - Output form: one file per sample (Input · Expected · Gold metrics baseline · Regression gate); metrics must not regress on a harness change — `/hx-doctor` enforces the gate

---

## How to add an eval

1. Pick a real MR or issue from this repo.
2. Create `evals/<id>.md` using the schema below.
3. Run the eval through a clean-context agent. Record the gold metrics
   under "Gold metrics (baseline)".
4. Commit it. From now on, `/hx-doctor` will rerun it on any change to
   `.harness/**` or `AGENTS.md`.

---

## Sample schema

```markdown
# Eval — ⟨id⟩  (source: MR/issue #⟨…⟩; owner: ⟨…⟩; date: ⟨YYYY-MM-DD⟩)

## Input
⟨The design doc / requirement handed to a clean-context agent.⟩

## Expected
⟨Capability changed + tests that must pass.⟩

## Gold metrics (baseline)
- first-try pass verify: ⟨y/n⟩
- extra clarify questions: ⟨n, ideal 0⟩
- review must-fix: ⟨n⟩
- rework: ⟨est⟩

## Regression gate
Rerun on any change to .harness/** or AGENTS.md. Metrics must not regress.
```
