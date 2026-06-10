"""Content-quality checks for baseline / constitution artifacts.

Per AGENTS.md § Subsystems, these checks live under:

- **Instructions** — constitution.md (5-subsystem structure was already
  in 0.3.0; 0.4.0 adds spec-kit version-line + cite-density floor)
- **Scope** — the 7 baseline knowledge docs (cite-density floor +
  required-sections + structure-form)

The checks are deliberately tolerant: they detect *patterns* (cite
markers, headings, tables) rather than parse Markdown ASTs. False
positives are preferred over false negatives — a flagged doc gets
re-baselined; an unflagged doc has at least crossed the form bar.
"""

from __future__ import annotations

import re
from pathlib import Path

CheckRow = tuple[str, str, str]

# Cite tokens we recognise. Any of these counts toward cite-density.
_FILE_EXTS = "py|ts|tsx|js|jsx|go|rs|java|kt|md|sh|toml|yaml|yml|json|j2|sql"
_CITE_PATTERNS = [
    re.compile(rf"\b[\w\-./]+\.(?:{_FILE_EXTS})\b:\d+"),  # path:line
    re.compile(r"\bgit@[0-9a-f]{7,40}\b"),  # git@SHA
    re.compile(r"\b[0-9a-f]{7,40}\b"),  # bare SHA in evidence text
    re.compile(r"\bPRD\s*§"),  # PRD §x.y
    re.compile(r"\bADR-\d{4}\b"),  # ADR-NNNN
    re.compile(r"\b(?:DEC|REQ|RISK|NFR|IF|US|T)-\d+\b"),  # stable IDs
    re.compile(rf"`[^`]+\.(?:{_FILE_EXTS})`"),  # `file.ext`
    re.compile(r"\[ADR-\d+\]"),  # [ADR-NNNN]
]

# Cite density floor: ≥ 1 cite per 200 words averaged across the file.
# We keep the floor permissive (the strict floor is "1 cite per
# *paragraph*", but that catches too many false negatives on bullet
# lists). 200 words is the harness-creator default.
CITE_DENSITY_FLOOR_PER_200_WORDS = 1.0
CITE_DENSITY_FAIL_RATIO = 0.3  # < 30% of floor → FAIL, otherwise WARN

# Per-doc required headings. Missing → WARN.
# Keys are filenames under .harness/knowledge/. Values are required
# (## or ###) headings that the 0.4.0 templates declare.
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "product.md": [
        "## Problem & Users",
        "## Core Capabilities",
        "## Key Journeys",
        "## Performance Targets",
        "## Scope / Non-goals",
    ],
    "architecture.md": [
        "## L1 — System Context",
        "## L2 — Containers",
        "## Runtime view",
        "## Cross-cutting",
        "## Invariants",
    ],
    "tech-stack.md": [
        "## Internal company frameworks",
    ],
    "business.md": [
        "## Business Context",
        "## Stakeholders",
        "## Domain Glossary",
        "## Business Rules",
        "## Key Workflows",
        "## Constraints & Compliance",
        "## Metrics That Matter",
    ],
    "conventions.md": [
        "## Reference Exemplars",
        "## Code Style",
        "## Concurrency & Locks",
        "## Distributed Locks",
        "## Caching",
    ],
    "glossary.md": [],  # single-table file; checked via structure-form
    "setup-and-verify.md": [
        "## First Run Sequence",
        "## Verification Targets",
        "## Common Failures",
        "## Environment Matrix",
    ],
}


