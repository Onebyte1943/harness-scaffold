"""Tests for harness.core.state — Subsystem 2 (State) loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness.core.state import (
    FeatureListError,
    FeatureStatus,
    find_feature_lists,
    has_cycle,
    load,
)


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))
    return path


def _valid(features: list[dict]) -> dict:
    return {"spec_id": "001", "features": features}


def _feat(
    fid: str,
    *,
    depends_on: list[str] | None = None,
    status: str = "not-started",
    evidence: str = "",
    verification: str = "uv run pytest -q",
) -> dict:
    return {
        "id": fid,
        "name": f"task {fid}",
        "depends_on": depends_on or [],
        "status": status,
        "evidence": evidence,
        "verification": verification,
    }


class TestLoad:
    def test_minimal_valid(self, tmp_path: Path) -> None:
        path = _write(tmp_path / "feature_list.json", _valid([_feat("T1.1")]))
        fl = load(path)
        assert fl.spec_id == "001"
        assert len(fl.features) == 1
        assert fl.features[0].status is FeatureStatus.NOT_STARTED

    def test_invalid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "feature_list.json"
        path.write_text("{not json")
        with pytest.raises(FeatureListError, match="invalid JSON"):
            load(path)

    def test_missing_spec_id(self, tmp_path: Path) -> None:
        path = _write(tmp_path / "feature_list.json", {"features": []})
        with pytest.raises(FeatureListError, match="spec_id"):
            load(path)

    def test_features_not_list(self, tmp_path: Path) -> None:
        path = _write(tmp_path / "feature_list.json", {"spec_id": "001", "features": {}})
        with pytest.raises(FeatureListError, match="must be a list"):
            load(path)

    def test_duplicate_ids(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid([_feat("T1.1"), _feat("T1.1")]),
        )
        with pytest.raises(FeatureListError, match="duplicate"):
            load(path)

    def test_passing_requires_evidence(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid([_feat("T1.1", status="passing", evidence="")]),
        )
        with pytest.raises(FeatureListError, match="empty evidence"):
            load(path)

    def test_unknown_dependency_id(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid([_feat("T1.1", depends_on=["T0.0"])]),
        )
        with pytest.raises(FeatureListError, match=r"unknown id 'T0\.0'"):
            load(path)

    def test_invalid_status_value(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid([_feat("T1.1", status="done")]),
        )
        with pytest.raises(FeatureListError, match="status must be one of"):
            load(path)

    def test_empty_verification_rejected(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid([_feat("T1.1", verification="")]),
        )
        with pytest.raises(FeatureListError, match="verification"):
            load(path)


class TestNextExecutable:
    def test_first_when_no_deps(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid([_feat("T1.1"), _feat("T1.2", depends_on=["T1.1"])]),
        )
        fl = load(path)
        assert fl.next_executable() is not None
        assert fl.next_executable().id == "T1.1"  # type: ignore[union-attr]

    def test_skips_passing(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid(
                [
                    _feat("T1.1", status="passing", evidence="abc123"),
                    _feat("T1.2", depends_on=["T1.1"]),
                ]
            ),
        )
        fl = load(path)
        assert fl.next_executable().id == "T1.2"  # type: ignore[union-attr]

    def test_blocks_when_dep_unfinished(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid(
                [
                    _feat("T1.1", status="in-progress"),
                    _feat("T1.2", depends_on=["T1.1"]),
                ]
            ),
        )
        fl = load(path)
        # T1.1 is still executable (in-progress, no deps); T1.2 is blocked.
        assert fl.next_executable().id == "T1.1"  # type: ignore[union-attr]

    def test_returns_none_when_all_passing(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid([_feat("T1.1", status="passing", evidence="abc123")]),
        )
        fl = load(path)
        assert fl.next_executable() is None


class TestCycleDetection:
    def test_no_cycle(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid([_feat("T1.1"), _feat("T1.2", depends_on=["T1.1"])]),
        )
        fl = load(path)
        assert not has_cycle(fl.features)

    def test_self_loop(self, tmp_path: Path) -> None:
        # depends_on that includes self forms a cycle via DFS grey-node.
        path = _write(
            tmp_path / "feature_list.json",
            _valid([_feat("T1.1", depends_on=["T1.1"])]),
        )
        fl = load(path)
        assert has_cycle(fl.features)

    def test_two_node_cycle(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path / "feature_list.json",
            _valid(
                [
                    _feat("T1.1", depends_on=["T1.2"]),
                    _feat("T1.2", depends_on=["T1.1"]),
                ]
            ),
        )
        fl = load(path)
        assert has_cycle(fl.features)


class TestFindFeatureLists:
    def test_finds_per_spec(self, tmp_path: Path) -> None:
        _write(tmp_path / "specs" / "001-auth" / "feature_list.json", _valid([_feat("T1.1")]))
        _write(tmp_path / "specs" / "002-billing" / "feature_list.json", _valid([_feat("T2.1")]))
        paths = find_feature_lists(tmp_path)
        assert len(paths) == 2
        assert all(p.name == "feature_list.json" for p in paths)

    def test_empty_when_no_specs(self, tmp_path: Path) -> None:
        assert find_feature_lists(tmp_path) == []
