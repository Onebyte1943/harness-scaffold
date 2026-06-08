"""Runtime message localization for CLI output.

Scaffold templates are English-only — deliverable narrative language is
chosen at `/hx-*` runtime by the agent, per the Output Language Contract
in AGENTS.md. This module covers the orthogonal concern of localizing
the CLI's own runtime strings — progress prints, the init summary
table, the `Next steps` panel, doctor diagnostics, and the interactive
`questionary` prompt.

Design constraints (per project guidance):
- Two locales only: `zh` and `en`. `zh` is the default.
- One source of truth per key, type-checked via dataclass fields.
- Adding a new locale = add a new `Messages` literal at the bottom; no
  call-site changes.
- Tool / file / command identifiers stay untranslated (verify.sh,
  /hx-baseline, .harness/, REQ-001, ...) — they appear verbatim in
  format placeholders.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Messages:
    """All CLI-emitted strings, in one locale."""

    # ─── harness init: agent picker ────────────────────────────────────
    pick_agents_prompt: str
    pick_agents_claude: str
    pick_agents_codex: str
    pick_agents_cursor: str
    pick_agents_copilot: str
    pick_agents_gemini: str

    # ─── harness init: progress headers ────────────────────────────────
    generating_brain: str
    generating_shared: str
    generating_adapter: str  # uses {agent}
    no_adapter_impl: str  # uses {agent}

    # ─── harness init: git bootstrap ──────────────────────────────────
    git_would_init: str
    git_initialized: str
    git_unavailable: str
    gitignore_appended: str

    # ─── harness init: messages around invocation ─────────────────────
    already_initialized: str
    adding_agents: str  # uses {agents}
    all_agents_already: str
    dry_run_banner: str
    dry_run_count: str  # uses {n}

    # ─── harness init: summary panel ──────────────────────────────────
    summary_title: str
    summary_setting: str
    summary_value: str
    summary_project: str
    summary_profile: str
    summary_flow: str
    summary_lang: str
    summary_output_lang: str
    summary_agents: str
    summary_shell: str
    summary_presets: str

    next_steps_title: str
    next_steps_panel_title: str
    next_step_constitution: str
    next_step_baseline: str
    next_step_next: str
    next_step_doctor: str

    # ─── harness doctor ───────────────────────────────────────────────
    doctor_not_in_project: str
    doctor_header: str  # uses {name}
    doctor_table_status: str
    doctor_table_item: str
    doctor_table_detail: str
    doctor_ok: str
    doctor_warn: str
    doctor_fail: str
    doctor_summary_errors: str  # uses {errors} {warnings}
    doctor_summary_warnings: str  # uses {warnings}
    doctor_all_passed: str


_EN = Messages(
    pick_agents_prompt="Select AI agent terminals to support:",
    pick_agents_claude="Claude Code",
    pick_agents_codex="Codex CLI",
    pick_agents_cursor="Cursor (via registry, not bundled)",
    pick_agents_copilot="Copilot (via registry, not bundled)",
    pick_agents_gemini="Gemini CLI (via registry, not bundled)",
    generating_brain="Generating .harness/ brain...",
    generating_shared="Generating shared contract layer...",
    generating_adapter="Generating {agent} adapter...",
    no_adapter_impl="No adapter implementation for '{agent}', skipping",
    git_would_init="would run git init",
    git_initialized="git init",
    git_unavailable="git not available, skipping git init",
    gitignore_appended="append .gitignore",
    already_initialized=(
        "Harness already initialized. Use --agent to add a new terminal "
        "adapter, or --force to re-render the brain."
    ),
    adding_agents="Adding agent(s): {agents}",
    all_agents_already="All requested agents already configured.",
    dry_run_banner="DRY RUN — no files will be written",
    dry_run_count="Would generate {n} files",
    summary_title="Harness Initialized",
    summary_setting="Setting",
    summary_value="Value",
    summary_project="Project",
    summary_profile="Profile",
    summary_flow="Flow",
    summary_lang="Lang",
    summary_output_lang="Output-Lang",
    summary_agents="Agents",
    summary_shell="Shell",
    summary_presets="Presets",
    next_steps_title="Next steps:",
    next_steps_panel_title="W0 Bootstrap",
    next_step_constitution=("1. Run /hx-constitution to synthesize engineering principles"),
    next_step_baseline="2. Run /hx-baseline to build the 7-doc knowledge base",
    next_step_next="3. Run /hx-next when in doubt about the next move",
    next_step_doctor="4. Run harness doctor to verify setup",
    doctor_not_in_project=("Not in a harness project. Run [cyan]harness init[/cyan] first."),
    doctor_header="Harness Doctor — checking {name}",
    doctor_table_status="Status",
    doctor_table_item="Item",
    doctor_table_detail="Detail",
    doctor_ok="OK",
    doctor_warn="WARN",
    doctor_fail="FAIL",
    doctor_summary_errors="{errors} error(s), {warnings} warning(s)",
    doctor_summary_warnings="No errors, {warnings} warning(s)",
    doctor_all_passed="All checks passed.",
)


_ZH = Messages(
    pick_agents_prompt="选择要适配的 AI Agent 终端:",
    pick_agents_claude="Claude Code",
    pick_agents_codex="Codex CLI",
    pick_agents_cursor="Cursor (通过 registry 引用,默认不打包)",
    pick_agents_copilot="Copilot (通过 registry 引用,默认不打包)",
    pick_agents_gemini="Gemini CLI (通过 registry 引用,默认不打包)",
    generating_brain="正在生成 .harness/ 中枢...",
    generating_shared="正在生成共享契约层...",
    generating_adapter="正在生成 {agent} 适配器...",
    no_adapter_impl="未实现 '{agent}' 适配器,跳过",
    git_would_init="将执行 git init",
    git_initialized="git init 完成",
    git_unavailable="未找到 git,跳过 git init",
    gitignore_appended="已追加 .gitignore",
    already_initialized=(
        "Harness 已初始化。用 --agent 追加新的终端适配器,或用 --force 重新渲染中枢。"
    ),
    adding_agents="新增 agent: {agents}",
    all_agents_already="所有请求的 agent 都已配置。",
    dry_run_banner="DRY RUN —— 不会写入任何文件",
    dry_run_count="将生成 {n} 个文件",
    summary_title="Harness 初始化完成",
    summary_setting="项",
    summary_value="值",
    summary_project="项目",
    summary_profile="Profile",
    summary_flow="Flow",
    summary_lang="主语言",
    summary_output_lang="输出语言",
    summary_agents="Agents",
    summary_shell="Shell",
    summary_presets="Presets",
    next_steps_title="下一步:",
    next_steps_panel_title="W0 Bootstrap",
    next_step_constitution="1. 运行 /hx-constitution 综合产出工程原则",
    next_step_baseline="2. 运行 /hx-baseline 构建 7 篇核心知识库文档",
    next_step_next="3. 拿不准下一步时,运行 /hx-next 让路由器推荐",
    next_step_doctor="4. 运行 harness doctor 自检",
    doctor_not_in_project=("当前目录不在 harness 项目中。请先运行 [cyan]harness init[/cyan]。"),
    doctor_header="Harness Doctor —— 正在检查 {name}",
    doctor_table_status="状态",
    doctor_table_item="项",
    doctor_table_detail="详情",
    doctor_ok="OK",
    doctor_warn="WARN",
    doctor_fail="FAIL",
    doctor_summary_errors="{errors} 个错误,{warnings} 个警告",
    doctor_summary_warnings="无错误,{warnings} 个警告",
    doctor_all_passed="所有检查通过。",
)


_LOCALES: dict[str, Messages] = {"en": _EN, "zh": _ZH}


def messages(lang: str) -> Messages:
    """Return the message table for `lang`. Falls back to en for unknown."""
    return _LOCALES.get(lang, _EN)
