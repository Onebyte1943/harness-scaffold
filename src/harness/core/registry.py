"""Adapter registry — parses registry.toml and routes to terminal adapters."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

REGISTRY_FILE = "registry.toml"


@dataclass
class CapabilitySpec:
    """Describes a single capability and its degradation path."""

    supported: bool = False
    required: bool = False
    degradation: str = ""


@dataclass
class AdapterSpec:
    """Describes a terminal adapter."""

    name: str
    adapter_type: str  # "cli" or "ide"
    config_dir: str
    context_file: str
    command_format: str
    templates_dir: str
    capabilities: dict[str, CapabilitySpec] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> AdapterSpec:
        caps_data = data.get("capabilities", {})
        capabilities = {}
        for cap_name, cap_data in caps_data.items():
            if isinstance(cap_data, dict):
                capabilities[cap_name] = CapabilitySpec(
                    supported=cap_data.get("supported", False),
                    required=cap_data.get("required", False),
                    degradation=cap_data.get("degradation", ""),
                )
        return cls(
            name=name,
            adapter_type=data.get("type", "cli"),
            config_dir=data.get("config_dir", ""),
            context_file=data.get("context_file", ""),
            command_format=data.get("command_format", ""),
            templates_dir=data.get("templates_dir", name),
            capabilities=capabilities,
        )


class Registry:
    """Multi-terminal adapter registry."""

    def __init__(self, adapters: dict[str, AdapterSpec]) -> None:
        self._adapters = adapters

    @classmethod
    def load(cls, path: Path) -> Registry:
        """Parse registry.toml and return a Registry instance."""
        if not path.exists():
            raise FileNotFoundError(f"Registry not found at {path}")
        with open(path, "rb") as f:
            data = tomllib.load(f)

        adapters: dict[str, AdapterSpec] = {}
        for name, adapter_data in data.get("adapters", {}).items():
            if isinstance(adapter_data, dict):
                adapters[name] = AdapterSpec.from_dict(name, adapter_data)
        return cls(adapters)

    def get_adapter(self, name: str) -> AdapterSpec:
        if name not in self._adapters:
            raise KeyError(f"Unknown adapter: {name}. Available: {self.supported_agents()}")
        return self._adapters[name]

    def list_adapters(self) -> list[AdapterSpec]:
        return list(self._adapters.values())

    def supported_agents(self) -> list[str]:
        return list(self._adapters.keys())

    def has_adapter(self, name: str) -> bool:
        return name in self._adapters
