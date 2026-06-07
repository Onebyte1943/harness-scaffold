# Security Policy

## Supported versions

Harness is pre-1.0 and ships from `main`. Only the latest tagged
release receives security fixes.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security reports.**

Use GitHub's private vulnerability reporting:
https://github.com/Onebyte1943/harness-scaffold/security/advisories/new

Include:

- A description of the vulnerability and its impact
- Steps to reproduce (or a proof-of-concept)
- The harness version and platform you observed it on
- Whether you would like credit in the eventual advisory

You should hear back within **5 business days**. If the issue is
confirmed, we aim to ship a fix within **30 days** for high-severity
issues. We'll coordinate disclosure timing with you.

## Scope

Harness writes scaffolding files into a project directory and shells
out to `git`. The following are in scope:

- Arbitrary file writes outside the target project directory
- Command injection via `harness init` flags or config values
- Template rendering that leaks secrets from the host environment
- Insecure default permissions on generated files

Out of scope:

- Vulnerabilities in the AI agents harness scaffolds for (report
  those to the agent's vendor)
- Issues that require write access to the user's home directory or
  a malicious `.harness/config.toml` already on disk
