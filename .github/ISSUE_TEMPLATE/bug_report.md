---
name: Bug report
about: Something doesn't work as documented
title: ""
labels: bug
---

## What happened

<!-- A clear, terse description of what went wrong. -->

## What you expected

<!-- What did you think would happen instead? -->

## Reproduction

<!-- The smallest sequence of commands that reproduces this — ideally
     against a fresh `harness init` in a temp directory. -->

```bash
mkdir /tmp/repro && cd /tmp/repro
harness init
# ...
```

## Environment

- Harness version: <!-- `harness --version` -->
- Python version: <!-- `python --version` -->
- OS: <!-- e.g. macOS 14.5, Ubuntu 22.04, Windows 11 -->
- Agent (if relevant): <!-- claude / codex / cursor / ... -->

## Logs / traceback

<!-- Paste the full output. If long, attach as a file or collapse
     in a <details> block. -->

```
<paste here>
```
