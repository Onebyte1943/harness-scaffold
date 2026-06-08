from __future__ import annotations

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

# Codex uses the same /hx-<cmd> surface; descriptions kept terse. English-only:
# agent contract files have a single source of truth; deliverable language is
# chosen at /hx-* runtime per the Output Language Contract in AGENTS.md.
_SKILL_DESCRIPTIONS: dict[str, str] = {
    "constitution": "Synthesize the project constitution",
    "baseline": "Build the 7-doc knowledge base",
    "next": "Route the next move (suggest flow + next command)",
    "propose": "Draft a change proposal under specs/<NNN>-<slug>/",
    "clarify": "Multi-round structured clarification",
    "design": "Produce an AI-friendly design with stable IDs",
    "plan": "Emit the implementation plan and any ADRs",
    "tasks": "Break design into TDD-ordered tasks",
    "analyze": "Cross-artifact consistency check",
    "implement": "Execute tasks one at a time, TDD-first",
    "verify": "Single deterministic sensor: lint + types + tests + honesty",
    "review": "Correctness/consistency + Google/Alibaba code review",
    "archive": "Post-merge knowledge refresh + reference validator",
    "doctor": "Harness self-check",
}


def _command_context(command: str) -> dict[str, Any]:
    return {
        "command": command,
        "description": _SKILL_DESCRIPTIONS[command],
        "playbook_path": playbook_path(command),
        "constitution_path": CONSTITUTION_PATH,
        "specs_dir": SPECS_DIR,
        "harness_dir": HARNESS_DIR,
        "agent_dir": AGENT_DIR,
    }


class CodexAdapter(AdapterBase):
    """Adapter for Codex CLI terminal."""

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

        commands_dir = project_root / ".codex" / "commands"
        for cmd in HX_COMMANDS:
            cmd_path = commands_dir / f"hx-{cmd}.md"
            if self.engine.render_file(
                "adapters/codex/command.md.j2",
                cmd_path,
                _command_context(cmd),
                force=force,
                dry_run=dry_run,
            ):
                generated.append(cmd_path)

        return generated

    def validate(self, project_root: Path) -> list[str]:
        issues: list[str] = []

        commands_dir = project_root / ".codex" / "commands"
        if not commands_dir.exists():
            issues.append(f"Missing directory {commands_dir}")
            return issues

        for cmd in HX_COMMANDS:
            cmd_path = commands_dir / f"hx-{cmd}.md"
            if not cmd_path.exists():
                issues.append(f"Missing slash command {cmd_path}")

        return issues
