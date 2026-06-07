from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from harness.core.registry import AdapterSpec
from harness.core.scaffold import ScaffoldEngine


class AdapterBase(ABC):
    """Base class for terminal adapters."""

    def __init__(self, spec: AdapterSpec, engine: ScaffoldEngine) -> None:
        self.spec = spec
        self.engine = engine

    @property
    def name(self) -> str:
        return self.spec.name

    @abstractmethod
    def generate(
        self,
        project_root: Path,
        context: dict[str, Any],
        *,
        force: bool = False,
        dry_run: bool = False,
    ) -> list[Path]:
        """Generate adapter files for this terminal. Returns list of generated file paths."""

    @abstractmethod
    def validate(self, project_root: Path) -> list[str]:
        """Validate adapter file integrity. Returns list of issues found."""

    def get_degradation_info(self) -> dict[str, str]:
        """Return capability degradation notes."""
        result = {}
        for cap_name, cap_spec in self.spec.capabilities.items():
            if not cap_spec.supported and cap_spec.degradation:
                result[cap_name] = cap_spec.degradation
        return result
