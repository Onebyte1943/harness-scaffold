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
# them in the command picker. Data table (not narrative); a future move to
# locales/skill_descriptions/{lang}.yaml would let translators edit without
# touching Python.
_SKILL_DESCRIPTIONS_EN: dict[str, str] = {
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

_SKILL_DESCRIPTIONS_ZH: dict[str, str] = {
    "constitution": (
        "综合通用 SDD 原则、principle packs,以及团队从代码库沉淀的事实模式,生成项目宪章"
    ),
    "baseline": (
        "构建 7 篇核心知识库文档 (product、architecture、tech-stack、business、"
        "conventions、glossary、setup-and-verify,以及 how-to/)"
    ),
    "next": ("路由下一步动作:根据当前状态推荐 flow 等级与下一个 /hx-<cmd> —— 不写入任何文件"),
    "propose": ("在 specs/<NNN>-<slug>/ 起草变更提案 (问题、备选方案、风险、验收)"),
    "clarify": ("多轮结构化澄清 —— 在设计前补齐缺失需求"),
    "design": ("产出 AI 友好的设计文档,带稳定 ID (REQ/NFR/IF/DEC/RISK/Q) 与追溯矩阵"),
    "plan": ("输出实施计划,并把 ADR 落到 .harness/knowledge/adr/"),
    "tasks": ("把设计拆解成 TDD 顺序、按用户故事分组的任务,带 [P] 并行标记"),
    "analyze": (
        "跨工件一致性检查 (constitution ↔ knowledge ↔ "
        "proposal ↔ design ↔ tasks) —— 用作 implement 的 gate"
    ),
    "implement": ("一次执行一个任务,TDD 优先,遇到上游缺陷支持回滚 / 熔断"),
    "verify": (
        "单一确定性传感器:lint + typecheck + tests + test honesty "
        "(与 hook、pre-commit、CI 共用同一脚本)"
    ),
    "review": (
        "双重评审 —— 对照 proposal/design 检查正确性与一致性,叠加 Google + 阿里代码评审维度"
    ),
    "archive": (
        "合并后:刷新受影响的知识文档,跑 reference validator,在 .agent/progress.md 追加一行"
    ),
    "doctor": ("Harness 自检:rule↔guardrail 同步、预算、漂移、死规则、eval 回归"),
}


def _skill_descriptions(output_lang: str) -> dict[str, str]:
    return _SKILL_DESCRIPTIONS_ZH if output_lang == "zh" else _SKILL_DESCRIPTIONS_EN


def _command_context(command: str, output_lang: str) -> dict[str, Any]:
    """Context for rendering one /hx-<cmd> slash-command file."""
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


def _claude_md_context(output_lang: str) -> dict[str, Any]:
    return {
        "hx_commands": HX_COMMANDS,
        "skill_descriptions": _skill_descriptions(output_lang),
        "constitution_path": CONSTITUTION_PATH,
        "output_lang": output_lang,
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
        output_lang = context.get("output_lang", "en")

        claude_md_path = project_root / "CLAUDE.md"
        if self.engine.render_localized(
            "adapters/claude/CLAUDE",
            claude_md_path,
            _claude_md_context(output_lang),
            force=force,
            dry_run=dry_run,
        ):
            generated.append(claude_md_path)

        commands_dir = project_root / ".claude" / "commands"
        for cmd in HX_COMMANDS:
            cmd_path = commands_dir / f"hx-{cmd}.md"
            if self.engine.render_localized(
                "adapters/claude/command",
                cmd_path,
                _command_context(cmd, output_lang),
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
