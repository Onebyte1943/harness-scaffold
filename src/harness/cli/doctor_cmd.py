"""harness doctor — 5-subsystem health check.

The doctor reports the project as a Harness OS (per AGENTS.md
§ Subsystems): five rows — Instructions, State, Verification, Scope,
Lifecycle — each rolled up to OK / WARN / FAIL with a short detail
string and any per-check sub-rows the user wants to see (`-v`).

Every individual check still produces a status tuple
`(status, item, detail)`, but the renderer now groups them under their
subsystem rather than dumping a flat list. This is a presentation
change first; the checks themselves are mostly the same as 0.2.x with
three additions for State/Verification/Lifecycle (init.sh present,
feature_list.json valid + ID parity, session-handoff.md freshness).
"""

from __future__ import annotations

import time
from collections import defaultdict
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from harness.core.config import HARNESS_DIR, detect_project_root, load_config
from harness.core.content_quality import (
    check_constitution_quality,
    check_doc_quality,
)
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
from harness.core.state import FeatureListError, find_feature_lists, has_cycle, load

console = Console()

AGENTS_MD_BUDGET = 32 * 1024  # 32 KiB (§12.4 A)
HANDOFF_STALE_SECONDS = 7 * 24 * 3600  # 7 days

# Subsystem labels per AGENTS.md § Subsystems.
INSTRUCTIONS = "Instructions"
STATE = "State"
VERIFICATION = "Verification"
SCOPE = "Scope"
LIFECYCLE = "Lifecycle"

CheckRow = tuple[str, str, str]  # (status, item, detail)
SubsystemRow = tuple[str, list[CheckRow]]


# --- Subsystem 1: Instructions ---------------------------------------


def _check_instructions(root: Path) -> list[CheckRow]:
    """AGENTS.md, CLAUDE.md, principle packs, constitution."""
    rows: list[CheckRow] = []

    agents_md = root / "AGENTS.md"
    if not agents_md.exists():
        rows.append(("error", "AGENTS.md", "Missing"))
    else:
        size = agents_md.stat().st_size
        if size > AGENTS_MD_BUDGET:
            rows.append(
                (
                    "warn",
                    "AGENTS.md",
                    f"Exceeds budget: {size // 1024} KiB > {AGENTS_MD_BUDGET // 1024} KiB",
                )
            )
        else:
            rows.append(("ok", "AGENTS.md", f"{size // 1024} KiB"))
        # 5-subsystem structure check — protects the contract surface.
        text = agents_md.read_text()
        for required in ("## 1. Instructions", "## 2. State", "## 3. Verification"):
            if required not in text:
                rows.append(
                    (
                        "warn",
                        "AGENTS.md",
                        f"Missing 5-subsystem section: {required}",
                    )
                )

    # Principle packs (Instructions feed material).
    generic = root / PRINCIPLE_PACKS_DIR / "generic.md"
    if generic.exists():
        rows.append(("ok", f"{PRINCIPLE_PACKS_DIR}/generic.md", "Found"))
    else:
        rows.append(("error", f"{PRINCIPLE_PACKS_DIR}/generic.md", "Missing"))

    # Constitution (lazy until /hx-constitution).
    constitution = root / CONSTITUTION_PATH
    if not constitution.exists():
        rows.append(("ok", CONSTITUTION_PATH, "Not yet created (run /hx-constitution)"))
    else:
        content = constitution.read_text().strip()
        lines = [
            line
            for line in content.splitlines()
            if line.strip() and not line.startswith("#") and not line.startswith(">")
        ]
        if len(lines) < 3:
            rows.append(
                (
                    "warn",
                    CONSTITUTION_PATH,
                    "Appears empty or minimal — re-run /hx-constitution",
                )
            )
        else:
            rows.append(("ok", CONSTITUTION_PATH, f"{len(lines)} content lines"))

        # spec-kit format checks (Version line, Governance, Sync Impact Report).
        rows.extend(check_constitution_quality(constitution))

    return rows


