"""harness init — Initialize harness in a repository (design v3)."""

from __future__ import annotations

import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from harness import __version__
from harness.core.config import HARNESS_DIR, HarnessConfig, save_config
from harness.core.i18n import Messages, messages
from harness.core.layout import (
    AGENT_DIR,
    EVALS_DIR,
    GITLAB_CI_CONFIG,
    HX_COMMANDS,
    KNOWLEDGE_DIR,
    KNOWLEDGE_DOCS,
    PLAYBOOK_FILES,
    PRE_COMMIT_CONFIG,
    PRINCIPLE_PACKS_DIR,
    SPECS_DIR,
    TEMPLATES_DIR,
)
from harness.core.scaffold import ScaffoldEngine

console = Console()

# Default-bundled adapters are claude + codex. Cursor / Copilot / Gemini
# remain in VALID_AGENTS so the registry can be extended without code
# changes, but they are not promoted as defaults in docs.
VALID_AGENTS = ["claude", "codex", "cursor", "copilot", "gemini"]
VALID_PROFILES = ["brownfield", "greenfield", "vibecode"]
VALID_FLOWS = ["quick", "standard", "full", "epic"]
VALID_PRESETS = ["trunk-based", "ddd", "secure"]
VALID_LANGS = ["auto", "python", "typescript", "go", "rust", "java", "polyglot"]
VALID_OUTPUT_LANGS = ["zh", "en"]


def _detect_shell() -> str:
    return "ps" if platform.system() == "Windows" else "sh"


def _detect_lang(project_root: Path) -> str:
    """Cheap heuristic: surface marker files. `auto` if nothing obvious."""
    markers = [
        ("pyproject.toml", "python"),
        ("requirements.txt", "python"),
        ("package.json", "typescript"),
        ("tsconfig.json", "typescript"),
        ("go.mod", "go"),
        ("Cargo.toml", "rust"),
        ("pom.xml", "java"),
        ("build.gradle", "java"),
        ("build.gradle.kts", "java"),
    ]
    hits = [lang for fname, lang in markers if (project_root / fname).exists()]
    if not hits:
        return "auto"
    if len(set(hits)) == 1:
        return hits[0]
    return "polyglot"


def _is_interactive() -> bool:
    # Detached/redirected stdin (CI, pipes) has no isatty — fall back to non-interactive.
    isatty = getattr(sys.stdin, "isatty", None)
    return bool(isatty and isatty())


def _prompt_agents(m: Messages) -> list[str]:
    try:
        import questionary
    except ImportError:
        return ["claude"]

    try:
        result = questionary.checkbox(
            m.pick_agents_prompt,
            choices=[
                questionary.Choice(m.pick_agents_claude, value="claude", checked=True),
                questionary.Choice(m.pick_agents_codex, value="codex"),
                questionary.Choice(m.pick_agents_cursor, value="cursor"),
                questionary.Choice(m.pick_agents_copilot, value="copilot"),
                questionary.Choice(m.pick_agents_gemini, value="gemini"),
            ],
        ).ask()
    except (KeyboardInterrupt, EOFError):
        return ["claude"]
    return result if result else ["claude"]


def _get_template_dir() -> Path:
    return Path(__file__).parent.parent / "templates"


def _backup_legacy_agents_md(root: Path, *, force: bool, dry_run: bool) -> None:
    """0.2 → 0.3 migration: if --force will overwrite a pre-0.3 AGENTS.md,
    back the existing one up to AGENTS.md.0.2.bak. Only runs when
    `force=True` AND the existing AGENTS.md predates the 5-subsystem
    rewrite (no `## Subsystems` heading) AND no backup file exists yet.

    The detection is structural rather than version-based: the
    pre-0.3 template did not contain the `## Subsystems` line, the
    0.3 template requires it. Future template revisions can refine
    the marker without breaking the migration path.
    """
    if not force:
        return
    agents_md = root / "AGENTS.md"
    if not agents_md.exists():
        return
    try:
        body = agents_md.read_text()
    except OSError:
        return
    if "## Subsystems" in body:
        # Already 0.3+ — nothing to migrate.
        return
    backup = root / "AGENTS.md.0.2.bak"
    if backup.exists():
        # Already migrated once; don't clobber the prior backup.
        console.print(
            "  [yellow]warn[/yellow] AGENTS.md.0.2.bak already exists — "
            "leaving prior backup in place."
        )
        return
    if dry_run:
        console.print("  [cyan]would back up legacy AGENTS.md → AGENTS.md.0.2.bak[/cyan]")
        return
    backup.write_text(body)
    console.print("  [green]backed up legacy AGENTS.md → AGENTS.md.0.2.bak[/green]")


