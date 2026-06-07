"""Tests for core/config.py (design v3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from harness.core.config import (
    HarnessConfig,
    detect_project_root,
    load_config,
    save_config,
)


class TestHarnessConfig:
    def test_defaults(self, tmp_path: Path) -> None:
        config = HarnessConfig(project_root=tmp_path)
        assert config.profile == "brownfield"
        assert config.flow == "standard"
        assert config.lang == "auto"
        assert config.agents == ["claude"]
        assert config.script_shell == "sh"
        assert config.presets == []
        assert config.output_lang == "zh"

    def test_harness_dir(self, tmp_path: Path) -> None:
        config = HarnessConfig(project_root=tmp_path)
        assert config.harness_dir == tmp_path / ".harness"

    def test_is_initialized_false(self, tmp_path: Path) -> None:
        config = HarnessConfig(project_root=tmp_path)
        assert not config.is_initialized()

    def test_is_initialized_true(self, tmp_path: Path) -> None:
        (tmp_path / ".harness").mkdir()
        config = HarnessConfig(project_root=tmp_path)
        assert config.is_initialized()

    def test_to_toml(self, tmp_path: Path) -> None:
        config = HarnessConfig(
            project_root=tmp_path,
            lang="python",
            agents=["claude", "codex"],
            presets=["trunk-based"],
        )
        toml = config.to_toml()
        assert "[harness]" in toml
        assert 'profile = "brownfield"' in toml
        assert 'lang = "python"' in toml
        assert '"claude", "codex"' in toml
        assert '"trunk-based"' in toml
        assert 'output_lang = "zh"' in toml

    def test_to_toml_output_lang_en(self, tmp_path: Path) -> None:
        config = HarnessConfig(project_root=tmp_path, output_lang="en")
        assert 'output_lang = "en"' in config.to_toml()


class TestSaveLoadConfig:
    def test_roundtrip(self, tmp_path: Path) -> None:
        original = HarnessConfig(
            project_root=tmp_path,
            profile="greenfield",
            flow="full",
            lang="typescript",
            agents=["claude", "codex"],
            script_shell="sh",
            presets=["secure"],
            output_lang="en",
        )
        save_config(original)
        loaded = load_config(tmp_path)
        assert loaded.profile == "greenfield"
        assert loaded.flow == "full"
        assert loaded.lang == "typescript"
        assert loaded.agents == ["claude", "codex"]
        assert loaded.presets == ["secure"]
        assert loaded.output_lang == "en"

    def test_load_defaults_output_lang_zh_when_missing(self, tmp_path: Path) -> None:
        """Older config.toml without output_lang loads as zh (the default)."""
        (tmp_path / ".harness").mkdir()
        (tmp_path / ".harness" / "config.toml").write_text(
            "[harness]\n"
            'profile = "brownfield"\n'
            'flow = "standard"\n'
            'lang = "auto"\n'
            'agents = ["claude"]\n'
            'script_shell = "sh"\n'
            "presets = []\n"
        )
        loaded = load_config(tmp_path)
        assert loaded.output_lang == "zh"

    def test_load_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path)


class TestDetectProjectRoot:
    def test_finds_root(self, tmp_path: Path) -> None:
        (tmp_path / ".harness").mkdir()
        subdir = tmp_path / "a" / "b"
        subdir.mkdir(parents=True)
        found = detect_project_root(subdir)
        assert found == tmp_path

    def test_not_found(self, tmp_path: Path) -> None:
        found = detect_project_root(tmp_path)
        assert found is None
