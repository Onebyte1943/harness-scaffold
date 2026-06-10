# Principle Pack — 12-Factor Agents

> Operating principles for production AI agents, distilled from
> HumanLayer's *12-Factor Agents*. Used as one of the synthesis
> sources by `/hx-constitution` when an agent is in the loop —
> particularly relevant when the project ships an agent harness
> itself, or when the team plans to operate agents in production.
>
> Pair with `generic.md`. Use `[enforceable]` when a deterministic
> guardrail can check it; otherwise `[inferential]` so `/hx-review`
> covers it.

> Provenance (T15)
> - Authoritative paradigm: HumanLayer *12-Factor Agents* (humanlayer.dev/blog/12-factor-agents) — production-oriented principles for agent systems modeled after the original 12-Factor App
> - Investigation protocol: every principle is named after its 12-Factor counterpart and tagged for enforceability; this pack is selected automatically when `profile = brownfield` or `vibecode` and may be selected manually otherwise via `/hx-constitution`
> - Output form: compact cards `P-12-N` — **Rule** (imperative) · **Why** (what breaks) · enforceability tag

---

## P-12-1 Natural language to tool calls

- Rule: every prompt that mutates state translates into a typed,
  inspectable tool call before execution. No free-text shell.
- Why: untyped prompts are unreviewable, untestable, and silently
  break under model drift.
- [enforceable: lint]

## P-12-2 Own your prompts

- Rule: prompts are checked-in, versioned source. No ad-hoc strings
  hidden inside agent frameworks.
- Why: prompts are the contract; you cannot debug or A/B-test what
  you cannot see in `git log`.
- [enforceable: arch-test]

## P-12-3 Own your context window

- Rule: explicitly choose what enters the context. Pruning, summarizing,
  and progressive disclosure are first-class operations, not side effects.
- Why: silently overflowing the context window converts a working
  agent into a hallucinating one with no obvious failure signal.
- [inferential]

## P-12-4 Tools are structured outputs

- Rule: tool definitions return structured schemas; never parse free-text
  back into structured fields downstream of the model.
- Why: parsing free-text back is where most "the agent broke" bugs
  actually live.
- [enforceable: lint]

## P-12-5 Unify execution state and business state

- Rule: agent execution state (in-flight tool calls, retries, tokens
  consumed) lives in the same store as business state (the user-visible
  outcome). One source of truth, one transaction.
- Why: dual stores diverge under crashes; the agent then "remembers"
  state the system has already discarded.
- [inferential]

## P-12-6 Launch / pause / resume with simple APIs

- Rule: every long-running agent run can be paused and resumed by ID
  through a single API call. No "rerun from scratch" as the recovery
  path.
- Why: real workloads run for minutes-to-hours; restarting on every
  hiccup makes the system economically unusable.
- [inferential]

## P-12-7 Contact humans with tool calls

- Rule: human escalation is itself a tool call (typed payload, audit
  log, async resume) — not a side-channel email or Slack thread the
  system cannot observe.
- Why: out-of-band human handoff is invisible to evals, traces,
  and rollback.
- [enforceable: arch-test]

## P-12-8 Own your control flow

- Rule: the agent's control flow (which tool runs next, when to give
  up, how to retry) is your code, not a black-box loop in a vendor SDK.
- Why: emergent control flow defeats every other guarantee in this
  pack.
- [enforceable: arch-test]

## P-12-9 Compact errors into context

- Rule: keep useful failures *in* the context window — error message,
  stack frame, the tool call that failed — so the model can recover.
  Discard noise, never the signal.
- Why: stripping errors out forces the next step to repeat the
  mistake; keeping the full transcript wastes tokens.
- [inferential]

## P-12-10 Small, focused agents

- Rule: an agent does one thing and is composed with siblings, not
  loaded with every tool the org owns.
- Why: a 60-tool agent's reliability is the product of 60 selections,
  each of which can be wrong.
- [inferential]

## P-12-11 Trigger from anywhere, meet users where they are

- Rule: the harness is the same whether triggered from the CLI, a
  webhook, a scheduled job, or a Slack message. No "Slack mode."
- Why: branching the harness per surface is how surfaces silently
  diverge in behavior.
- [inferential]

## P-12-12 Make your agent a stateless reducer

- Rule: an agent step is `f(state, event) -> state'`. Statelessness
  in the runtime; durability in the store.
- Why: stateless reducers are the only model where pause / resume /
  replay / parallel-shard all work without re-derivation.
- [enforceable: arch-test]