# --- Subsystem 2: State ---------------------------------------------


def _check_state(root: Path) -> list[CheckRow]:
    """feature_list.json per spec — schema + ID parity vs tasks.md."""
    rows: list[CheckRow] = []
    specs = root / SPECS_DIR
    if not specs.is_dir():
        rows.append(("ok", f"{SPECS_DIR}/", "Not yet created (lazy, by /hx-propose)"))
        return rows

    feature_lists = find_feature_lists(root)
    spec_dirs = [p for p in specs.iterdir() if p.is_dir()]

    if not spec_dirs:
        rows.append(("ok", f"{SPECS_DIR}/", "No spec dirs yet"))
        return rows

    # Per-spec: every spec with tasks.md should also have feature_list.json
    # with id parity.
    for spec in sorted(spec_dirs):
        tasks_md = spec / "tasks.md"
        feat_json = spec / "feature_list.json"
        rel = f"{SPECS_DIR}/{spec.name}"

        if not tasks_md.exists() and not feat_json.exists():
            # Pre-/hx-tasks: nothing to check.
            continue

        if tasks_md.exists() and not feat_json.exists():
            rows.append(
                (
                    "warn",
                    f"{rel}/feature_list.json",
                    "Missing — re-run /hx-tasks to generate State machine truth",
                )
            )
            continue
        if feat_json.exists() and not tasks_md.exists():
            rows.append(
                (
                    "warn",
                    f"{rel}/feature_list.json",
                    "Present but tasks.md missing — narrative out of sync",
                )
            )

        # Schema check.
        try:
            fl = load(feat_json)
        except FeatureListError as exc:
            rows.append(("error", f"{rel}/feature_list.json", str(exc)))
            continue

        # Cycle check.
        if has_cycle(fl.features):
            rows.append(("error", f"{rel}/feature_list.json", "depends_on graph has a cycle"))
        else:
            rows.append(("ok", f"{rel}/feature_list.json", f"{len(fl.features)} feature(s) valid"))

        # ID-parity check vs tasks.md (best effort — tokens like T1.1 in
        # markdown bullets). False positives possible if naming drifts;
        # we WARN rather than FAIL.
        if tasks_md.exists():
            md_text = tasks_md.read_text()
            json_ids = {f.id for f in fl.features}
            present = {fid for fid in json_ids if fid in md_text}
            missing = json_ids - present
            if missing:
                rows.append(
                    (
                        "warn",
                        f"{rel}",
                        f"feature_list.json ids not found in tasks.md: "
                        f"{', '.join(sorted(missing))}",
                    )
                )

    if not feature_lists:
        rows.append(
            (
                "ok",
                f"{SPECS_DIR}/*/feature_list.json",
                "No feature_list.json files yet (lazy, by /hx-tasks)",
            )
        )

    return rows


# --- Subsystem 3: Verification ---------------------------------------