def _backup_legacy_constitution(root: Path, *, force: bool, dry_run: bool) -> None:
    """0.3 → 0.4 migration: if a pre-0.4 constitution exists (no Sync
    Impact Report and no spec-kit `**Version**:` line), back it up to
    `.harness/memory/constitution.md.0.3.bak` so the user can diff
    against it after running `/hx-constitution` to regenerate the
    spec-kit-shaped file.

    The constitution itself is lazy (created by `/hx-constitution`,
    not by `harness init`), so this helper only runs when --force is
    set and the file already exists. We do not write a fresh
    constitution.md here — that's `/hx-constitution`'s job.
    """
    if not force:
        return
    from harness.core.layout import CONSTITUTION_PATH

    constitution = root / CONSTITUTION_PATH
    if not constitution.exists():
        return
    try:
        body = constitution.read_text()
    except OSError:
        return
    has_sync_report = "SYNC IMPACT REPORT" in body[:200]
    has_version_line = "**Version**" in body
    if has_sync_report and has_version_line:
        # Already spec-kit-formatted — nothing to migrate.
        return
    backup = constitution.with_suffix(".md.0.3.bak")
    if backup.exists():
        console.print(
            f"  [yellow]warn[/yellow] {backup.name} already exists — leaving prior backup in place."
        )
        return
    if dry_run:
        console.print(
            f"  [cyan]would back up legacy {CONSTITUTION_PATH} → {backup.relative_to(root)}[/cyan]"
        )
        return
    backup.write_text(body)
    console.print(
        f"  [green]backed up legacy {CONSTITUTION_PATH} → "
        f"{backup.relative_to(root)}[/green] "
        "(rerun /hx-constitution to regenerate in spec-kit format)"
    )


def _build_context(config: HarnessConfig) -> dict[str, Any]:
    return {
        "project_name": config.project_root.name,
        "profile": config.profile,
        "flow": config.flow,
        "lang": config.lang,
        "output_lang": config.output_lang,
        "agents": config.agents,
        "presets": config.presets,
        "script_shell": config.script_shell,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "harness_version": __version__,
        "hx_commands": HX_COMMANDS,
        "specs_dir": SPECS_DIR,
        "agent_dir": AGENT_DIR,
        "knowledge_dir": KNOWLEDGE_DIR,
        "principle_packs_dir": PRINCIPLE_PACKS_DIR,
        "evals_dir": EVALS_DIR,
        "templates_dir": TEMPLATES_DIR,
        "knowledge_docs": KNOWLEDGE_DOCS,
    }


