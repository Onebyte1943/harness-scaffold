"""Tests for CLI commands (design v3)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from harness.cli import cli

EXPECTED_COMMAND_COUNT = 14  # 12 phase commands + hx-next + hx-doctor


class TestInit:
    def test_init_creates_brain_and_contract(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        assert result.exit_code == 0
        # Brain
        assert (tmp_path / ".harness" / "config.toml").exists()
        assert (tmp_path / ".harness" / "registry.toml").exists()
        assert (tmp_path / ".harness" / "playbooks").is_dir()
        assert (tmp_path / ".harness" / "scripts").is_dir()
        assert (tmp_path / ".harness" / "principle-packs" / "generic.md").exists()
        assert (tmp_path / ".harness" / "evals" / "README.md").exists()
        assert (tmp_path / ".harness" / "memory").is_dir()
        assert (tmp_path / ".harness" / "knowledge").is_dir()
        assert (tmp_path / ".harness" / "templates").is_dir()
        # Contract files
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / "CLAUDE.md").exists()
        assert (tmp_path / ".claude" / "commands" / "hx-constitution.md").exists()
        assert (tmp_path / ".claude" / "commands" / "hx-next.md").exists()
        # CI + pre-commit + .agent marker
        assert (tmp_path / ".gitlab-ci.yml").exists()
        assert (tmp_path / ".pre-commit-config.yaml").exists()
        assert (tmp_path / ".agent").is_dir()

    def test_init_codex(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["init", str(tmp_path), "--agent", "codex", "--no-git"])
        assert result.exit_code == 0
        assert (tmp_path / ".codex" / "commands" / "hx-constitution.md").exists()
        assert (tmp_path / ".codex" / "commands" / "hx-next.md").exists()

    def test_init_both_agents(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["init", str(tmp_path), "--agent", "claude", "--agent", "codex", "--no-git"],
        )
        assert result.exit_code == 0
        assert (tmp_path / "CLAUDE.md").exists()
        assert (tmp_path / ".codex" / "commands").is_dir()

    def test_init_idempotent(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        result = runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        assert result.exit_code == 0
        assert "already configured" in result.output

    def test_init_incremental_agent(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        result = runner.invoke(cli, ["init", str(tmp_path), "--agent", "codex", "--no-git"])
        assert result.exit_code == 0
        assert (tmp_path / ".codex" / "commands").is_dir()

    def test_init_dry_run(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert not (tmp_path / ".harness").exists()
        # No legacy paths
        assert not (tmp_path / "harness-artifacts").exists()
        assert not (tmp_path / "memory").exists()

    def test_init_greenfield(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["init", str(tmp_path), "--agent", "claude", "--profile", "greenfield", "--no-git"],
        )
        assert result.exit_code == 0
        agents_md = (tmp_path / "AGENTS.md").read_text()
        assert "greenfield" in agents_md

    def test_init_full_flow(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["init", str(tmp_path), "--agent", "claude", "--flow", "full", "--no-git"],
        )
        assert result.exit_code == 0

    def test_init_lang_explicit(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["init", str(tmp_path), "--agent", "claude", "--lang", "python", "--no-git"],
        )
        assert result.exit_code == 0
        cfg = (tmp_path / ".harness" / "config.toml").read_text()
        assert 'lang = "python"' in cfg

    def test_init_lang_autodetect_python(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n")
        runner = CliRunner()
        result = runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        assert result.exit_code == 0
        cfg = (tmp_path / ".harness" / "config.toml").read_text()
        assert 'lang = "python"' in cfg

    def test_init_script_ps(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["init", str(tmp_path), "--agent", "claude", "--script", "ps", "--no-git"],
        )
        assert result.exit_code == 0
        cfg = (tmp_path / ".harness" / "config.toml").read_text()
        assert 'script_shell = "ps"' in cfg

    def test_init_preset_secure(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["init", str(tmp_path), "--agent", "claude", "--preset", "secure", "--no-git"],
        )
        assert result.exit_code == 0
        cfg = (tmp_path / ".harness" / "config.toml").read_text()
        assert "secure" in cfg

    def test_init_output_lang_default_zh(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        assert result.exit_code == 0
        cfg = (tmp_path / ".harness" / "config.toml").read_text()
        assert 'output_lang = "zh"' in cfg
        # zh narrative renders in playbook bodies
        verify_pb = (tmp_path / ".harness" / "playbooks" / "41-verify.md").read_text()
        assert "单一确定性传感器" in verify_pb
        # but section headings + Provenance stay English
        assert "## Purpose" in verify_pb
        assert "## Prerequisites" in verify_pb
        assert "> - Authoritative paradigm:" in verify_pb
        assert "> - Investigation protocol:" in verify_pb
        assert "> - Output form:" in verify_pb

    def test_init_output_lang_en(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "init",
                str(tmp_path),
                "--agent",
                "claude",
                "--output-lang",
                "en",
                "--no-git",
            ],
        )
        assert result.exit_code == 0
        cfg = (tmp_path / ".harness" / "config.toml").read_text()
        assert 'output_lang = "en"' in cfg
        verify_pb = (tmp_path / ".harness" / "playbooks" / "41-verify.md").read_text()
        assert "The single deterministic sensor" in verify_pb
        # No Chinese narrative in the en render
        assert "单一确定性传感器" not in verify_pb
        # Provenance still English (always)
        assert "> - Authoritative paradigm:" in verify_pb

    def test_init_output_lang_invalid(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "init",
                str(tmp_path),
                "--agent",
                "claude",
                "--output-lang",
                "fr",
                "--no-git",
            ],
        )
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid choice" in result.output.lower()

    def test_init_output_lang_propagates_to_adapters(self, tmp_path: Path) -> None:
        """The claude adapter (CLAUDE.md + slash commands) honors output_lang."""
        runner = CliRunner()
        runner.invoke(
            cli,
            [
                "init",
                str(tmp_path),
                "--agent",
                "claude",
                "--agent",
                "codex",
                "--no-git",
            ],
        )
        # zh by default — slash command body in Chinese
        verify_cmd = (tmp_path / ".claude" / "commands" / "hx-verify.md").read_text()
        assert "执行" in verify_cmd or "playbook" in verify_cmd  # zh body
        assert "## Instructions" in verify_cmd  # heading stays English
        # Codex slash command also zh
        codex_verify = (tmp_path / ".codex" / "commands" / "hx-verify.md").read_text()
        assert "执行" in codex_verify or "playbook" in codex_verify
        # CLAUDE.md: Provenance always English, narrative in zh
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "> - Authoritative paradigm:" in claude_md
        assert "共享 agent 上下文" in claude_md

    def test_init_constitution_lazy(self, tmp_path: Path) -> None:
        """L-RULE is lazy: constitution.md only appears after /hx-constitution."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        # The memory directory is eager (created so first writer doesn't need mkdir)
        assert (tmp_path / ".harness" / "memory").is_dir()
        # But constitution.md is lazy — not present yet
        assert not (tmp_path / ".harness" / "memory" / "constitution.md").exists()

    def test_init_lazy_state_roots(self, tmp_path: Path) -> None:
        """specs/, adr/, .agent/progress.md, knowledge docs — none eager."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        # No specs/ tree at root yet
        assert not (tmp_path / "specs").exists()
        # adr/ subdir not yet created
        assert not (tmp_path / ".harness" / "knowledge" / "adr").exists()
        # progress log not yet created
        assert not (tmp_path / ".agent" / "progress.md").exists()
        # None of the 8 knowledge docs are seeded yet
        assert not (tmp_path / ".harness" / "knowledge" / "architecture.md").exists()
        # No legacy artifact tree
        assert not (tmp_path / "harness-artifacts").exists()
        assert not (tmp_path / "memory").exists()

    def test_init_no_legacy_skills_dir(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        assert not (tmp_path / ".claude" / "skills").exists()

    def test_init_playbook_count(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        playbooks = list((tmp_path / ".harness" / "playbooks").glob("*.md"))
        assert len(playbooks) == EXPECTED_COMMAND_COUNT
        # No 20-audit
        assert not (tmp_path / ".harness" / "playbooks" / "20-audit.md").exists()
        # 12-next is present
        assert (tmp_path / ".harness" / "playbooks" / "12-next.md").exists()

    def test_init_slash_command_count(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        commands = list((tmp_path / ".claude" / "commands").glob("hx-*.md"))
        assert len(commands) == EXPECTED_COMMAND_COUNT
        assert not (tmp_path / ".claude" / "commands" / "hx-audit.md").exists()

    def test_init_slash_command_has_frontmatter(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        content = (tmp_path / ".claude" / "commands" / "hx-plan.md").read_text()
        assert content.startswith("---\n")
        assert "description:" in content
        assert ".harness/playbooks/33-plan.md" in content

    def test_init_claude_md_imports_agents(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        content = (tmp_path / "CLAUDE.md").read_text()
        assert "@AGENTS.md" in content
        assert "/hx-constitution" in content
        assert "/hx-next" in content
        assert ".claude/commands/" in content

    def test_init_constitution_seed_embedded_in_playbook(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        pb = (tmp_path / ".harness" / "playbooks" / "00-constitution.md").read_text()
        assert "Appendix A" in pb

    def test_init_progress_seed_embedded_in_implement(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        pb = (tmp_path / ".harness" / "playbooks" / "40-implement.md").read_text()
        assert "Appendix A" in pb
        assert "Progress Log" in pb

    def test_init_verify_script_executable(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        verify = tmp_path / ".harness" / "scripts" / "sh" / "verify.sh"
        assert verify.exists()
        assert verify.stat().st_mode & 0o755 == 0o755


class TestDoctor:
    def test_doctor_healthy_after_init(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(cli, ["doctor"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "All checks passed" in result.output

    def test_doctor_verbose_marks_lazy_paths(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(cli, ["doctor", "-v"])
        assert result.exit_code == 0
        assert "Not yet" in result.output  # lazy artifacts annotated

    def test_doctor_flags_legacy_layout(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        # Simulate stale v1 layout
        (tmp_path / "harness-artifacts").mkdir()
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(cli, ["doctor"])
        # Legacy detection is a warning, not an error.
        assert result.exit_code == 0
        assert "Legacy v1 layout" in result.output

    def test_doctor_not_initialized(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["doctor"])
        assert result.exit_code == 1
        assert "Not in a harness project" in result.output

    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
