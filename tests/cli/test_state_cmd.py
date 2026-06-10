"""Tests for `harness state` — Subsystem 2 (State) CLI."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from harness.cli import cli


def _seed_project(root: Path, *, with_spec: bool = True) -> None:
    """Lay down a minimal harness project with one spec + feature_list.json."""
    runner = CliRunner()
    runner.invoke(cli, ["init", str(root), "--agent", "claude", "--no-git"])
    if with_spec:
        spec = root / "specs" / "001-auth"
        spec.mkdir(parents=True)
        (spec / "feature_list.json").write_text(
            json.dumps(
                {
                    "spec_id": "001",
                    "features": [
                        {
                            "id": "T1.1",
                            "name": "write login test",
                            "depends_on": [],
                            "status": "not-started",
                            "evidence": "",
                            "verification": "uv run pytest tests/test_login.py",
                        },
                        {
                            "id": "T1.2",
                            "name": "implement login",
                            "depends_on": ["T1.1"],
                            "status": "not-started",
                            "evidence": "",
                            "verification": "./init.sh",
                        },
                    ],
                }
            )
        )


def _write_last_verify(root: Path, *, status: str = "green", age_seconds: float = 0.0) -> None:
    payload = {
        "status": status,
        "timestamp": time.time() - age_seconds,
        "target": "all",
    }
    (root / ".harness" / ".last-verify.json").write_text(json.dumps(payload))


class TestShow:
    def test_show_renders_table(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _seed_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "show"])
        assert result.exit_code == 0, result.output
        assert "T1.1" in result.output
        assert "T1.2" in result.output
        assert "001-auth" in result.output

    def test_show_no_specs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _seed_project(tmp_path, with_spec=False)
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "show"])
        assert result.exit_code != 0
        assert "specs/" in result.output.lower()

    def test_show_outside_project(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "show"])
        assert result.exit_code != 0
        assert "harness init" in result.output


class TestNext:
    def test_next_picks_first_executable(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _seed_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "next"])
        assert result.exit_code == 0
        assert "T1.1" in result.output

    def test_next_after_first_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _seed_project(tmp_path)
        # Hand-edit feature_list.json to mark T1.1 passing.
        fl_path = tmp_path / "specs" / "001-auth" / "feature_list.json"
        data = json.loads(fl_path.read_text())
        data["features"][0]["status"] = "passing"
        data["features"][0]["evidence"] = "abc1234"
        fl_path.write_text(json.dumps(data))

        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "next"])
        assert result.exit_code == 0
        assert "T1.2" in result.output


class TestPass:
    def test_pass_requires_evidence(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _seed_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "pass", "T1.1"])
        assert result.exit_code != 0
        assert "evidence" in result.output.lower()

    def test_pass_rejects_without_recent_verify(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _seed_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "pass", "T1.1", "--evidence", "abc1234"])
        assert result.exit_code != 0
        assert "verify" in result.output.lower()

    def test_pass_rejects_red_verify(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _seed_project(tmp_path)
        _write_last_verify(tmp_path, status="red")
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "pass", "T1.1", "--evidence", "abc1234"])
        assert result.exit_code != 0
        assert "red" in result.output.lower() or "not green" in result.output.lower()

    def test_pass_rejects_stale_verify(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _seed_project(tmp_path)
        _write_last_verify(tmp_path, status="green", age_seconds=600)  # 10 min
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "pass", "T1.1", "--evidence", "abc1234"])
        assert result.exit_code != 0
        assert "older" in result.output.lower() or "stale" in result.output.lower()

    def test_pass_succeeds_with_fresh_green(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _seed_project(tmp_path)
        _write_last_verify(tmp_path, status="green", age_seconds=10)
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "pass", "T1.1", "--evidence", "abc1234"])
        assert result.exit_code == 0, result.output
        # JSON updated.
        data = json.loads((tmp_path / "specs" / "001-auth" / "feature_list.json").read_text())
        assert data["features"][0]["status"] == "passing"
        assert data["features"][0]["evidence"] == "abc1234"

    def test_pass_blocked_by_unmet_dependency(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _seed_project(tmp_path)
        _write_last_verify(tmp_path, status="green")
        monkeypatch.chdir(tmp_path)
        # T1.2 depends_on T1.1 — try to skip ahead.
        result = CliRunner().invoke(cli, ["state", "pass", "T1.2", "--evidence", "abc1234"])
        assert result.exit_code != 0
        assert "T1.1" in result.output

    def test_pass_force_skips_freshness_check(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _seed_project(tmp_path)
        # No .last-verify.json at all.
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(
            cli, ["state", "pass", "T1.1", "--evidence", "abc1234", "--force"]
        )
        assert result.exit_code == 0, result.output

    def test_pass_unknown_feature(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _seed_project(tmp_path)
        _write_last_verify(tmp_path)
        monkeypatch.chdir(tmp_path)
        result = CliRunner().invoke(cli, ["state", "pass", "BOGUS", "--evidence", "abc1234"])
        assert result.exit_code != 0
        assert "BOGUS" in result.output
