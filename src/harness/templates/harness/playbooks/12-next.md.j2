---
name: hx-next
phase: routing
flow: [quick, standard, full, epic]
---
# /hx-next

## Purpose

Router. Look at the current state of the change, classify its risk and
size, recommend the next command and the appropriate flow level. Produces
no file output — only a recommendation.

## Prerequisites

- Harness initialized.
- Optional: a `specs/NNN-<slug>/` folder for an in-progress change.

## Inputs

- Active branch name (look for `NNN-<slug>` pattern).
- `specs/NNN-<slug>/` contents (which artifacts exist).
- `git diff --name-only main...HEAD` — changed file count, affected paths.
- `.harness/config.toml` — project default flow.
- `.harness/memory/constitution.md` — `[enforceable]` clauses naming
  sensitive paths (security, public API surface).

## Steps

1. **Detect active change.** If on a `NNN-<slug>` branch with matching
   `specs/NNN-<slug>/`, use that. Otherwise treat as "no active change".
2. **Read State + Lifecycle first.** When an active spec exists, read
   `specs/<NNN>-<slug>/feature_list.json` and (if present)
   `specs/<NNN>-<slug>/session-handoff.md`. The handoff's
   "Next Session Startup" + the next executable feature
   (per `harness state next`) often answer the routing question
   directly — return that before doing flow analysis.
3. **Signal collection**:
   - `n_files = git diff --name-only main...HEAD | wc -l`
   - `touches_public_api` — true if changes hit declared public API surface.
   - `touches_security` — true if changes hit security-sensitive paths
     (auth, crypto, payment, secrets).
   - `req_size` — number of user-facing requirements (from proposal /
     design if present).
4. **Suggest flow level**:
   - `quick` — n_files ≤ 3, no public API, no security, no constitution
     `[enforceable]` impact.
   - `standard` — default; n_files ≤ 20.
   - `full` — touches_public_api OR touches_security OR n_files > 20.
   - `epic` — req_size > 1 capability or spans modules with conflicting
     owners.
5. **Suggest next command** based on what artifacts exist in `specs/NNN/`:
   - none → `/hx-propose` (or `/hx-design` if design-first).
   - proposal only → `/hx-clarify` if ambiguities flagged; else `/hx-design`
     (full+) or `/hx-plan` (standard).
   - design exists, no plan → `/hx-plan`.
   - plan exists, no tasks → `/hx-tasks`.
   - tasks exist, not all done → `/hx-implement` (and run
     `harness state next` to pick the feature).
   - all tasks done → `/hx-verify`, then `/hx-review`, then `/hx-archive`.
6. **Print** the recommendation as: `flow = X · next = /hx-Y · reason = ⟨…⟩`.
   List the signals that drove the choice so the human can override.

## Outputs

- A single recommendation printed to the agent / terminal.
- **No file is written.** The recommendation is advisory.

## Exit Criteria

- The recommendation cites concrete signals (file count, paths,
  enforceable clauses) — not vibes.
- A clear next command is named.

## Gate

None. This is a routing aid, not a gate.

---

## Provenance (T-router)

> Provenance
> - Authoritative paradigm: cc-sdd discovery router + signal-driven flow tailoring (§5.3) — pick the cheapest flow level the signals justify
> - Investigation protocol: read the active branch name for the `NNN-<slug>` pattern, enumerate which artifacts exist under `specs/NNN-<slug>/`, count `git diff --name-only main...HEAD`, detect touches on public API or security-sensitive paths, count user-facing requirements; map signals → flow level (`quick` / `standard` / `full` / `epic`) and → next command (proposal → clarify/design → plan → tasks → implement → verify → review → archive)
> - Output form: a single advisory line `flow = X · next = /hx-Y · reason = ⟨signals⟩` printed to the terminal — no file is written, human may override
