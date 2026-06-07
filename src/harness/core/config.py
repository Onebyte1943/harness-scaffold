"""Project configuration management."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

HARNESS_DIR = ".harness"
CONFIG_FILE = "config.toml"


@dataclass
class HarnessConfig:
    """Harness project configuration (design v3)."""

    project_root: Path
    profile: Literal["brownfield", "greenfield"] = "brownfield"
    flow: Literal["quick", "standard", "full", "epic"] = "standard"
    lang: str = "auto"
    agents: list[str] = field(default_factory=lambda: ["claude"])
    script_shell: Literal["sh", "ps"] = "sh"
    presets: list[str] = field(default_factory=list)
    output_lang: Literal["zh", "en"] = "zh"

    @property
    def harness_dir(self) -> Path:
        return self.project_root / HARNESS_DIR

    @property
    def config_path(self) -> Path:
        return self.harness_dir / CONFIG_FILE

    def is_initialized(self) -> bool:
        return self.harness_dir.exists()

    def to_toml(self) -> str:
        agents_str = ", ".join('"' + a + '"' for a in self.agents)
        presets_str = ", ".join('"' + p + '"' for p in self.presets)
        lines = [
            "[harness]",
            f'profile = "{self.profile}"',
            f'flow = "{self.flow}"',
            f'lang = "{self.lang}"',
            f"agents = [{agents_str}]",
            f'script_shell = "{self.script_shell}"',
            f"presets = [{presets_str}]",
            f'output_lang = "{self.output_lang}"',
        ]
        return "\n".join(lines) + "\n"


def load_config(project_root: Path) -> HarnessConfig:
    """Load harness configuration from .harness/config.toml."""
    config_path = project_root / HARNESS_DIR / CONFIG_FILE
    if not config_path.exists():
        raise FileNotFoundError(f"No harness config found at {config_path}")

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    harness_data: dict[str, Any] = data.get("harness", {})
    return HarnessConfig(
        project_root=project_root,
        profile=harness_data.get("profile", "brownfield"),
        flow=harness_data.get("flow", "standard"),
        lang=harness_data.get("lang", "auto"),
        agents=harness_data.get("agents", ["claude"]),
        script_shell=harness_data.get("script_shell", "sh"),
        presets=harness_data.get("presets", []),
        output_lang=harness_data.get("output_lang", "zh"),
    )


def save_config(config: HarnessConfig) -> None:
    """Save harness configuration to .harness/config.toml."""
    config.harness_dir.mkdir(parents=True, exist_ok=True)
    config.config_path.write_text(config.to_toml())


def detect_project_root(start: Path | None = None) -> Path | None:
    """Walk up from start directory to find .harness/ directory."""
    current = (start or Path.cwd()).resolve()
    while True:
        if (current / HARNESS_DIR).is_dir():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent
