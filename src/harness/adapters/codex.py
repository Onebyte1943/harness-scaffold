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

# Codex uses the same /hx-<cmd> surface; descriptions kept terse.
_SKILL_DESCRIPTIONS_EN: dict[str, str] = {
    "constitution": "Synthesize the project constitution",
    "baseline": "Build the 8-doc knowledge base",
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

_SKILL_DESCRIPTIONS_ZH: dict[str, str] = {
    "constitution": "生成项目宪章",
    "baseline": "构建 8 篇核心知识库文档",
    "next": "路由下一步动作 (推荐 flow 与下一个命令)",
    "propose": "在 specs/<NNN>-<slug>/ 起草变更提案",
    "clarify": "多轮结构化澄清",
    "design": "产出带稳定 ID 的 AI 友好设计文档",
    "plan": "输出实施计划与 ADR",
    "tasks": "把设计拆解为 TDD 顺序的任务",
    "analyze": "跨工件一致性检查",
    "implement": "一次执行一个任务,TDD 优先",
    "verify": "单一确定性传感器:lint + types + tests + honesty",
    "review": "正确性/一致性 + Google/阿里代码评审",
    "archive": "合并后刷新知识 + 跑 reference validator",
    "doctor": "Harness 自检",
}


def _skill_descriptions(output_lang: str) -> dict[str, str]:
    return _SKILL_DESCRIPTIONS_ZH if output_lang == "zh" else _SKILL_DESCRIPTIONS_EN


def _command_context(command: str, output_lang: str) -> dict[str, Any]:
    return {
        "command": command,
        "description": _skill_descriptions(output_lang)[command],
        "playbook_path": playbook_path(command),
        "constitution_path": CONSTITUTION_PATH,
        "specs_dir": SPECS_DIR,
        "harness_dir": HARNESS_DIR,
        "agent_dir": AGENT_DIR,
        "output_lang": output_lang,
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
        output_lang = context.get("output_lang", "en")

        commands_dir = project_root / ".codex" / "commands"
        for cmd in HX_COMMANDS:
            cmd_path = commands_dir / f"hx-{cmd}.md"
            if self.engine.render_localized(
                "adapters/codex/command",
                cmd_path,
                _command_context(cmd, output_lang),
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
