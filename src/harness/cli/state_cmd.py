"""harness state — Subsystem 2 (State) CLI command group.

Three subcommands per AGENTS.md § 2.3:

- `harness state show [spec-id]` — render the feature list table for a
  spec; defaults to the most-recently-modified spec.
- `harness state next` — print the next executable feature (per the
  Resume → Advance contract).
- `harness state pass <feat-id> --evidence <ref>` — flip status to
  `passing`. Refuses unless the feature's `verification` command ran
  green within the last 5 minutes (recorded in
  `.harness/.last-verify.json`).

The 5-minute freshness window is the harness analogue of `make test &&
git commit`: the commit only stands if the test was just green. Stale
verify ⇒ go re-run it; the agent doesn't get to claim a feature done
on yesterday's lunch.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from harness.core.config import HARNESS_DIR
from harness.core.state import (
    FeatureList,
    FeatureListError,
    FeatureStatus,
    load,
)

console = Console()

VERIFY_FRESHNESS_SECONDS = 300  # 5 minutes


def _project_root() -> Path:
    """Walk up looking for `.harness/`. Mirrors doctor_cmd's resolver."""
    cur = Path.cwd().resolve()
    for candidate in (cur, *cur.parents):
        if (candidate / HARNESS_DIR).is_dir():
            return candidate
    raise click.ClickException("Not in a harness project. Run `harness init` first.")