def _check_verification(root: Path) -> list[CheckRow]:
    """init.sh, verify.sh, last-verify freshness, CI/pre-commit."""
    rows: list[CheckRow] = []

    try:
        config = load_config(root)
        shell = config.script_shell
    except FileNotFoundError:
        shell = "sh"

    # init.sh — entry script.
    init_name = "init.sh" if shell == "sh" else "init.ps1"
    init_path = root / init_name
    if not init_path.exists():
        rows.append(("error", init_name, "Missing — re-run harness init"))
    else:
        if shell == "sh":
            mode = init_path.stat().st_mode
            if not mode & 0o111:
                rows.append(
                    (
                        "warn",
                        init_name,
                        "Not executable — `chmod +x init.sh` or re-run harness init --force",
                    )
                )
            else:
                rows.append(("ok", init_name, "Executable"))
        else:
            rows.append(("ok", init_name, "Present"))

    # verify.sh.
    verify = (
        root / HARNESS_DIR / "scripts" / shell / ("verify.sh" if shell == "sh" else "verify.ps1")
    )
    if not verify.exists():
        rows.append(("error", str(verify.relative_to(root)), "Missing"))
    else:
        rows.append(("ok", str(verify.relative_to(root)), "Present"))

    # Last verify status (lazy: only present after init.sh runs).
    last = root / HARNESS_DIR / ".last-verify.json"
    if last.exists():
        try:
            import json as _json

            data = _json.loads(last.read_text())
            ts = data.get("timestamp")
            status = data.get("status", "unknown")
            if isinstance(ts, (int, float)):
                age = int(time.time() - ts)
                if age < 60:
                    age_str = f"{age}s ago"
                elif age < 3600:
                    age_str = f"{age // 60}m ago"
                else:
                    age_str = f"{age // 3600}h ago"
            else:
                age_str = "unknown age"
            level = "ok" if status == "green" else "warn"
            rows.append(
                (
                    level,
                    f"{HARNESS_DIR}/.last-verify.json",
                    f"{status} ({age_str})",
                )
            )
        except (ValueError, OSError) as exc:
            rows.append(
                (
                    "warn",
                    f"{HARNESS_DIR}/.last-verify.json",
                    f"Unparseable: {exc}",
                )
            )
    else:
        rows.append(
            (
                "ok",
                f"{HARNESS_DIR}/.last-verify.json",
                "Not yet recorded (run ./init.sh)",
            )
        )

    # CI + pre-commit (also Verification-layer sensors).
    for label, rel in (
        ("GitLab CI", GITLAB_CI_CONFIG),
        ("pre-commit", PRE_COMMIT_CONFIG),
    ):
        path = root / rel
        if path.exists():
            rows.append(("ok", rel, "Found"))
        else:
            rows.append(("error", rel, f"Missing ({label})"))

    return rows


# --- Subsystem 4: Scope ---------------------------------------------


def _check_scope(root: Path) -> list[CheckRow]:
    """Knowledge base, ADRs, agent dir, templates — define & evidence the
    boundaries the agent must respect."""
    rows: list[CheckRow] = []

    knowledge_root = root / KNOWLEDGE_DIR
    if knowledge_root.is_dir():
        present = [doc for doc in KNOWLEDGE_DOCS if (knowledge_root / f"{doc}.md").exists()]
        missing = [f"{doc}.md" for doc in KNOWLEDGE_DOCS if doc not in present]
        if not present:
            rows.append(
                (
                    "ok",
                    f"{KNOWLEDGE_DIR}/",
                    "Not yet populated (lazy, by /hx-baseline)",
                )
            )
        elif missing:
            rows.append(
                (
                    "warn",
                    f"{KNOWLEDGE_DIR}/",
                    f"Incomplete: {len(present)}/{len(KNOWLEDGE_DOCS)} docs present, "
                    f"missing {', '.join(missing[:3])}"
                    f"{'…' if len(missing) > 3 else ''} — re-run /hx-baseline",
                )
            )
        else:
            rows.append(
                (
                    "ok",
                    f"{KNOWLEDGE_DIR}/",
                    f"All {len(KNOWLEDGE_DOCS)} core docs present",
                )
            )
        # Per-doc content-quality checks (cite-density, required-sections,
        # structure-form). Skips files that are not present.
        for doc in present:
            rows.extend(check_doc_quality(knowledge_root / f"{doc}.md"))
        howto = root / KNOWLEDGE_HOWTO_DIR
        if howto.is_dir():
            n = len(list(howto.glob("*.md")))
            rows.append(("ok", f"{KNOWLEDGE_HOWTO_DIR}/", f"{n} recipe(s)"))
    else:
        rows.append(
            (
                "ok",
                f"{KNOWLEDGE_DIR}/",
                "Not yet populated (lazy, by /hx-baseline)",
            )
        )

    adr = root / ADR_DIR
    if adr.is_dir():
        rows.append(("ok", f"{ADR_DIR}/", "Found"))
    else:
        rows.append(("ok", f"{ADR_DIR}/", "Not yet created (lazy, by /hx-plan)"))

    templates = root / TEMPLATES_DIR
    if templates.is_dir():
        n = len(list(templates.glob("*")))
        rows.append(("ok", f"{TEMPLATES_DIR}/", f"{n} project-local override(s)"))

    # Evals seed (boundary evidence for `harness doctor`-style regressions).
    evals_readme = root / EVALS_DIR / "README.md"
    if evals_readme.exists():
        rows.append(("ok", f"{EVALS_DIR}/README.md", "Found"))
    else:
        rows.append(("warn", f"{EVALS_DIR}/README.md", "Missing (seed format guide)"))

    # Legacy v1 layout warnings — treated as scope contamination.
    if (root / LEGACY_ARTIFACTS_DIR).exists():
        rows.append(
            (
                "warn",
                f"{LEGACY_ARTIFACTS_DIR}/",
                "Legacy v1 layout detected — design v3 moved artifacts to specs/ "
                "and .harness/knowledge/; review and remove or merge",
            )
        )
    if (root / LEGACY_CONSTITUTION_PATH).exists():
        rows.append(
            (
                "warn",
                LEGACY_CONSTITUTION_PATH,
                f"Legacy location — design v3 expects {CONSTITUTION_PATH}",
            )
        )

    return rows


