"""Tests for harness.core.content_quality — Subsystem 4 (Scope) +
Subsystem 1 (Instructions) baseline / constitution health checks."""

from __future__ import annotations

from pathlib import Path

from harness.core.content_quality import (
    _cite_density,
    _has_numbered_steps,
    _has_table,
    check_constitution_quality,
    check_doc_quality,
)


class TestCiteDensity:
    def test_dense_doc(self, tmp_path: Path) -> None:
        p = tmp_path / "architecture.md"
        p.write_text(
            "Background. Implementation lives in `src/main.py:10` and "
            "is wired up in `src/services/foo.py:42`. Tested via "
            "`tests/test_foo.py:18`. The relevant ADR is ADR-0001.\n"
        )
        density, cites, _ = _cite_density(p)
        assert cites >= 4
        assert density > 1.0

    def test_empty_doc_no_division(self, tmp_path: Path) -> None:
        p = tmp_path / "x.md"
        p.write_text("")
        density, cites, words = _cite_density(p)
        assert density == 0.0
        assert cites == 0
        assert words == 0

    def test_skips_fenced_blocks_for_word_count(self, tmp_path: Path) -> None:
        p = tmp_path / "x.md"
        p.write_text(
            "Real prose here citing src/foo.py:1 once.\n"
            "```python\n"
            "many many many many many words inside a fence\n"
            "but they should not count toward word count\n"
            "```\n"
        )
        _, _, words = _cite_density(p)
        # Only the first line outside the fence is counted.
        assert words < 20


class TestStructureForm:
    def test_table_detected(self) -> None:
        text = "| a | b |\n| - | - |\n| 1 | 2 |\n"
        assert _has_table(text) is True

    def test_no_table(self) -> None:
        assert _has_table("just prose, no pipes") is False

    def test_numbered_steps_detected(self) -> None:
        text = "1. first\n2. second\n3. third\n"
        assert _has_numbered_steps(text) is True

    def test_numbered_steps_with_gap(self) -> None:
        text = "1. first\n   sub\n2. second\n   sub\n3. third\n"
        assert _has_numbered_steps(text) is True

    def test_only_two_steps_not_enough(self) -> None:
        assert _has_numbered_steps("1. a\n2. b\n") is False


class TestCheckDocQuality:
    def test_missing_required_sections_warns(self, tmp_path: Path) -> None:
        # business.md template requires 7 sections; an empty one fails.
        p = tmp_path / "business.md"
        p.write_text("# Business\n\n" + "Some prose with cite src/main.py:1. " * 30)
        rows = check_doc_quality(p)
        # Required headings missing → warn.
        warns = [r for r in rows if r[0] == "warn"]
        assert any("Missing required headings" in r[2] for r in warns)

    def test_low_cite_density_fails(self, tmp_path: Path) -> None:
        p = tmp_path / "architecture.md"
        # ~600 words of prose, no cites → density 0.
        p.write_text(
            "# Architecture\n\n"
            "## L1 — System Context\n## L2 — Containers\n"
            "## Runtime view\n## Cross-cutting\n## Invariants\n\n"
            + "1. step one\n2. step two\n3. step three\n\n"
            + "filler word " * 300
        )
        rows = check_doc_quality(p)
        # 0 cites in 600 words → far below floor → FAIL.
        assert any(r[0] == "error" for r in rows)
        assert any("Cite density" in r[2] for r in rows if r[0] == "error")

    def test_glossary_without_table_warns(self, tmp_path: Path) -> None:
        p = tmp_path / "glossary.md"
        p.write_text("# Glossary\n\nProse paragraph with src/foo.py:1.\n" + "filler word " * 60)
        rows = check_doc_quality(p)
        warn_msgs = [r[2] for r in rows if r[0] == "warn"]
        assert any("ISO 11179" in m for m in warn_msgs)

    def test_glossary_with_table_passes(self, tmp_path: Path) -> None:
        p = tmp_path / "glossary.md"
        p.write_text(
            "# Glossary\n\n"
            "| Term | Definition | First-mentioned-at | Synonyms |\n"
            "| --- | --- | --- | --- |\n"
            "| Foo | Bar | src/foo.py:1 | none |\n" + "filler word " * 60
        )
        rows = check_doc_quality(p)
        # No structure-form warning.
        assert not any("ISO 11179" in r[2] for r in rows)

    def test_skeleton_below_threshold_no_density_warning(self, tmp_path: Path) -> None:
        # < 80 words → density check skipped; required-sections still apply.
        p = tmp_path / "architecture.md"
        p.write_text("# Architecture\n\nTODO\n")
        rows = check_doc_quality(p)
        # No cite-density warn.
        assert not any("Cite density" in r[2] for r in rows)

    def test_setup_and_verify_no_steps_warns(self, tmp_path: Path) -> None:
        p = tmp_path / "setup-and-verify.md"
        p.write_text(
            "# Setup\n\n"
            "## First Run Sequence\n"
            "## Verification Targets\n"
            "## Common Failures\n"
            "## Environment Matrix\n"
            "Just prose with src/foo.py:1.\n" + "filler word " * 60
        )
        rows = check_doc_quality(p)
        assert any("numbered steps" in r[2] for r in rows if r[0] == "warn")


class TestCheckConstitutionQuality:
    def test_missing_version_line(self, tmp_path: Path) -> None:
        p = tmp_path / "constitution.md"
        p.write_text("# Constitution\n\n## Core Principles\n\n## Governance\n")
        rows = check_constitution_quality(p)
        warns = [r[2] for r in rows if r[0] == "warn"]
        assert any("version line" in w.lower() for w in warns)

    def test_missing_governance(self, tmp_path: Path) -> None:
        p = tmp_path / "constitution.md"
        p.write_text(
            "# Constitution\n\n## Core Principles\n\n"
            "**Version**: 1.0.0 | **Ratified**: 2026-06-10 | **Last Amended**: 2026-06-10\n"
        )
        rows = check_constitution_quality(p)
        assert any("Governance" in r[2] for r in rows)

    def test_missing_sync_impact_report(self, tmp_path: Path) -> None:
        p = tmp_path / "constitution.md"
        p.write_text(
            "# Constitution\n\n## Core Principles\n\n## Governance\n\n"
            "**Version**: 1.0.0 | **Ratified**: 2026-06-10 | **Last Amended**: 2026-06-10\n"
        )
        rows = check_constitution_quality(p)
        assert any("Sync Impact Report" in r[2] for r in rows)

    def test_well_formed_passes(self, tmp_path: Path) -> None:
        p = tmp_path / "constitution.md"
        p.write_text(
            "<!--\nSYNC IMPACT REPORT\nVersion: 0.0.0 → 1.0.0\n-->\n\n"
            "# Constitution\n\n## Core Principles\n\n## Governance\n\n"
            "**Version**: 1.0.0 | **Ratified**: 2026-06-10 | **Last Amended**: 2026-06-10\n"
        )
        rows = check_constitution_quality(p)
        assert all(r[0] == "ok" for r in rows)

    def test_lazy_constitution_no_rows(self, tmp_path: Path) -> None:
        # Path that does not exist is handled silently — caller reports
        # missing-doc separately.
        rows = check_constitution_quality(tmp_path / "nope.md")
        assert rows == []
