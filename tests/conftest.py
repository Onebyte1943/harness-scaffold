from __future__ import annotations

import pytest


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary directory for testing project initialization."""
    return tmp_path
