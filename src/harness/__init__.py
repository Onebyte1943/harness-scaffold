"""Harness — Unified AI agent engineering scaffold for teams."""

from importlib.metadata import PackageNotFoundError, version

# Distribution name on PyPI is `harness-scaffold`; the importable module
# stays `harness`. Keep these two in sync with [project].name in
# pyproject.toml.
try:
    __version__ = version("harness-scaffold")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