def _resolve_spec(root: Path, spec_id: str | None) -> tuple[str, Path]:
    """Return (spec-dir-name, feature_list.json path) for spec_id, or
    fall back to the most-recently-modified spec dir under specs/."""
    specs = root / "specs"
    if not specs.is_dir():
        raise click.ClickException("No specs/ directory yet — run /hx-propose to start a change.")

    if spec_id:
        # Accept either "001" or "001-auth" or full dir name.
        candidates = [p for p in specs.iterdir() if p.is_dir() and p.name.startswith(spec_id)]
        if not candidates:
            raise click.ClickException(f"No spec dir matching '{spec_id}' under specs/")
        chosen = candidates[0]
    else:
        spec_dirs = sorted(
            (p for p in specs.iterdir() if p.is_dir()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not spec_dirs:
            raise click.ClickException("specs/ exists but has no spec dirs yet.")
        chosen = spec_dirs[0]

    fl_path = chosen / "feature_list.json"
    if not fl_path.exists():
        raise click.ClickException(f"{chosen.name}/feature_list.json not found — re-run /hx-tasks.")
    return chosen.name, fl_path


def _read_feature_list(path: Path) -> FeatureList:
    try:
        return load(path)
    except FeatureListError as exc:
        raise click.ClickException(str(exc)) from exc


def _last_verify(root: Path) -> dict[str, Any] | None:
    """Read .harness/.last-verify.json. Missing or unparseable ⇒ None."""
    p = root / HARNESS_DIR / ".last-verify.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


@click.group()
def state() -> None:
    """Inspect or update Subsystem 2 (State): feature_list.json."""


@state.command("show")
@click.argument("spec_id", required=False)
def state_show(spec_id: str | None) -> None:
    """Render the feature_list.json table for a spec."""
    root = _project_root()
    spec_name, fl_path = _resolve_spec(root, spec_id)
    fl = _read_feature_list(fl_path)

    table = Table(
        title=f"State — {spec_name}",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("ID", style="bold")
    table.add_column("Name")
    table.add_column("Depends on")
    table.add_column("Status")
    table.add_column("Evidence", overflow="fold")

    status_style = {
        FeatureStatus.NOT_STARTED: "dim",
        FeatureStatus.IN_PROGRESS: "yellow",
        FeatureStatus.PASSING: "green",
    }
    for f in fl.features:
        table.add_row(
            f.id,
            f.name,
            ", ".join(f.depends_on) or "—",
            f"[{status_style[f.status]}]{f.status.value}[/]",
            f.evidence or "—",
        )
    console.print(table)


@state.command("next")
@click.argument("spec_id", required=False)
def state_next(spec_id: str | None) -> None:
    """Print the next executable feature for a spec."""
    root = _project_root()
    spec_name, fl_path = _resolve_spec(root, spec_id)
    fl = _read_feature_list(fl_path)

    nxt = fl.next_executable()
    if nxt is None:
        console.print(f"[green]{spec_name}: all features passing.[/green]")
        return

    console.print(f"[bold]Next executable in {spec_name}:[/bold] {nxt.id} — {nxt.name}")
    console.print(f"  status      : {nxt.status.value}")
    console.print(f"  depends_on  : {', '.join(nxt.depends_on) or '—'}")
    console.print(f"  verification: [cyan]{nxt.verification}[/cyan]")


@state.command("pass")
@click.argument("feat_id")
@click.option(
    "--evidence",
    required=True,
    help="Proof of pass: commit SHA, test snippet, or path:line citation.",
)
@click.option("--spec", "spec_id", help="Target spec id; defaults to most-recent.")
@click.option(
    "--force",
    is_flag=True,
    help="Skip the 5-minute verify-freshness check (use sparingly).",
)
def state_pass(feat_id: str, evidence: str, spec_id: str | None, force: bool) -> None:
    """Flip a feature's status to `passing`.

    Refuses unless `verify.sh` ran green within the last 5 minutes,
    unless --force is given. The freshness signal lives in
    `.harness/.last-verify.json` (init.sh writes it on green exit).
    """
    root = _project_root()
    spec_name, fl_path = _resolve_spec(root, spec_id)
    fl = _read_feature_list(fl_path)

    feat = fl.by_id(feat_id)
    if feat is None:
        raise click.ClickException(f"No feature '{feat_id}' in {spec_name}.")
    if feat.status is FeatureStatus.PASSING:
        console.print(f"[yellow]{feat_id} already passing.[/yellow]")
        return

    # Dependency gate.
    by_id = {f.id: f for f in fl.features}
    unmet = [d for d in feat.depends_on if by_id[d].status is not FeatureStatus.PASSING]
    if unmet:
        raise click.ClickException(
            f"Cannot pass {feat_id} — unmet dependencies: {', '.join(unmet)}"
        )

    # Verify-freshness gate.
    if not force:
        last = _last_verify(root)
        if last is None:
            raise click.ClickException(
                "No verify run recorded in .harness/.last-verify.json. "
                "Run `./init.sh` (which calls verify.sh) before claiming pass, "
                "or pass --force if you have a reason."
            )
        if last.get("status") != "green":
            raise click.ClickException(
                f"Last verify was '{last.get('status')}', not green. "
                "Re-run `./init.sh` until it passes."
            )
        ts = last.get("timestamp")
        if not isinstance(ts, (int, float)) or time.time() - ts > VERIFY_FRESHNESS_SECONDS:
            raise click.ClickException(
                f"Last verify is older than {VERIFY_FRESHNESS_SECONDS}s. "
                "Re-run `./init.sh` and try again."
            )

    # Patch the JSON in place. Preserve key order by round-tripping
    # through the parsed structure rather than rebuilding from the
    # dataclass (which has its own field order).
    raw = json.loads(fl_path.read_text())
    for entry in raw["features"]:
        if entry["id"] == feat_id:
            entry["status"] = FeatureStatus.PASSING.value
            entry["evidence"] = evidence
            break
    fl_path.write_text(json.dumps(raw, indent=2) + "\n")

    console.print(f"[green]✓ {feat_id} passing[/green] · evidence: {evidence}")

    # Re-read to drive next-executable hint.
    fl_after = _read_feature_list(fl_path)
    nxt = fl_after.next_executable()
    if nxt:
        console.print(f"  next        : [cyan]{nxt.id}[/cyan] — {nxt.name}")
    else:
        console.print(f"  [green]all features in {spec_name} passing.[/green]")


__all__ = ["state"]
