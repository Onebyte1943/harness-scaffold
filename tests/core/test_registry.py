"""Tests for core/registry.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from harness.core.registry import AdapterSpec, Registry

SAMPLE_REGISTRY = """\
[adapters.claude]
type = "cli"
config_dir = ".claude"
context_file = "CLAUDE.md"
command_format = "/hx-{cmd}"
templates_dir = "claude"

[adapters.claude.capabilities.hook]
supported = true
required = false
degradation = "Fall back to pre-commit"

[adapters.codex]
type = "cli"
config_dir = ".codex"
context_file = "AGENTS.md"
command_format = "$hx-{cmd}"
templates_dir = "codex"

[adapters.codex.capabilities.hook]
supported = false
required = false
degradation = "CI only"
"""


class TestAdapterSpec:
    def test_from_dict(self) -> None:
        spec = AdapterSpec.from_dict(
            "claude",
            {
                "type": "cli",
                "config_dir": ".claude",
                "context_file": "CLAUDE.md",
                "command_format": "/hx-{cmd}",
                "templates_dir": "claude",
                "capabilities": {
                    "hook": {"supported": True, "required": False, "degradation": "pre-commit"},
                },
            },
        )
        assert spec.name == "claude"
        assert spec.adapter_type == "cli"
        assert spec.capabilities["hook"].supported is True
        assert spec.capabilities["hook"].degradation == "pre-commit"


class TestRegistry:
    def test_load(self, tmp_path: Path) -> None:
        reg_file = tmp_path / "registry.toml"
        reg_file.write_text(SAMPLE_REGISTRY)
        registry = Registry.load(reg_file)
        assert registry.supported_agents() == ["claude", "codex"]

    def test_get_adapter(self, tmp_path: Path) -> None:
        reg_file = tmp_path / "registry.toml"
        reg_file.write_text(SAMPLE_REGISTRY)
        registry = Registry.load(reg_file)
        spec = registry.get_adapter("claude")
        assert spec.config_dir == ".claude"

    def test_get_unknown_adapter(self, tmp_path: Path) -> None:
        reg_file = tmp_path / "registry.toml"
        reg_file.write_text(SAMPLE_REGISTRY)
        registry = Registry.load(reg_file)
        with pytest.raises(KeyError):
            registry.get_adapter("unknown")

    def test_load_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            Registry.load(tmp_path / "missing.toml")

    def test_has_adapter(self, tmp_path: Path) -> None:
        reg_file = tmp_path / "registry.toml"
        reg_file.write_text(SAMPLE_REGISTRY)
        registry = Registry.load(reg_file)
        assert registry.has_adapter("claude")
        assert not registry.has_adapter("cursor")
