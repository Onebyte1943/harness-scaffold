"""Harness — Unified AI agent engineering scaffold for teams."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("harness")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
