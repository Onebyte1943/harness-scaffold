from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness.adapters.base import AdapterBase
from harness.core.layout import (
    AGENT_DIR,
    CONSTITUTION_PATH,
    HARNESS_DIR,
    HX_COMMANDS,
    SPECS_DIR,
    playbook_path,
)
from harness.core.registry import AdapterSpec
from harness.core.scaffold import ScaffoldEngine

# Short, one-line `description:` per /hx-<cmd>. Keep terse — Claude Code shows
# them in the command picker. English-only: the slash command files are part
# of the agent contract layer and must stay in a single source-of-truth
# language; deliverable narrative language is decided at /hx-* runtime per
# the Output Language Contract in AGENTS.md.
_SKILL_DESCRIPTIONS: dict[str, str] = {
    "constitution": (
        "Synthesize the project constitution from universal SDD principles, "
        "principle packs, and the team's de-facto patterns"
    ),
    "baseline": (
        "Build the 7-doc knowledge base (product, architecture, tech-stack, "
        "business, conventions, glossary, setup-and-verify, plus how-to/)"
    ),
    "next": (
        "Route the next move: suggest flow level and the next /hx-<cmd> "
        "based on current state — no files written"
    ),
    "propose": (
        "Draft a change proposal under specs/<NNN>-<slug>/ (problem, options, risk, acceptance)"
    ),
    "clarify": ("Multi-round structured clarification — gather missing requirements before design"),
    "design": (
        "Produce an AI-friendly design with stable IDs (REQ/NFR/IF/DEC/RISK/Q) "
        "and a traceability matrix"
    ),
    "plan": ("Emit the implementation plan and any ADRs into .harness/knowledge/adr/"),
    "tasks": (
        "Break design into TDD-ordered, user-story-grouped tasks with [P] parallelism markers"
    ),
    "analyze": (
        "Cross-artifact consistency check (constitution ↔ knowledge ↔ "
        "proposal ↔ design ↔ tasks) — gates implement"
    ),
    "implement": (
        "Execute one task at a time, TDD-first, with rollback / circuit-breaker on upstream flaws"
    ),
    "verify": (
        "Single deterministic sensor: lint + typecheck + tests + test honesty "
        "(same script as hooks, pre-commit, and CI)"
    ),
    "review": (
        "Dual review — correctness & consistency vs proposal/design plus "
        "Google + Alibaba code-review dimensions"
    ),
    "archive": (
        "Post-merge: refresh affected knowledge docs, run reference validator, "
        "append a row to .agent/progress.md"
    ),
    "doctor": (
        "Harness self-check: rule↔guardrail sync, budgets, drift, dead rules, eval regressions"
    ),
}


def _command_context(command: str) -> dict[str, Any]:
    """Context for rendering one /hx-<cmd> slash-command file."""
    return {
        "command": command,
        "description": _SKILL_DESCRIPTIONS[command],
        "playbook_path": playbook_path(command),
        "constitution_path": CONSTITUTION_PATH,
        "specs_dir": SPECS_DIR,
        "harness_dir": HARNESS_DIR,
        "agent_dir": AGENT_DIR,
    }


def _claude_md_context() -> dict[str, Any]:
    return {
        "hx_commands": HX_COMMANDS,
        "skill_descriptions": _SKILL_DESCRIPTIONS,
        "constitution_path": CONSTITUTION_PATH,
    }


def _build_settings() -> dict[str, Any]:
    return {
        "permissions": {
            "allow": [
                f"Read({HARNESS_DIR}/**)",
                f"Write({HARNESS_DIR}/**)",
                "Read(.claude/**)",
                "Write(.claude/**)",
                f"Read({SPECS_DIR}/**)",
                f"Write({SPECS_DIR}/**)",
                f"Read({AGENT_DIR}/**)",
                f"Write({AGENT_DIR}/**)",
                "Read(AGENTS.md)",
                "Read(CLAUDE.md)",
            ],
        },
    }


class ClaudeAdapter(AdapterBase):
    """Adapter for Claude Code terminal."""

    def __init__(self, spec: AdapterSpec, engine: ScaffoldEngine) -> None:
        super().__init__(spec, engine)

    def generate(
        self,
        project_root: Path,
        context: dict[str, Any],
        *,
        force: bool = False,
        dry_run: bool = False,
    ) -> list[Path]:
        generated: list[Path] = []

        claude_md_path = project_root / "CLAUDE.md"
        if self.engine.render_file(
            "adapters/claude/CLAUDE.md.j2",
            claude_md_path,
            _claude_md_context(),
            force=force,
            dry_run=dry_run,
        ):
            generated.append(claude_md_path)

        commands_dir = project_root / ".claude" / "commands"
        for cmd in HX_COMMANDS:
            cmd_path = commands_dir / f"hx-{cmd}.md"
            if self.engine.render_file(
                "adapters/claude/command.md.j2",
                cmd_path,
                _command_context(cmd),
                force=force,
                dry_run=dry_run,
            ):
                generated.append(cmd_path)

        self.engine.ensure_dir(project_root / ".claude" / "hooks", dry_run=dry_run)

        settings_path = project_root / ".claude" / "settings.json"
        settings_content = json.dumps(_build_settings(), indent=2) + "\n"
        if self.engine.render_static(settings_content, settings_path, force=force, dry_run=dry_run):
            generated.append(settings_path)

        return generated

    def validate(self, project_root: Path) -> list[str]:
        issues: list[str] = []

        claude_md = project_root / "CLAUDE.md"
        if not claude_md.exists():
            issues.append(f"Missing {claude_md}")

        commands_dir = project_root / ".claude" / "commands"
        for cmd in HX_COMMANDS:
            cmd_path = commands_dir / f"hx-{cmd}.md"
            if not cmd_path.exists():
                issues.append(f"Missing slash command {cmd_path}")

        settings_path = project_root / ".claude" / "settings.json"
        if not settings_path.exists():
            issues.append(f"Missing {settings_path}")

        hooks_dir = project_root / ".claude" / "hooks"
        if not hooks_dir.exists():
            issues.append(f"Missing directory {hooks_dir}")

        return issues