# --- Subsystem 5: Lifecycle -----------------------------------------


def _check_lifecycle(root: Path) -> list[CheckRow]:
    """progress.md, .agent/, session-handoff.md per active spec."""
    rows: list[CheckRow] = []

    progress = root / PROGRESS_PATH
    if progress.exists():
        rows.append(("ok", PROGRESS_PATH, "Found"))
    else:
        rows.append(("ok", PROGRESS_PATH, "Not yet created (lazy, by /hx-implement)"))

    agent_dir = root / AGENT_DIR
    if agent_dir.is_dir():
        rows.append(("ok", f"{AGENT_DIR}/", "Found"))
    else:
        rows.append(("warn", f"{AGENT_DIR}/", "Missing (re-run harness init)"))

    # Per-spec session-handoff.md: present? stale (>7d)?
    specs = root / SPECS_DIR
    if specs.is_dir():
        for spec in sorted(p for p in specs.iterdir() if p.is_dir()):
            handoff = spec / "session-handoff.md"
            rel = f"{SPECS_DIR}/{spec.name}/session-handoff.md"
            if not handoff.exists():
                # If feature_list.json exists for this spec, the agent has
                # been working on it — handoff should exist too.
                if (spec / "feature_list.json").exists():
                    rows.append(("warn", rel, "Missing — write at session end"))
                else:
                    # Pre-/hx-implement: it's reasonable not to have one yet.
                    rows.append(("ok", rel, "Not yet written"))
                continue
            age = int(time.time() - handoff.stat().st_mtime)
            if age > HANDOFF_STALE_SECONDS:
                days = age // (24 * 3600)
                rows.append(("warn", rel, f"Stale ({days}d) — overwrite at session end"))
            else:
                if age < 60:
                    age_str = f"{age}s ago"
                elif age < 3600:
                    age_str = f"{age // 60}m ago"
                elif age < 86400:
                    age_str = f"{age // 3600}h ago"
                else:
                    age_str = f"{age // 86400}d ago"
                rows.append(("ok", rel, f"Updated {age_str}"))

    return rows


# --- Adapter checks (cross-subsystem; reported under Instructions) ---


def _check_adapters(root: Path) -> list[CheckRow]:
    rows: list[CheckRow] = []
    try:
        config = load_config(root)
    except FileNotFoundError:
        rows.append(("error", "config", "Cannot load harness config"))
        return rows

    from harness.adapters import get_adapter
    from harness.core.scaffold import ScaffoldEngine

    template_dir = Path(__file__).parent.parent / "templates"
    engine = ScaffoldEngine(template_dir)

    for agent_name in config.agents:
        try:
            adapter = get_adapter(agent_name, engine)
            issues = adapter.validate(root)
            if issues:
                for issue in issues:
                    rows.append(("warn", f"{agent_name} adapter", issue))
            else:
                rows.append(("ok", f"{agent_name} adapter", "All files present"))
        except KeyError:
            rows.append(("warn", f"{agent_name} adapter", "No adapter implementation"))
    return rows


