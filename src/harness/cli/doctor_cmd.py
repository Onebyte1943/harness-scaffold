"""harness doctor — Self-check harness integrity (design v3)."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from harness.core.config import HARNESS_DIR, detect_project_root, load_config
from harness.core.i18n import messages
from harness.core.layout import (
    ADR_DIR,
    AGENT_DIR,
    CONSTITUTION_PATH,
    EVALS_DIR,
    GITLAB_CI_CONFIG,
    KNOWLEDGE_DIR,
    KNOWLEDGE_DOCS,
    KNOWLEDGE_HOWTO_DIR,
    LEGACY_ARTIFACTS_DIR,
    LEGACY_CONSTITUTION_PATH,
    PRE_COMMIT_CONFIG,
    PRINCIPLE_PACKS_DIR,
    PROGRESS_PATH,
    SPECS_DIR,
    TEMPLATES_DIR,
)

console = Console()

AGENTS_MD_BUDGET = 32 * 1024  # 32 KiB (§12.4 A)

# Files materialized eagerly by `harness init`.
REQUIRED_HARNESS_FILES = [
    "config.toml",
    "registry.toml",
]

# Directories materialized eagerly under .harness/.
REQUIRED_HARNESS_DIRS = [
    "playbooks",
    "scripts",
    "principle-packs",
    "evals",
    "memory",
    "knowledge",
    "templates",
]


def _check_harness_structure(project_root: Path) -> list[tuple[str, str, str]]:
    """Check .harness/ directory completeness."""
    results: list[tuple[str, str, str]] = []
    harness_dir = project_root / HARNESS_DIR

    if not harness_dir.exists():
        results.append(("error", ".harness/", "Directory not found"))
        return results

    results.append(("ok", ".harness/", "Directory exists"))

    for f in REQUIRED_HARNESS_FILES:
        path = harness_dir / f
        if path.exists():
            results.append(("ok", f".harness/{f}", "Found"))
        else:
            results.append(("error", f".harness/{f}", "Missing"))

    for d in REQUIRED_HARNESS_DIRS:
        path = harness_dir / d
        if path.is_dir():
            count = len(list(path.glob("*")))
            results.append(("ok", f".harness/{d}/", f"{count} entries"))
        else:
            results.append(("error", f".harness/{d}/", "Missing"))

    # Principle packs: at minimum the generic pack must exist.
    generic = project_root / PRINCIPLE_PACKS_DIR / "generic.md"
    if generic.exists():
        results.append(("ok", f"{PRINCIPLE_PACKS_DIR}/generic.md", "Found"))
    else:
        results.append(("error", f"{PRINCIPLE_PACKS_DIR}/generic.md", "Missing"))

    # Evals seed (informational; absence is fine until baseline runs)
    evals_readme = project_root / EVALS_DIR / "README.md"
    if evals_readme.exists():
        results.append(("ok", f"{EVALS_DIR}/README.md", "Found"))
    else:
        results.append(("warn", f"{EVALS_DIR}/README.md", "Missing (seed format guide)"))

    return results


def _check_contract_layer(project_root: Path) -> list[tuple[str, str, str]]:
    """Check shared agent contract + CI + pre-commit + L-RULE/L-STATE."""
    results: list[tuple[str, str, str]] = []

    agents_md = project_root / "AGENTS.md"
    if agents_md.exists():
        size = agents_md.stat().st_size
        if size > AGENTS_MD_BUDGET:
            results.append(
                (
                    "warn",
                    "AGENTS.md",
                    f"Exceeds budget: {size // 1024} KiB > {AGENTS_MD_BUDGET // 1024} KiB",
                )
            )
        else:
            results.append(("ok", "AGENTS.md", f"{size // 1024} KiB"))
    else:
        results.append(("error", "AGENTS.md", "Missing"))

    # GitLab CI + pre-commit are eager-init.
    for label, rel in (
        ("GitLab CI", GITLAB_CI_CONFIG),
        ("pre-commit", PRE_COMMIT_CONFIG),
    ):
        path = project_root / rel
        if path.exists():
            results.append(("ok", rel, "Found"))
        else:
            results.append(("error", rel, f"Missing ({label})"))

    # Constitution (L-RULE) — lazy: created by /hx-constitution.
    constitution = project_root / CONSTITUTION_PATH
    if constitution.exists():
        content = constitution.read_text().strip()
        lines = [
            line
            for line in content.splitlines()
            if line.strip() and not line.startswith("#") and not line.startswith(">")
        ]
        if len(lines) < 3:
            results.append(
                (
                    "warn",
                    CONSTITUTION_PATH,
                    "Appears empty or minimal — re-run /hx-constitution",
                )
            )
        else:
            results.append(("ok", CONSTITUTION_PATH, f"{len(lines)} content lines"))
    else:
        results.append(("ok", CONSTITUTION_PATH, "Not yet created (run /hx-constitution)"))

    # Knowledge docs (L-STATE) — lazy: created by /hx-baseline.
    knowledge_root = project_root / KNOWLEDGE_DIR
    if knowledge_root.is_dir():
        present = [doc for doc in KNOWLEDGE_DOCS if (knowledge_root / f"{doc}.md").exists()]
        missing = [f"{doc}.md" for doc in KNOWLEDGE_DOCS if doc not in present]
        if not present:
            # Empty knowledge dir post-init is the normal state — not a warning.
            results.append(
                (
                    "ok",
                    f"{KNOWLEDGE_DIR}/",
                    "Not yet populated (lazy, by /hx-baseline)",
                )
            )
        elif missing:
            results.append(
                (
                    "warn",
                    f"{KNOWLEDGE_DIR}/",
                    f"Incomplete: {len(present)}/{len(KNOWLEDGE_DOCS)} docs present, "
                    f"missing {', '.join(missing[:3])}"
                    f"{'…' if len(missing) > 3 else ''} — re-run /hx-baseline",
                )
            )
        else:
            results.append(
                (
                    "ok",
                    f"{KNOWLEDGE_DIR}/",
                    f"All {len(KNOWLEDGE_DOCS)} core docs present",
                )
            )
        howto = project_root / KNOWLEDGE_HOWTO_DIR
        if howto.is_dir():
            n = len(list(howto.glob("*.md")))
            results.append(("ok", f"{KNOWLEDGE_HOWTO_DIR}/", f"{n} recipe(s)"))
    else:
        results.append(
            (
                "ok",
                f"{KNOWLEDGE_DIR}/",
                "Not yet populated (lazy, by /hx-baseline)",
            )
        )

    # Per-change specs + ADRs + progress log are lazy.
    for d, creator in (
        (SPECS_DIR, "/hx-propose"),
        (ADR_DIR, "/hx-plan"),
    ):
        path = project_root / d
        if path.is_dir():
            results.append(("ok", f"{d}/", "Found"))
        else:
            results.append(("ok", f"{d}/", f"Not yet created (lazy, by {creator})"))

    progress = project_root / PROGRESS_PATH
    if progress.exists():
        results.append(("ok", PROGRESS_PATH, "Found"))
    else:
        results.append(("ok", PROGRESS_PATH, "Not yet created (lazy, by /hx-implement)"))

    agent_dir = project_root / AGENT_DIR
    if agent_dir.is_dir():
        results.append(("ok", f"{AGENT_DIR}/", "Found"))
    else:
        results.append(("warn", f"{AGENT_DIR}/", "Missing (re-run harness init)"))

    templates_dir = project_root / TEMPLATES_DIR
    if templates_dir.is_dir():
        n = len(list(templates_dir.glob("*")))
        results.append(("ok", f"{TEMPLATES_DIR}/", f"{n} project-local override(s)"))

    return results


def _check_legacy_layout(project_root: Path) -> list[tuple[str, str, str]]:
    """Surface the v1 layout — design v3 doesn't migrate, just warns."""
    results: list[tuple[str, str, str]] = []
    if (project_root / LEGACY_ARTIFACTS_DIR).exists():
        results.append(
            (
                "warn",
                f"{LEGACY_ARTIFACTS_DIR}/",
                "Legacy v1 layout detected — design v3 moved artifacts to "
                "specs/ and .harness/knowledge/; review and remove or merge",
            )
        )
    if (project_root / LEGACY_CONSTITUTION_PATH).exists():
        results.append(
            (
                "warn",
                LEGACY_CONSTITUTION_PATH,
                f"Legacy location — design v3 expects {CONSTITUTION_PATH}",
            )
        )
    return results


