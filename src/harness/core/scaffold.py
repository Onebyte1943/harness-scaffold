"""Scaffold engine — renders Jinja2 templates to generate project files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console

console = Console()


class ScaffoldEngine:
    """Renders Jinja2 templates to generate harness project files."""

    def __init__(self, template_dir: Path) -> None:
        self._template_dir = template_dir
        self._env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape([]),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._generated: list[Path] = []

    @property
    def generated_files(self) -> list[Path]:
        return list(self._generated)

    def render_file(
        self,
        template_name: str,
        output_path: Path,
        context: dict[str, Any],
        *,
        force: bool = False,
        dry_run: bool = False,
        executable: bool = False,
    ) -> bool:
        """Render a single template to output_path. Returns True if file was written."""
        if output_path.exists() and not force:
            console.print(f"  [dim]skip[/dim] {output_path} (exists)")
            return False

        template = self._env.get_template(template_name)
        content = template.render(**context)

        if dry_run:
            console.print(f"  [cyan]would create[/cyan] {output_path}")
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        if executable:
            output_path.chmod(0o755)
        self._generated.append(output_path)
        console.print(f"  [green]create[/green] {output_path}")
        return True

    def render_static(
        self,
        content: str,
        output_path: Path,
        *,
        force: bool = False,
        dry_run: bool = False,
    ) -> bool:
        """Write static content (no template rendering)."""
        if output_path.exists() and not force:
            console.print(f"  [dim]skip[/dim] {output_path} (exists)")
            return False

        if dry_run:
            console.print(f"  [cyan]would create[/cyan] {output_path}")
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        self._generated.append(output_path)
        console.print(f"  [green]create[/green] {output_path}")
        return True

    def ensure_dir(
        self,
        path: Path,
        *,
        dry_run: bool = False,
        gitkeep: bool = True,
    ) -> None:
        """Create directory with optional .gitkeep for empty dirs."""
        if dry_run:
            if not path.exists():
                console.print(f"  [cyan]would create[/cyan] {path}/")
            return

        path.mkdir(parents=True, exist_ok=True)
        if gitkeep:
            keep = path / ".gitkeep"
            if not keep.exists() and not any(path.iterdir()):
                keep.touch()

    def has_template(self, template_name: str) -> bool:
        """Check if a template exists."""
        try:
            self._env.get_template(template_name)
            return True
        except Exception:
            return False

    def render_localized(
        self,
        template_stem: str,
        output_path: Path,
        context: dict[str, Any],
        *,
        force: bool = False,
        dry_run: bool = False,
        executable: bool = False,
    ) -> bool:
        """Render a translatable template.

        `template_stem` is the path without the language + extension suffix —
        e.g. `harness/playbooks/41-verify`. The engine resolves it to
        `<stem>.<output_lang>.md.j2` based on context["output_lang"]. Raises
        TemplateNotFound if neither variant exists.
        """
        output_lang = context.get("output_lang", "en")
        localized = f"{template_stem}.{output_lang}.md.j2"
        if not self.has_template(localized):
            raise FileNotFoundError(
                f"Localized template missing: {localized}. "
                f"Every translatable template must ship a .zh.md.j2 and a .en.md.j2 sibling."
            )
        return self.render_file(
            localized,
            output_path,
            context,
            force=force,
            dry_run=dry_run,
            executable=executable,
        )