def _generate_brain(
    engine: ScaffoldEngine,
    config: HarnessConfig,
    context: dict[str, Any],
    *,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Generate .harness/ brain directory (L-MECH layer)."""
    m = messages(config.output_lang)
    console.print(f"\n[bold]{m.generating_brain}[/bold]")
    root = config.project_root
    harness = root / HARNESS_DIR

    # 0.3 → 0.4 migration: if --force is overwriting a pre-spec-kit
    # constitution, back it up first so the user can diff against the
    # newly regenerated file.
    _backup_legacy_constitution(root, force=force, dry_run=dry_run)

    engine.render_file(
        "harness/registry.toml.j2",
        harness / "registry.toml",
        context,
        force=force,
        dry_run=dry_run,
    )
    engine.render_file(
        "harness/config.toml.j2",
        harness / "config.toml",
        context,
        force=force,
        dry_run=dry_run,
    )

    for pb_filename in PLAYBOOK_FILES.values():
        engine.render_file(
            f"harness/playbooks/{pb_filename}.md.j2",
            harness / "playbooks" / f"{pb_filename}.md",
            context,
            force=force,
            dry_run=dry_run,
        )

    engine.render_file(
        "harness/principle-packs/generic.md.j2",
        harness / "principle-packs" / "generic.md",
        context,
        force=force,
        dry_run=dry_run,
    )

    # 12-Factor Agents pack — Subsystem 1 (Instructions) feed material
    # for /hx-constitution. Selected automatically by brownfield /
    # vibecode profiles; available to greenfield via explicit pick.
    engine.render_file(
        "harness/principle-packs/12-factor-agents.md.j2",
        harness / "principle-packs" / "12-factor-agents.md",
        context,
        force=force,
        dry_run=dry_run,
    )

    engine.render_file(
        "harness/evals/README.md.j2",
        harness / "evals" / "README.md",
        context,
        force=force,
        dry_run=dry_run,
    )

    # feature_list.schema.json — Subsystem 2 (State). Ships at
    # .harness/templates/feature_list.schema.json so each spec's
    # feature_list.json can `$ref` it for editor / CI validation.
    engine.render_file(
        "harness/templates/feature_list.schema.json.j2",
        harness / "templates" / "feature_list.schema.json",
        context,
        force=force,
        dry_run=dry_run,
    )

    # Eager-create parents so first-write doesn't need `mkdir -p` ceremony.
    # adr/ and how-to/ remain lazy — created by /hx-plan and /hx-baseline.
    for sub in ("memory", "knowledge", "templates"):
        engine.ensure_dir(harness / sub, dry_run=dry_run)

    script_shell = config.script_shell
    script_templates = [
        (f"harness/scripts/{script_shell}/verify.sh.j2", f"scripts/{script_shell}/verify.sh"),
        (
            f"harness/scripts/{script_shell}/lib/common.sh.j2",
            f"scripts/{script_shell}/lib/common.sh",
        ),
    ]
    for tmpl, out in script_templates:
        if engine.has_template(tmpl):
            engine.render_file(
                tmpl,
                harness / out,
                context,
                force=force,
                dry_run=dry_run,
                executable=True,
            )


def _generate_shared(
    engine: ScaffoldEngine,
    config: HarnessConfig,
    context: dict[str, Any],
    *,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Materialize AGENTS.md, GitLab CI, pre-commit, and the .agent/ marker.

    L-RULE (constitution), L-STATE (specs, knowledge content) are still
    bootstrapped lazily by the first playbook that needs them.
    """
    m = messages(config.output_lang)
    console.print(f"\n[bold]{m.generating_shared}[/bold]")
    root = config.project_root

    # 0.2 → 0.3 migration: if --force is overwriting a pre-0.3 AGENTS.md
    # (one without the `## Subsystems` heading the new template carries),
    # back it up first so the user can diff against their old contract.
    _backup_legacy_agents_md(root, force=force, dry_run=dry_run)

    engine.render_file(
        "shared/AGENTS.md.j2",
        root / "AGENTS.md",
        context,
        force=force,
        dry_run=dry_run,
    )

    engine.render_file(
        "shared/gitlab-ci.yml.j2",
        root / GITLAB_CI_CONFIG,
        context,
        force=force,
        dry_run=dry_run,
    )

    engine.render_file(
        "shared/pre-commit-config.yaml.j2",
        root / PRE_COMMIT_CONFIG,
        context,
        force=force,
        dry_run=dry_run,
    )

    # init.sh — Subsystem 3 (Verification) entry script.
    # Single command the agent runs at session start (Resume); calls verify.sh.
    init_template = "shared/init.sh.j2" if config.script_shell == "sh" else "shared/init.ps1.j2"
    init_filename = "init.sh" if config.script_shell == "sh" else "init.ps1"
    engine.render_file(
        init_template,
        root / init_filename,
        context,
        force=force,
        dry_run=dry_run,
        executable=True,
    )

    # .agent/ holds .agent/progress.md once /hx-implement first writes there.
    # Drop a .gitkeep so the directory is committable from day one.
    engine.ensure_dir(root / AGENT_DIR, dry_run=dry_run)
    gitkeep = root / AGENT_DIR / ".gitkeep"
    if not gitkeep.exists() and not dry_run:
        gitkeep.write_text("")


def _generate_adapters(
    engine: ScaffoldEngine,
    config: HarnessConfig,
    context: dict[str, Any],
    *,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Generate per-agent adapter files."""
    from harness.adapters import get_adapter

    m = messages(config.output_lang)
    for agent_name in config.agents:
        console.print(f"\n[bold]{m.generating_adapter.format(agent=agent_name)}[/bold]")
        try:
            adapter = get_adapter(agent_name, engine)
            adapter.generate(config.project_root, context, force=force, dry_run=dry_run)
        except KeyError:
            console.print(
                f"  [yellow]warning[/yellow] {m.no_adapter_impl.format(agent=agent_name)}"
            )


def _init_git(
    project_root: Path,
    engine: ScaffoldEngine,
    context: dict[str, Any],
    *,
    dry_run: bool = False,
) -> None:
    """Initialize git repo if not already in one."""
    m = messages(context.get("output_lang", "en"))
    if (project_root / ".git").exists():
        return

    if dry_run:
        console.print(f"  [cyan]{m.git_would_init}[/cyan]")
        return

    try:
        subprocess.run(["git", "init"], cwd=project_root, capture_output=True, check=True)
        console.print(f"  [green]{m.git_initialized}[/green]")
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(f"  [yellow]warning[/yellow] {m.git_unavailable}")

    if engine.has_template("shared/gitignore.j2"):
        gitignore_path = project_root / ".gitignore"
        if gitignore_path.exists():
            existing = gitignore_path.read_text()
            from jinja2 import Environment, FileSystemLoader

            env = Environment(loader=FileSystemLoader(str(_get_template_dir())))
            tmpl = env.get_template("shared/gitignore.j2")
            harness_block = tmpl.render(**context)
            if "# harness" not in existing:
                gitignore_path.write_text(existing.rstrip() + "\n\n" + harness_block)
                console.print(f"  [green]{m.gitignore_appended}[/green]")
        else:
            engine.render_file("shared/gitignore.j2", gitignore_path, context)


def _print_summary(config: HarnessConfig) -> None:
    """Print initialization summary."""
    m = messages(config.output_lang)
    table = Table(title=m.summary_title, show_header=True, header_style="bold cyan")
    table.add_column(m.summary_setting, style="bold")
    table.add_column(m.summary_value)
    table.add_row(m.summary_project, config.project_root.name)
    table.add_row(m.summary_profile, config.profile)
    table.add_row(m.summary_flow, config.flow)
    table.add_row(m.summary_lang, config.lang)
    table.add_row(m.summary_output_lang, config.output_lang)
    table.add_row(m.summary_agents, ", ".join(config.agents))
    table.add_row(m.summary_shell, config.script_shell)
    if config.presets:
        table.add_row(m.summary_presets, ", ".join(config.presets))
    console.print()
    console.print(table)
    console.print()
    # Splice the literal `/hx-*` and `harness doctor` tokens with cyan
    # styling. Localized strings carry the surrounding prose; identifiers
    # stay untranslated.
    next_steps = "\n".join(
        f"  {line}"
        for line in (
            m.next_step_constitution.replace("/hx-constitution", "[cyan]/hx-constitution[/cyan]"),
            m.next_step_baseline.replace("/hx-baseline", "[cyan]/hx-baseline[/cyan]"),
            m.next_step_next.replace("/hx-next", "[cyan]/hx-next[/cyan]"),
            m.next_step_doctor.replace("harness doctor", "[cyan]harness doctor[/cyan]"),
        )
    )
    console.print(
        Panel(
            f"[bold]{m.next_steps_title}[/bold]\n{next_steps}",
            title=m.next_steps_panel_title,
            border_style="green",
        )
    )


@click.command()
@click.argument("project", default=".", type=click.Path())
@click.option(
    "--agent",
    "-a",
    "agents",
    multiple=True,
    type=click.Choice(VALID_AGENTS),
    help="Agent terminals to support (repeatable).",
)
@click.option(
    "--profile",
    "-p",
    type=click.Choice(VALID_PROFILES),
    default="brownfield",
    help="Project profile.",
)
@click.option(
    "--flow",
    "-f",
    type=click.Choice(VALID_FLOWS),
    default="standard",
    help="Default workflow level.",
)
@click.option(
    "--lang",
    type=click.Choice(VALID_LANGS),
    default=None,
    help="Primary language (auto-detected from marker files if omitted).",
)
@click.option(
    "--output-lang",
    type=click.Choice(VALID_OUTPUT_LANGS),
    default="zh",
    help="Narrative output language for generated playbooks and docs "
    "(structural items — headings, frontmatter, Provenance, paths, "
    "IDs — always stay English). Default: zh.",
)
@click.option(
    "--script",
    type=click.Choice(["sh", "ps"]),
    default=None,
    help="Shell script type (auto-detected if omitted).",
)
@click.option(
    "--preset",
    "presets",
    multiple=True,
    type=click.Choice(VALID_PRESETS),
    help="Workflow presets (repeatable).",
)
@click.option("--force", is_flag=True, help="Overwrite existing files.")
@click.option("--no-git", is_flag=True, help="Skip git initialization.")
@click.option("--dry-run", is_flag=True, help="Show what would be generated without writing.")
def init(
    project: str,
    agents: tuple[str, ...],
    profile: str,
    flow: str,
    lang: str | None,
    output_lang: str,
    script: str | None,
    presets: tuple[str, ...],
    force: bool,
    no_git: bool,
    dry_run: bool,
) -> None:
    """Initialize harness in a repository.

    PROJECT is the target directory (defaults to current directory).
    """
    project_root = Path(project).resolve()
    if not project_root.exists():
        project_root.mkdir(parents=True)

    is_incremental = (project_root / HARNESS_DIR).exists()
    m = messages(output_lang)
    if is_incremental and not agents:
        console.print(f"[yellow]{m.already_initialized}[/yellow]")
        if not force:
            return

    if agents:
        agent_list = list(agents)
    elif _is_interactive():
        agent_list = _prompt_agents(m)
    else:
        agent_list = ["claude"]
    script_shell = script or _detect_shell()
    resolved_lang = lang or _detect_lang(project_root)

    if is_incremental and not force:
        from harness.core.config import load_config

        existing = load_config(project_root)
        # Existing config's output_lang is the source of truth on
        # incremental runs — never override the user's earlier choice.
        m = messages(existing.output_lang)
        new_agents = [a for a in agent_list if a not in existing.agents]
        if not new_agents:
            console.print(f"[yellow]{m.all_agents_already}[/yellow]")
            return
        existing.agents.extend(new_agents)
        config = existing
        console.print(f"[bold]{m.adding_agents.format(agents=', '.join(new_agents))}[/bold]")
    else:
        config = HarnessConfig(
            project_root=project_root,
            profile=profile,  # type: ignore[arg-type]
            flow=flow,  # type: ignore[arg-type]
            lang=resolved_lang,
            agents=agent_list,
            script_shell=script_shell,  # type: ignore[arg-type]
            presets=list(presets),
            output_lang=output_lang,  # type: ignore[arg-type]
        )

    template_dir = _get_template_dir()
    engine = ScaffoldEngine(template_dir)
    context = _build_context(config)

    if dry_run:
        console.print(f"[bold cyan]{m.dry_run_banner}[/bold cyan]\n")

    if not is_incremental or force:
        _generate_brain(engine, config, context, force=force, dry_run=dry_run)
        _generate_shared(engine, config, context, force=force, dry_run=dry_run)

    _generate_adapters(engine, config, context, force=force, dry_run=dry_run)

    if not dry_run:
        save_config(config)

    if not no_git and (not is_incremental or force):
        _init_git(project_root, engine, context, dry_run=dry_run)

    if not dry_run:
        _print_summary(config)
    else:
        console.print(f"\n[cyan]{m.dry_run_count.format(n=len(engine.generated_files))}[/cyan]")