# --- Roll-up & rendering --------------------------------------------


def _rollup(rows: list[CheckRow]) -> tuple[str, int, int, int]:
    """Reduce a subsystem's rows to (worst-status, ok, warn, error)."""
    ok = sum(1 for s, _, _ in rows if s == "ok")
    warn = sum(1 for s, _, _ in rows if s == "warn")
    err = sum(1 for s, _, _ in rows if s == "error")
    if err:
        worst = "error"
    elif warn:
        worst = "warn"
    else:
        worst = "ok"
    return worst, ok, warn, err


def _resolve_output_lang(root: Path) -> str:
    try:
        return load_config(root).output_lang
    except Exception:
        return "en"


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Show all checks including passing.")
def doctor(verbose: bool) -> None:
    """Check harness integrity, organized by the 5 subsystems."""
    root = detect_project_root()
    if root is None:
        m = messages("en")
        console.print(f"[red]{m.doctor_not_in_project}[/red]")
        raise SystemExit(1)

    m = messages(_resolve_output_lang(root))
    console.print(f"[bold]{m.doctor_header.format(name=root.name)}[/bold]\n")

    # Collect per-subsystem rows.
    by_subsystem: dict[str, list[CheckRow]] = defaultdict(list)
    by_subsystem[INSTRUCTIONS] = _check_instructions(root) + _check_adapters(root)
    by_subsystem[STATE] = _check_state(root)
    by_subsystem[VERIFICATION] = _check_verification(root)
    by_subsystem[SCOPE] = _check_scope(root)
    by_subsystem[LIFECYCLE] = _check_lifecycle(root)

    icons = {
        "ok": f"[green]{m.doctor_ok}[/green]",
        "warn": f"[yellow]{m.doctor_warn}[/yellow]",
        "error": f"[red]{m.doctor_fail}[/red]",
    }

    # Top-level subsystem summary table (always shown).
    summary = Table(show_header=True, header_style="bold cyan")
    summary.add_column("Subsystem", style="bold")
    summary.add_column("Status", width=8)
    summary.add_column("Detail")

    total_err = 0
    total_warn = 0
    for sub in (INSTRUCTIONS, STATE, VERIFICATION, SCOPE, LIFECYCLE):
        rows = by_subsystem[sub]
        worst, ok, warn, err = _rollup(rows)
        total_err += err
        total_warn += warn
        detail = f"{ok} OK · {warn} WARN · {err} FAIL" if rows else "no checks ran"
        summary.add_row(sub, icons[worst], detail)

    console.print(summary)

    # Per-subsystem detail table — verbose shows all; otherwise only
    # rows that are not OK.
    detail_table = Table(show_header=True, header_style="bold")
    detail_table.add_column("Subsystem", width=14)
    detail_table.add_column(m.doctor_table_status, width=6)
    detail_table.add_column(m.doctor_table_item)
    detail_table.add_column(m.doctor_table_detail)

    have_detail_rows = False
    for sub in (INSTRUCTIONS, STATE, VERIFICATION, SCOPE, LIFECYCLE):
        for status, item, det in by_subsystem[sub]:
            if not verbose and status == "ok":
                continue
            detail_table.add_row(sub, icons[status], item, det)
            have_detail_rows = True

    if have_detail_rows:
        console.print()
        console.print(detail_table)

    console.print()
    if total_err > 0:
        msg = m.doctor_summary_errors.format(errors=total_err, warnings=total_warn)
        console.print(f"[red bold]{msg}[/red bold]")
        raise SystemExit(1)
    elif total_warn > 0:
        console.print(f"[green]{m.doctor_summary_warnings.format(warnings=total_warn)}[/green]")
    else:
        console.print(f"[green bold]{m.doctor_all_passed}[/green bold]")
