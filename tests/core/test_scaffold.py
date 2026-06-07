"""Tests for core/scaffold.py."""

from __future__ import annotations

from pathlib import Path

from harness.core.scaffold import ScaffoldEngine


class TestScaffoldEngine:
    def _make_template_dir(self, tmp_path: Path) -> Path:
        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        (tmpl_dir / "hello.txt.j2").write_text("Hello {{ name }}!\n")
        return tmpl_dir

    def test_render_file(self, tmp_path: Path) -> None:
        tmpl_dir = self._make_template_dir(tmp_path)
        engine = ScaffoldEngine(tmpl_dir)
        out = tmp_path / "output" / "hello.txt"
        engine.render_file("hello.txt.j2", out, {"name": "World"})
        assert out.read_text() == "Hello World!\n"
        assert out in engine.generated_files

    def test_render_file_skip_existing(self, tmp_path: Path) -> None:
        tmpl_dir = self._make_template_dir(tmp_path)
        engine = ScaffoldEngine(tmpl_dir)
        out = tmp_path / "hello.txt"
        out.write_text("existing")
        result = engine.render_file("hello.txt.j2", out, {"name": "X"})
        assert result is False
        assert out.read_text() == "existing"

    def test_render_file_force(self, tmp_path: Path) -> None:
        tmpl_dir = self._make_template_dir(tmp_path)
        engine = ScaffoldEngine(tmpl_dir)
        out = tmp_path / "hello.txt"
        out.write_text("existing")
        result = engine.render_file("hello.txt.j2", out, {"name": "X"}, force=True)
        assert result is True
        assert out.read_text() == "Hello X!\n"

    def test_render_file_dry_run(self, tmp_path: Path) -> None:
        tmpl_dir = self._make_template_dir(tmp_path)
        engine = ScaffoldEngine(tmpl_dir)
        out = tmp_path / "hello.txt"
        result = engine.render_file("hello.txt.j2", out, {"name": "X"}, dry_run=True)
        assert result is False
        assert not out.exists()

    def test_render_static(self, tmp_path: Path) -> None:
        tmpl_dir = self._make_template_dir(tmp_path)
        engine = ScaffoldEngine(tmpl_dir)
        out = tmp_path / "static.txt"
        result = engine.render_static("hello world", out)
        assert result is True
        assert out.read_text() == "hello world"

    def test_ensure_dir(self, tmp_path: Path) -> None:
        tmpl_dir = self._make_template_dir(tmp_path)
        engine = ScaffoldEngine(tmpl_dir)
        d = tmp_path / "subdir"
        engine.ensure_dir(d)
        assert d.is_dir()
        assert (d / ".gitkeep").exists()

    def test_ensure_dir_no_gitkeep_if_has_files(self, tmp_path: Path) -> None:
        tmpl_dir = self._make_template_dir(tmp_path)
        engine = ScaffoldEngine(tmpl_dir)
        d = tmp_path / "subdir"
        d.mkdir()
        (d / "file.txt").write_text("x")
        engine.ensure_dir(d)
        assert not (d / ".gitkeep").exists()

    def test_has_template(self, tmp_path: Path) -> None:
        tmpl_dir = self._make_template_dir(tmp_path)
        engine = ScaffoldEngine(tmpl_dir)
        assert engine.has_template("hello.txt.j2")
        assert not engine.has_template("missing.j2")

    def test_render_file_executable(self, tmp_path: Path) -> None:
        tmpl_dir = self._make_template_dir(tmp_path)
        engine = ScaffoldEngine(tmpl_dir)
        out = tmp_path / "script.sh"
        engine.render_file("hello.txt.j2", out, {"name": "X"}, executable=True)
        assert out.stat().st_mode & 0o755 == 0o755
