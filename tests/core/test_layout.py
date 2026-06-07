"""Tests for core/layout.py (design v3)."""

from __future__ import annotations

from harness.core.layout import (
    ADR_DIR,
    AGENT_DIR,
    CONSTITUTION_PATH,
    EVALS_DIR,
    GITLAB_CI_CONFIG,
    HARNESS_DIR,
    HX_COMMANDS,
    KNOWLEDGE_DIR,
    KNOWLEDGE_DOCS,
    KNOWLEDGE_HOWTO_DIR,
    LEGACY_ARTIFACTS_DIR,
    LEGACY_CONSTITUTION_PATH,
    MEMORY_DIR,
    PLAYBOOK_FILES,
    PLAYBOOKS_DIR,
    PRE_COMMIT_CONFIG,
    PRINCIPLE_PACKS_DIR,
    PROGRESS_PATH,
    SCRIPTS_DIR,
    SPECS_DIR,
    TEMPLATES_DIR,
    playbook_path,
)


class TestPaths:
    def test_harness_subdirs(self) -> None:
        assert HARNESS_DIR == ".harness"
        assert PLAYBOOKS_DIR == ".harness/playbooks"
        assert SCRIPTS_DIR == ".harness/scripts"
        assert MEMORY_DIR == ".harness/memory"
        assert KNOWLEDGE_DIR == ".harness/knowledge"
        assert ADR_DIR == ".harness/knowledge/adr"
        assert KNOWLEDGE_HOWTO_DIR == ".harness/knowledge/how-to"
        assert PRINCIPLE_PACKS_DIR == ".harness/principle-packs"
        assert TEMPLATES_DIR == ".harness/templates"
        assert EVALS_DIR == ".harness/evals"

    def test_constitution_in_memory(self) -> None:
        assert CONSTITUTION_PATH == ".harness/memory/constitution.md"

    def test_specs_at_root(self) -> None:
        assert SPECS_DIR == "specs"

    def test_agent_state(self) -> None:
        assert AGENT_DIR == ".agent"
        assert PROGRESS_PATH == ".agent/progress.md"

    def test_ci_paths(self) -> None:
        assert GITLAB_CI_CONFIG == ".gitlab-ci.yml"
        assert PRE_COMMIT_CONFIG == ".pre-commit-config.yaml"

    def test_legacy_paths(self) -> None:
        assert LEGACY_ARTIFACTS_DIR == "harness-artifacts"
        assert LEGACY_CONSTITUTION_PATH == "memory/constitution.md"


class TestKnowledgeDocs:
    def test_count(self) -> None:
        # product, architecture, tech-stack, business, conventions, glossary, setup-and-verify
        assert len(KNOWLEDGE_DOCS) == 7

    def test_required_docs_present(self) -> None:
        for doc in (
            "product",
            "architecture",
            "tech-stack",
            "business",
            "conventions",
            "glossary",
            "setup-and-verify",
        ):
            assert doc in KNOWLEDGE_DOCS


class TestCommands:
    def test_count(self) -> None:
        # 12 phase commands + hx-next + hx-doctor
        assert len(HX_COMMANDS) == 14

    def test_no_audit(self) -> None:
        assert "audit" not in HX_COMMANDS

    def test_next_present(self) -> None:
        assert "next" in HX_COMMANDS

    def test_playbook_path(self) -> None:
        assert playbook_path("plan") == ".harness/playbooks/33-plan.md"
        assert playbook_path("next") == ".harness/playbooks/12-next.md"
        assert playbook_path("doctor") == ".harness/playbooks/90-doctor.md"

    def test_playbook_files_keys_match_commands(self) -> None:
        assert set(PLAYBOOK_FILES.keys()) == set(HX_COMMANDS)