def _check_adapters(project_root: Path) -> list[tuple[str, str, str]]:
    """Check adapter file integrity."""
    results: list[tuple[str, str, str]] = []

    try:
        config = load_config(project_root)
    except FileNotFoundError:
        results.append(("error", "config", "Cannot load harness config"))
        return results

    from harness.adapters import get_adapter
    from harness.core.scaffold import ScaffoldEngine

    template_dir = Path(__file__).parent.parent / "templates"
    engine = ScaffoldEngine(template_dir)

    for agent_name in config.agents:
        try:
            adapter = get_adapter(agent_name, engine)
            issues = adapter.validate(project_root)
            if issues:
                for issue in issues:
                    results.append(("warn", f"{agent_name} adapter", issue))
            else:
                results.append(("ok", f"{agent_name} adapter", "All files present"))
        except KeyError:
            results.append(("warn", f"{agent_name} adapter", "No adapter implementation"))

    return results


def _resolve_output_lang(root: Path) -> str:
    """Read the project's output_lang from .harness/config.toml. Falls
    back to `en` if config is unreadable — doctor never crashes on a
    misconfigured project just to print its own diagnostics."""
    try:
        return load_config(root).output_lang
    except Exception:
        return "en"


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Show all checks including passing.")
def doctor(verbose: bool) -> None:
    """Check harness integrity and report issues."""
    root = detect_project_root()
    if root is None:
        # No project context, so no config to read — default to en for
        # this one diagnostic message.
        m = messages("en")
        console.print(f"[red]{m.doctor_not_in_project}[/red]")
        raise SystemExit(1)

    m = messages(_resolve_output_lang(root))
    console.print(f"[bold]{m.doctor_header.format(name=root.name)}[/bold]\n")

    all_results: list[tuple[str, str, str]] = []
    all_results.extend(_check_harness_structure(root))
    all_results.extend(_check_contract_layer(root))
    all_results.extend(_check_legacy_layout(root))
    all_results.extend(_check_adapters(root))

    table = Table(show_header=True, header_style="bold")
    table.add_column(m.doctor_table_status, width=6)
    table.add_column(m.doctor_table_item)
    table.add_column(m.doctor_table_detail)

    icons = {
        "ok": f"[green]{m.doctor_ok}[/green]",
        "warn": f"[yellow]{m.doctor_warn}[/yellow]",
        "error": f"[red]{m.doctor_fail}[/red]",
    }
    errors = 0
    warnings = 0

    for status, item, detail in all_results:
        if status == "error":
            errors += 1
        elif status == "warn":
            warnings += 1
        if verbose or status != "ok":
            table.add_row(icons[status], item, detail)

    if verbose or errors > 0 or warnings > 0:
        console.print(table)

    console.print()
    if errors > 0:
        summary = m.doctor_summary_errors.format(errors=errors, warnings=warnings)
        console.print(f"[red bold]{summary}[/red bold]")
        raise SystemExit(1)
    elif warnings > 0:
        console.print(f"[green]{m.doctor_summary_warnings.format(warnings=warnings)}[/green]")
    else:
        console.print(f"[green bold]{m.doctor_all_passed}[/green bold]")
