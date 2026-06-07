"""harness init — Initialize harness in a repository (design v2)."""

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
VALID_PROFILES = ["brownfield", "greenfield"]
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


def _prompt_agents() -> list[str]:
    try:
        import questionary
    except ImportError:
        return ["claude"]

    try:
        result = questionary.checkbox(
            "Select AI agent terminals to support:",
            choices=[
                questionary.Choice("Claude Code", value="claude", checked=True),
                questionary.Choice("Codex CLI", value="codex"),
                questionary.Choice("Cursor (via registry, not bundled)", value="cursor"),
                questionary.Choice("Copilot (via registry, not bundled)", value="copilot"),
                questionary.Choice("Gemini CLI (via registry, not bundled)", value="gemini"),
            ],
        ).ask()
    except (KeyboardInterrupt, EOFError):
        return ["claude"]
    return result if result else ["claude"]


def _get_template_dir() -> Path:
    return Path(__file__).parent.parent / "templates"


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
    console.print("\n[bold]Generating .harness/ brain...[/bold]")
    root = config.project_root
    harness = root / HARNESS_DIR

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
        template_stem = f"harness/playbooks/{pb_filename}"
        engine.render_localized(
            template_stem,
            harness / "playbooks" / f"{pb_filename}.md",
            context,
            force=force,
            dry_run=dry_run,
        )

    engine.render_localized(
        "harness/principle-packs/generic",
        harness / "principle-packs" / "generic.md",
        context,
        force=force,
        dry_run=dry_run,
    )

    engine.render_localized(
        "harness/evals/README",
        harness / "evals" / "README.md",
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
    console.print("\n[bold]Generating shared contract layer...[/bold]")
    root = config.project_root

    engine.render_localized(
        "shared/AGENTS",
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

    for agent_name in config.agents:
        console.print(f"\n[bold]Generating {agent_name} adapter...[/bold]")
        try:
            adapter = get_adapter(agent_name, engine)
            adapter.generate(config.project_root, context, force=force, dry_run=dry_run)
        except KeyError:
            console.print(
                f"  [yellow]warning[/yellow] No adapter implementation for '{agent_name}', skipping"
            )


def _init_git(
    project_root: Path,
    engine: ScaffoldEngine,
    context: dict[str, Any],
    *,
    dry_run: bool = False,
) -> None:
    """Initialize git repo if not already in one."""
    if (project_root / ".git").exists():
        return

    if dry_run:
        console.print("  [cyan]would run[/cyan] git init")
        return

    try:
        subprocess.run(["git", "init"], cwd=project_root, capture_output=True, check=True)
        console.print("  [green]git init[/green]")
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("  [yellow]warning[/yellow] git not available, skipping git init")

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
                console.print("  [green]append[/green] .gitignore")
        else:
            engine.render_file("shared/gitignore.j2", gitignore_path, context)


def _print_summary(config: HarnessConfig) -> None:
    """Print initialization summary."""
    table = Table(title="Harness Initialized", show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="bold")
    table.add_column("Value")
    table.add_row("Project", config.project_root.name)
    table.add_row("Profile", config.profile)
    table.add_row("Flow", config.flow)
    table.add_row("Lang", config.lang)
    table.add_row("Output-Lang", config.output_lang)
    table.add_row("Agents", ", ".join(config.agents))
    table.add_row("Shell", config.script_shell)
    if config.presets:
        table.add_row("Presets", ", ".join(config.presets))
    console.print()
    console.print(table)
    console.print()
    console.print(
        Panel(
            "[bold]Next steps:[/bold]\n"
            "  1. Run [cyan]/hx-constitution[/cyan] to synthesize "
            "engineering principles\n"
            "  2. Run [cyan]/hx-baseline[/cyan] to build the 8-doc knowledge base\n"
            "  3. Run [cyan]/hx-next[/cyan] when in doubt about the next move\n"
            "  4. Run [cyan]harness doctor[/cyan] to verify setup",
            title="W0 Bootstrap",
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
    if is_incremental and not agents:
        console.print(
            "[yellow]Harness already initialized.[/yellow] "
            "Use --agent to add a new terminal adapter, or --force to "
            "re-render the brain."
        )
        if not force:
            return

    agent_list = list(agents) if agents else (_prompt_agents() if _is_interactive() else ["claude"])
    script_shell = script or _detect_shell()
    resolved_lang = lang or _detect_lang(project_root)

    if is_incremental and not force:
        from harness.core.config import load_config

        existing = load_config(project_root)
        new_agents = [a for a in agent_list if a not in existing.agents]
        if not new_agents:
            console.print("[yellow]All requested agents already configured.[/yellow]")
            return
        existing.agents.extend(new_agents)
        config = existing
        console.print(f"[bold]Adding agent(s): {', '.join(new_agents)}[/bold]")
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
        console.print("[bold cyan]DRY RUN — no files will be written[/bold cyan]\n")

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
        console.print(f"\n[cyan]Would generate {len(engine.generated_files)} files[/cyan]")