def _word_count(text: str) -> int:
    """Cheap word count — splits on whitespace, ignores fenced blocks."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append(line)
    return len(" ".join(out).split())


def _count_cites(text: str) -> int:
    """Count cite occurrences across all patterns."""
    return sum(len(p.findall(text)) for p in _CITE_PATTERNS)


def _cite_density(path: Path) -> tuple[float, int, int]:
    """Return (cites_per_200_words, total_cites, total_words)."""
    try:
        text = path.read_text()
    except OSError:
        return 0.0, 0, 0
    words = _word_count(text)
    cites = _count_cites(text)
    if words == 0:
        return 0.0, cites, 0
    return cites * 200.0 / words, cites, words


def _has_table(text: str) -> bool:
    """Detect a markdown table (header + separator row)."""
    return bool(re.search(r"^\s*\|.+\|\s*\n\s*\|[\s\-|:]+\|\s*$", text, re.MULTILINE))


def _has_numbered_steps(text: str, threshold: int = 3) -> bool:
    """Detect a numbered list with ≥ threshold consecutive steps."""
    pattern = r"^\s*1\..*\n(?:.*\n){0,3}\s*2\..*\n(?:.*\n){0,3}\s*3\."
    return bool(re.search(pattern, text, re.MULTILINE))


def check_doc_quality(path: Path) -> list[CheckRow]:
    """Run all content-quality checks on one knowledge doc.

    Returns 0+ rows. An OK row is emitted only when every check passes
    so doctor's roll-up still shows green when verbose is off.
    """
    rows: list[CheckRow] = []
    rel = f".harness/knowledge/{path.name}"
    if not path.exists():
        return rows  # caller already reported missing-doc separately

    text = path.read_text()
    density, cites, words = _cite_density(path)

    # --- Required sections ------------------------------------------
    required = REQUIRED_SECTIONS.get(path.name, [])
    missing_sections = [h for h in required if h not in text]
    if missing_sections:
        rows.append(
            (
                "warn",
                rel,
                f"Missing required headings: {', '.join(missing_sections[:3])}"
                + (f" (+{len(missing_sections) - 3} more)" if len(missing_sections) > 3 else ""),
            )
        )

    # --- Cite density ----------------------------------------------
    if words < 80:
        # Skeleton-only files are below check threshold — neither
        # OK nor WARN; they will be picked up by required-sections.
        pass
    elif density < CITE_DENSITY_FLOOR_PER_200_WORDS * CITE_DENSITY_FAIL_RATIO:
        rows.append(
            (
                "error",
                rel,
                f"Cite density {density:.2f}/200w (floor {CITE_DENSITY_FLOOR_PER_200_WORDS:.1f}) — "
                f"likely fabricated; rerun /hx-baseline --refresh",
            )
        )
    elif density < CITE_DENSITY_FLOOR_PER_200_WORDS:
        rows.append(
            (
                "warn",
                rel,
                f"Cite density {density:.2f}/200w (floor {CITE_DENSITY_FLOOR_PER_200_WORDS:.1f}) — "
                f"add path:line citations or rerun /hx-baseline",
            )
        )

    # --- Structure form ---------------------------------------------
    # Files whose authoritative form is "single table" must contain a
    # table. Files whose form is procedural must contain numbered steps.
    if path.name == "glossary.md":
        if words >= 80 and not _has_table(text):
            rows.append(("warn", rel, "ISO 11179 form requires a single table"))
    elif path.name == "setup-and-verify.md":
        if words >= 80 and not _has_numbered_steps(text):
            rows.append(("warn", rel, "First Run Sequence must be numbered steps"))
    elif path.name == "architecture.md" and words >= 80 and not _has_numbered_steps(text):
        rows.append(("warn", rel, "Flow Walkthroughs must be numbered steps"))

    # --- OK row only when nothing flagged --------------------------
    if not rows:
        rows.append(("ok", rel, f"{cites} cites · {words} words · {density:.1f} cites/200w"))

    return rows


def check_constitution_quality(path: Path) -> list[CheckRow]:
    """Constitution-specific quality checks per spec-kit standard."""
    rows: list[CheckRow] = []
    rel = ".harness/memory/constitution.md"
    if not path.exists():
        # Lazy — handled by the existing constitution-presence check.
        return rows

    text = path.read_text()

    # Spec-kit version line: `**Version**: X.Y.Z | **Ratified**: ... | **Last Amended**: ...`
    if not re.search(r"\*\*Version\*\*\s*:\s*\d+\.\d+\.\d+", text):
        rows.append(
            (
                "warn",
                rel,
                "Missing spec-kit version line `**Version**: X.Y.Z | ...`",
            )
        )

    # Governance section.
    if "## Governance" not in text:
        rows.append(("warn", rel, "Missing `## Governance` section (spec-kit standard)"))

    # Sync Impact Report at top (HTML comment).
    head = text[:200]
    if not re.search(r"<!--\s*\n?\s*SYNC IMPACT REPORT", head, re.IGNORECASE):
        rows.append(
            (
                "warn",
                rel,
                "Missing Sync Impact Report (HTML comment at top of file)",
            )
        )

    if not rows:
        rows.append(("ok", rel, "spec-kit format OK"))
    return rows
