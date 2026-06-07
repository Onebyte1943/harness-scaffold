"""Canonical directory layout and command/playbook mapping (design v3).

Single source of truth for every path the scaffold writes or reads.
"""

from __future__ import annotations

# Brain (L-MECH) — tool-neutral mechanism
HARNESS_DIR = ".harness"
PLAYBOOKS_DIR = f"{HARNESS_DIR}/playbooks"
SCRIPTS_DIR = f"{HARNESS_DIR}/scripts"
MEMORY_DIR = f"{HARNESS_DIR}/memory"
KNOWLEDGE_DIR = f"{HARNESS_DIR}/knowledge"
ADR_DIR = f"{KNOWLEDGE_DIR}/adr"
KNOWLEDGE_HOWTO_DIR = f"{KNOWLEDGE_DIR}/how-to"
PRINCIPLE_PACKS_DIR = f"{HARNESS_DIR}/principle-packs"
TEMPLATES_DIR = f"{HARNESS_DIR}/templates"
EVALS_DIR = f"{HARNESS_DIR}/evals"

# L-RULE: constitution lives inside the brain (design v3)
CONSTITUTION_PATH = f"{MEMORY_DIR}/constitution.md"

# Per-change specs at repo root (spec-kit flat convention)
SPECS_DIR = "specs"

# Cross-session progress log (lightweight, separate from specs)
AGENT_DIR = ".agent"
PROGRESS_PATH = f"{AGENT_DIR}/progress.md"

# CI + hooks (GitLab CI is the canonical pipeline; design v3)
GITLAB_CI_CONFIG = ".gitlab-ci.yml"
PRE_COMMIT_CONFIG = ".pre-commit-config.yaml"

# The 7 knowledge base documents produced by /hx-baseline.
KNOWLEDGE_DOCS: list[str] = [
    "product",
    "architecture",
    "tech-stack",
    "business",
    "conventions",
    "glossary",
    "setup-and-verify",
]

# Command → playbook filename (without .md). Order = recommended SDD flow.
PLAYBOOK_FILES: dict[str, str] = {
    "constitution": "00-constitution",
    "baseline": "10-baseline",
    "next": "12-next",
    "propose": "30-propose",
    "clarify": "31-clarify",
    "design": "32-design",
    "plan": "33-plan",
    "tasks": "34-tasks",
    "analyze": "35-analyze",
    "implement": "40-implement",
    "verify": "41-verify",
    "review": "50-review",
    "archive": "51-archive",
    "doctor": "90-doctor",
}

# Ordered command list (used by AGENTS.md tables and adapters).
HX_COMMANDS: list[str] = list(PLAYBOOK_FILES.keys())


def playbook_path(command: str) -> str:
    """Return the relative path to a command's playbook file."""
    return f"{PLAYBOOKS_DIR}/{PLAYBOOK_FILES[command]}.md"


# Legacy paths from the previous layout — used by `harness doctor` to warn
# users with the old `harness-artifacts/` and root `memory/` directories.
LEGACY_ARTIFACTS_DIR = "harness-artifacts"
LEGACY_CONSTITUTION_PATH = "memory/constitution.md"
