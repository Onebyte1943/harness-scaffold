"""Subsystem 2 — State.

Loads, validates, and queries `specs/<NNN>-<slug>/feature_list.json`.

This module is the single Python surface for State across the project:
the `harness state` CLI (init_cmd siblings), `harness doctor` (the State
row in the 5-subsystem health table), and any future automation read
state through these helpers — never by re-implementing JSON parsing.

The schema is mirrored in
`.harness/templates/feature_list.schema.json` (rendered into each
project at init time). Keep this module's vocabulary aligned with the
schema's `enum`s so a JSON file that validates against the schema also
parses cleanly here, and vice versa.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class FeatureStatus(str, Enum):
    """Mirrors the `status.enum` in feature_list.schema.json."""

    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    PASSING = "passing"


@dataclass(frozen=True, slots=True)
class Feature:
    id: str
    name: str
    depends_on: tuple[str, ...]
    status: FeatureStatus
    evidence: str
    verification: str


@dataclass(frozen=True, slots=True)
class FeatureList:
    """In-memory view of a spec's feature_list.json."""

    spec_id: str
    features: tuple[Feature, ...]
    path: Path

    def by_id(self, feat_id: str) -> Feature | None:
        return next((f for f in self.features if f.id == feat_id), None)

    def next_executable(self) -> Feature | None:
        """First feature with all `depends_on` passing and `status != passing`.

        Mirrors the runtime contract in AGENTS.md § 2.2: the agent picks
        exactly one such feature per session. Returns None when nothing
        is executable (everything passing, or a dependency cycle has
        blocked progress).
        """
        passing = {f.id for f in self.features if f.status is FeatureStatus.PASSING}
        for f in self.features:
            if f.status is FeatureStatus.PASSING:
                continue
            if all(d in passing for d in f.depends_on):
                return f
        return None


class FeatureListError(ValueError):
    """Schema-violating feature_list.json. Doctor turns this into a FAIL row."""


def load(path: Path) -> FeatureList:
    """Load + validate a feature_list.json. Raises FeatureListError on
    schema violations the agent could plausibly introduce by hand-editing.
    """
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise FeatureListError(f"{path}: invalid JSON — {exc}") from exc

    if not isinstance(raw, dict):
        raise FeatureListError(f"{path}: top-level must be an object")

    spec_id = raw.get("spec_id")
    if not isinstance(spec_id, str) or not spec_id:
        raise FeatureListError(f"{path}: missing or empty 'spec_id'")

    raw_features = raw.get("features")
    if not isinstance(raw_features, list):
        raise FeatureListError(f"{path}: 'features' must be a list")

    features: list[Feature] = []
    seen_ids: set[str] = set()
    for i, item in enumerate(raw_features):
        if not isinstance(item, dict):
            raise FeatureListError(f"{path}: features[{i}] must be an object")
        for required in ("id", "name", "depends_on", "status", "evidence", "verification"):
            if required not in item:
                raise FeatureListError(f"{path}: features[{i}] missing '{required}'")
        feat_id = item["id"]
        if not isinstance(feat_id, str) or not feat_id:
            raise FeatureListError(f"{path}: features[{i}].id must be a non-empty string")
        if feat_id in seen_ids:
            raise FeatureListError(f"{path}: duplicate feature id '{feat_id}'")
        seen_ids.add(feat_id)
        deps = item["depends_on"]
        if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
            raise FeatureListError(f"{path}: features[{i}].depends_on must be an array of strings")
        try:
            status = FeatureStatus(item["status"])
        except ValueError as exc:
            raise FeatureListError(
                f"{path}: features[{i}].status must be one of {[s.value for s in FeatureStatus]}"
            ) from exc
        evidence = item["evidence"]
        if not isinstance(evidence, str):
            raise FeatureListError(f"{path}: features[{i}].evidence must be a string")
        if status is FeatureStatus.PASSING and not evidence.strip():
            raise FeatureListError(
                f"{path}: feature '{feat_id}' is 'passing' but has empty evidence"
            )
        verification = item["verification"]
        if not isinstance(verification, str) or not verification.strip():
            raise FeatureListError(f"{path}: features[{i}].verification must be a non-empty string")
        features.append(
            Feature(
                id=feat_id,
                name=str(item["name"]),
                depends_on=tuple(deps),
                status=status,
                evidence=evidence,
                verification=verification,
            )
        )

    # depends_on references must resolve.
    for f in features:
        for d in f.depends_on:
            if d not in seen_ids:
                raise FeatureListError(f"{path}: feature '{f.id}' depends on unknown id '{d}'")

    return FeatureList(spec_id=spec_id, features=tuple(features), path=path)


def find_feature_lists(project_root: Path) -> list[Path]:
    """Find every spec's feature_list.json under a harness project."""
    specs = project_root / "specs"
    if not specs.is_dir():
        return []
    return sorted(specs.glob("*/feature_list.json"))


def has_cycle(features: tuple[Feature, ...]) -> bool:
    """Detect a cycle in the depends_on graph."""
    by_id = {f.id: f for f in features}
    WHITE, GREY, BLACK = 0, 1, 2
    color = dict.fromkeys(by_id, WHITE)

    def dfs(node: str) -> bool:
        color[node] = GREY
        for nxt in by_id[node].depends_on:
            if nxt not in by_id:
                continue
            if color[nxt] == GREY:
                return True
            if color[nxt] == WHITE and dfs(nxt):
                return True
        color[node] = BLACK
        return False

    return any(color[f_id] == WHITE and dfs(f_id) for f_id in by_id)
