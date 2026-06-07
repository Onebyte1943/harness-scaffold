"""Terminal adapters package."""

from __future__ import annotations

from harness.adapters.base import AdapterBase
from harness.core.registry import AdapterSpec
from harness.core.scaffold import ScaffoldEngine

_ADAPTER_CLASSES: dict[str, type[AdapterBase]] = {}


def _ensure_registered() -> None:
    if _ADAPTER_CLASSES:
        return
    from harness.adapters.claude import ClaudeAdapter
    from harness.adapters.codex import CodexAdapter

    _ADAPTER_CLASSES["claude"] = ClaudeAdapter
    _ADAPTER_CLASSES["codex"] = CodexAdapter


def get_adapter(name: str, engine: ScaffoldEngine) -> AdapterBase:
    """Get an adapter instance by name."""
    _ensure_registered()
    if name not in _ADAPTER_CLASSES:
        raise KeyError(f"No adapter for '{name}'. Available: {list(_ADAPTER_CLASSES.keys())}")
    spec = AdapterSpec(
        name=name,
        adapter_type="cli",
        config_dir=f".{name}",
        context_file="CLAUDE.md" if name == "claude" else "AGENTS.md",
        command_format="/hx-{cmd}",
        templates_dir=name,
    )
    return _ADAPTER_CLASSES[name](spec, engine)
