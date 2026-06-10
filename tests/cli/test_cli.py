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

    def test_init_force_backs_up_legacy_constitution(self, tmp_path: Path) -> None:
        """0.3 → 0.4 migration: --force on a project whose
        constitution.md predates the spec-kit format (no Sync Impact
        Report and no spec-kit Version line) preserves the old file
        as constitution.md.0.3.bak."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        # Hand-write a pre-0.4 constitution.
        memory = tmp_path / ".harness" / "memory"
        memory.mkdir(parents=True, exist_ok=True)
        legacy_body = (
            "# Constitution\n\n"
            "## P1 Verification is mandatory   [enforceable: arch-test]\n"
            "- Rule: legacy 0.3.x format\n"
            "- Why: lacks spec-kit Version line + Sync Impact Report\n"
        )
        (memory / "constitution.md").write_text(legacy_body)
        result = runner.invoke(
            cli, ["init", str(tmp_path), "--agent", "claude", "--no-git", "--force"]
        )
        assert result.exit_code == 0
        backup = memory / "constitution.md.0.3.bak"
        assert backup.exists()
        assert backup.read_text() == legacy_body

    def test_init_force_skips_constitution_backup_when_already_spec_kit(
        self, tmp_path: Path
    ) -> None:
        """No-op when the existing constitution.md already has both
        the Sync Impact Report and a spec-kit Version line."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        memory = tmp_path / ".harness" / "memory"
        memory.mkdir(parents=True, exist_ok=True)
        (memory / "constitution.md").write_text(
            "<!--\nSYNC IMPACT REPORT\nVersion: 0.0.0 → 1.0.0\n-->\n\n"
            "# Constitution\n\n## Core Principles\n\n## Governance\n\n"
            "**Version**: 1.0.0 | **Ratified**: 2026-06-10 | "
            "**Last Amended**: 2026-06-10\n"
        )
        result = runner.invoke(
            cli, ["init", str(tmp_path), "--agent", "claude", "--no-git", "--force"]
        )
        assert result.exit_code == 0
        assert not (memory / "constitution.md.0.3.bak").exists()

    def test_init_force_backs_up_legacy_agents_md(self, tmp_path: Path) -> None:
        """0.2 → 0.3 migration: --force on a project whose AGENTS.md
        predates the 5-subsystem rewrite preserves the old file as
        AGENTS.md.0.2.bak before overwriting."""
        runner = CliRunner()
        # Seed a 0.2-shaped project.
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        # Hand-edit AGENTS.md to look like a pre-0.3 file (no ## Subsystems).
        legacy_body = "# AGENTS.md\n\nLegacy 0.2.x contract — no Subsystems section.\n"
        (tmp_path / "AGENTS.md").write_text(legacy_body)

        # Re-init with --force; the new template should land, but the
        # legacy body must be preserved.
        result = runner.invoke(
            cli, ["init", str(tmp_path), "--agent", "claude", "--no-git", "--force"]
        )
        assert result.exit_code == 0
        backup = tmp_path / "AGENTS.md.0.2.bak"
        assert backup.exists()
        assert backup.read_text() == legacy_body
        # New AGENTS.md has the 5-subsystem structure.
        assert "## Subsystems" in (tmp_path / "AGENTS.md").read_text()

    def test_init_force_skips_backup_when_already_0_3(self, tmp_path: Path) -> None:
        """No-op when the existing AGENTS.md already has the 5-subsystem
        spine (i.e. user already migrated, or never had a 0.2 install)."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        # The freshly-rendered file already has ## Subsystems.
        result = runner.invoke(
            cli, ["init", str(tmp_path), "--agent", "claude", "--no-git", "--force"]
        )
        assert result.exit_code == 0
        assert not (tmp_path / "AGENTS.md.0.2.bak").exists()

    def test_init_idempotent(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        result = runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        assert result.exit_code == 0
        # zh-default phrasing: "所有请求的 agent 都已配置。"
        assert "都已配置" in result.output

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

    def test_init_vibecode(self, tmp_path: Path) -> None:
        """Third profile: 'vibecode' for inheriting AI-generated codebases
        (per sawinyh's three-way taxonomy)."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["init", str(tmp_path), "--agent", "claude", "--profile", "vibecode", "--no-git"],
        )
        assert result.exit_code == 0
        cfg = (tmp_path / ".harness" / "config.toml").read_text()
        assert 'profile = "vibecode"' in cfg
        agents_md = (tmp_path / "AGENTS.md").read_text()
        assert "vibecode" in agents_md

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
        """Default output_lang is zh; templates stay English; AGENTS.md
        carries the contract so /hx-* agents render deliverables in zh
        at runtime."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        assert result.exit_code == 0
        cfg = (tmp_path / ".harness" / "config.toml").read_text()
        assert 'output_lang = "zh"' in cfg
        # Scaffold artifacts are single-source-of-truth English.
        verify_pb = (tmp_path / ".harness" / "playbooks" / "41-verify.md").read_text()
        assert "## Purpose" in verify_pb
        assert "> - Authoritative paradigm:" in verify_pb
        # AGENTS.md is organized by the 5-subsystem model. Output Language
        # Contract lives under ## 1. Instructions; the active output_lang
        # value is rendered there for the agent to honor at runtime.
        agents_md = (tmp_path / "AGENTS.md").read_text()
        assert "## 1. Instructions" in agents_md
        assert "### 1.1 Output Language Contract" in agents_md
        assert "**`zh`**" in agents_md
        # No translation happens in templates — Chinese narrative only
        # appears later, written by /hx-* agents into deliverables.
        assert "单一确定性传感器" not in verify_pb

    def test_init_output_lang_en(self, tmp_path: Path) -> None:
        """--output-lang en flips the contract; templates are unchanged."""
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
        agents_md = (tmp_path / "AGENTS.md").read_text()
        assert "### 1.1 Output Language Contract" in agents_md
        assert "**`en`**" in agents_md
        # Verify the same playbook content as zh case — templates do
        # not depend on output_lang.
        verify_pb = (tmp_path / ".harness" / "playbooks" / "41-verify.md").read_text()
        assert "## Purpose" in verify_pb
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

    def test_init_agents_md_five_subsystem_structure(self, tmp_path: Path) -> None:
        """AGENTS.md is organized by the 5-subsystem harness OS model.
        Every section heading is required; downstream playbooks and
        adapters pattern-match on these names."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        agents_md = (tmp_path / "AGENTS.md").read_text()
        for required in (
            "## Subsystems",
            "## 1. Instructions",
            "### 1.1 Output Language Contract",
            "## 2. State",
            "### 2.1 feature_list.json",
            "### 2.3 CLI surface",
            "## 3. Verification",
            "### 3.1 init.sh",
            "## 4. Scope",
            "### 4.1 Boundaries",
            "## 5. Lifecycle",
            "### 5.1 Session Contract",
            "### 5.2 session-handoff.md",
        ):
            assert required in agents_md, f"missing required section: {required}"
        # agentsmd standard superset declaration
        assert "superset of the [agentsmd/agents.md] standard" in agents_md

    def test_init_adapter_commands_point_to_contract(self, tmp_path: Path) -> None:
        """Adapter slash-command files are English-only, but each one
        explicitly references the Output Language Contract in AGENTS.md
        so the executing agent always picks up the deliverable
        language."""
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
        verify_cmd = (tmp_path / ".claude" / "commands" / "hx-verify.md").read_text()
        assert "## Instructions" in verify_cmd
        assert "Output Language Contract" in verify_cmd
        codex_verify = (tmp_path / ".codex" / "commands" / "hx-verify.md").read_text()
        assert "Output Language Contract" in codex_verify
        # CLAUDE.md imports AGENTS.md so the contract reaches Claude.
        claude_md = (tmp_path / "CLAUDE.md").read_text()
        assert "@AGENTS.md" in claude_md

    def test_init_ships_12_factor_principle_pack(self, tmp_path: Path) -> None:
        """Subsystem 1: 12-factor-agents.md ships under principle-packs/
        as a feed for /hx-constitution synthesis."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        pack = tmp_path / ".harness" / "principle-packs" / "12-factor-agents.md"
        assert pack.exists()
        content = pack.read_text()
        # ID prefix locks the pack's identity into structural tests.
        assert "P-12-1" in content
        assert "P-12-12" in content
        # Source attribution.
        assert "12-Factor Agents" in content

    def test_init_renders_feature_list_schema(self, tmp_path: Path) -> None:
        """Subsystem 2: feature_list.schema.json ships under .harness/templates/."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        schema = tmp_path / ".harness" / "templates" / "feature_list.schema.json"
        assert schema.exists()
        import json as _json

        data = _json.loads(schema.read_text())
        # Schema-of-schemas sanity: required keys reflect Subsystem 2 contract.
        assert data["required"] == ["spec_id", "features"]
        feat_props = data["$defs"]["feature"]["properties"]
        assert set(feat_props) == {
            "id",
            "name",
            "depends_on",
            "status",
            "evidence",
            "verification",
        }
        assert feat_props["status"]["enum"] == ["not-started", "in-progress", "passing"]

    def test_init_creates_init_sh(self, tmp_path: Path) -> None:
        """init.sh is the Verification subsystem entry script:
        present at project root, executable, calls verify.sh."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        init_sh = tmp_path / "init.sh"
        assert init_sh.exists()
        assert init_sh.stat().st_mode & 0o755 == 0o755
        content = init_sh.read_text()
        # The three documented sections.
        assert "=== Harness" in content
        assert "=== Environment ===" in content
        assert "=== Verify ===" in content
        # Calls the unified verify.sh, not arbitrary commands.
        assert ".harness/scripts/sh/verify.sh" in content

    def test_init_creates_init_ps1_on_windows_shell(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(
            cli,
            ["init", str(tmp_path), "--agent", "claude", "--script", "ps", "--no-git"],
        )
        assert (tmp_path / "init.ps1").exists()
        assert not (tmp_path / "init.sh").exists()

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
        # None of the 7 knowledge docs are seeded yet
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

    def test_init_implement_playbook_session_handoff(self, tmp_path: Path) -> None:
        """Subsystem 5: implement playbook teaches the agent to overwrite
        session-handoff.md at session end, with a verbatim 6-section
        template under Appendix B."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        pb = (tmp_path / ".harness" / "playbooks" / "40-implement.md").read_text()
        assert "Appendix B" in pb
        assert "session-handoff.md" in pb
        for required in (
            "## Current Objective",
            "## Completed This Session",
            "## Verification Evidence",
            "## Files Changed",
            "## Decisions Made",
            "## Blockers / Risks",
            "## Next Session Startup",
        ):
            assert required in pb, f"missing handoff section: {required}"
        # Steps reference State CLI integration and init.sh.
        assert "harness state pass" in pb
        assert "./init.sh" in pb

    def test_init_tasks_playbook_writes_feature_list_json(self, tmp_path: Path) -> None:
        """Subsystem 2: /hx-tasks playbook now requires feature_list.json
        alongside tasks.md, with a verbatim JSON template under
        Appendix B."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        pb = (tmp_path / ".harness" / "playbooks" / "34-tasks.md").read_text()
        assert "feature_list.json" in pb
        assert "Appendix B" in pb
        # Hard rule the agent must read.
        assert "MUST NOT" in pb

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
        # Default output_lang is zh, so doctor renders the zh phrasing.
        assert "所有检查通过" in result.output

    def test_doctor_renders_subsystem_summary(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Doctor groups checks under the 5-subsystem model."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(cli, ["doctor", "-v"])
        assert result.exit_code == 0
        for sub in ("Instructions", "State", "Verification", "Scope", "Lifecycle"):
            assert sub in result.output, f"missing subsystem row: {sub}"

    def test_doctor_flags_invalid_feature_list(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A schema-violating feature_list.json surfaces under State as FAIL."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        # Hand-write a bad feature_list — passing without evidence.
        spec = tmp_path / "specs" / "001-auth"
        spec.mkdir(parents=True)
        (spec / "tasks.md").write_text("# Tasks\n- [x] T1.1\n")
        import json as _json

        (spec / "feature_list.json").write_text(
            _json.dumps(
                {
                    "spec_id": "001",
                    "features": [
                        {
                            "id": "T1.1",
                            "name": "broken",
                            "depends_on": [],
                            "status": "passing",
                            "evidence": "",
                            "verification": "true",
                        }
                    ],
                }
            )
        )
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(cli, ["doctor"])
        assert result.exit_code != 0
        # Rich may truncate the long detail string in the test terminal,
        # but the spec dir name + a State-row FAIL must be visible.
        assert "001-auth" in result.output
        assert "State" in result.output

    def test_doctor_flags_missing_init_sh(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing init.sh surfaces under Verification."""
        runner = CliRunner()
        runner.invoke(cli, ["init", str(tmp_path), "--agent", "claude", "--no-git"])
        (tmp_path / "init.sh").unlink()
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(cli, ["doctor"])
        assert result.exit_code != 0
        assert "init.sh" in result.output

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
        assert "0.4.0" in result.output
