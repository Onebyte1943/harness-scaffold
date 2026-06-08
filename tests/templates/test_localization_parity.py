"""Parity tests for translatable templates.

Every translatable template ships as a `.zh.md.j2` + `.en.md.j2` pair. The
structural skeleton (section headings, frontmatter, Provenance) MUST be
identical between the two — only narrative prose may differ. These tests
catch drift where one language grows or loses a section.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "src" / "harness" / "templates"

# Stems (path-without-suffix) of every translatable template. The convention
# is `<stem>.{zh,en}.md.j2`.
TRANSLATABLE_STEMS = [
    "harness/playbooks/00-constitution",
    "harness/playbooks/10-baseline",
    "harness/playbooks/12-next",
    "harness/playbooks/30-propose",
    "harness/playbooks/31-clarify",
    "harness/playbooks/32-design",
    "harness/playbooks/33-plan",
    "harness/playbooks/34-tasks",
    "harness/playbooks/35-analyze",
    "harness/playbooks/40-implement",
    "harness/playbooks/41-verify",
    "harness/playbooks/50-review",
    "harness/playbooks/51-archive",
    "harness/playbooks/90-doctor",
    "harness/principle-packs/generic",
    "harness/evals/README",
    "shared/AGENTS",
    "adapters/claude/command",
    "adapters/claude/CLAUDE",
    "adapters/codex/command",
]

# Minimal render context — enough to make every Jinja variable resolvable
# without coupling to the production _build_context().
_RENDER_CONTEXT = {
    "project_name": "demo",
    "profile": "brownfield",
    "flow": "standard",
    "lang": "python",
    "agents": ["claude", "codex"],
    "presets": [],
    "script_shell": "sh",
    "timestamp": "2026-01-01 00:00 UTC",
    "harness_version": "0.1.0",
    "hx_commands": [
        "constitution",
        "baseline",
        "next",
        "propose",
        "clarify",
        "design",
        "plan",
        "tasks",
        "analyze",
        "implement",
        "verify",
        "review",
        "archive",
        "doctor",
    ],
    "specs_dir": "specs",
    "agent_dir": ".agent",
    "knowledge_dir": ".harness/knowledge",
    "principle_packs_dir": ".harness/principle-packs",
    "evals_dir": ".harness/evals",
    "templates_dir": ".harness/templates",
    "knowledge_docs": [],
    # Adapter-template extras
    "command": "verify",
    "description": "demo description",
    "playbook_path": ".harness/playbooks/41-verify.md",
    "constitution_path": ".harness/memory/constitution.md",
    "harness_dir": ".harness",
    "skill_descriptions": {
        cmd: f"{cmd} description"
        for cmd in [
            "constitution",
            "baseline",
            "next",
            "propose",
            "clarify",
            "design",
            "plan",
            "tasks",
            "analyze",
            "implement",
            "verify",
            "review",
            "archive",
            "doctor",
        ]
    },
}


@pytest.fixture(scope="module")
def env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _headings(rendered: str) -> list[str]:
    """Extract the sequence of `## ` / `### ` / `# ` markdown headings,
    skipping lines that sit inside ``` fenced code blocks. The parity
    contract covers the playbook's own outer structure — embedded
    code-block content (e.g. seed-template literals) often translates
    its placeholder text alongside the rest of the narrative, and that
    is intentional, not drift."""
    headings: list[str] = []
    in_fence = False
    for line in rendered.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r"^#{1,6}\s+", line):
            headings.append(line)
    return headings


def _frontmatter(rendered: str) -> str:
    """Extract the YAML frontmatter block (between leading `---` fences),
    or empty if absent."""
    m = re.match(r"\A---\n(.*?\n)---\n", rendered, flags=re.DOTALL)
    return m.group(1) if m else ""


def _provenance_lines(rendered: str) -> list[str]:
    """Every blockquote line that's part of a Provenance block."""
    return [
        line
        for line in rendered.splitlines()
        if line.startswith("> Provenance")
        or line.startswith("> - Authoritative paradigm:")
        or line.startswith("> - Investigation protocol:")
        or line.startswith("> - Output form:")
    ]


@pytest.mark.parametrize("stem", TRANSLATABLE_STEMS)
def test_heading_sequence_parity(stem: str, env: Environment) -> None:
    zh = env.get_template(f"{stem}.zh.md.j2").render(**{**_RENDER_CONTEXT, "output_lang": "zh"})
    en = env.get_template(f"{stem}.en.md.j2").render(**{**_RENDER_CONTEXT, "output_lang": "en"})
    assert _headings(zh) == _headings(en), (
        f"Heading drift in {stem}: zh and en must share the same headings."
    )


@pytest.mark.parametrize("stem", TRANSLATABLE_STEMS)
def test_frontmatter_parity(stem: str, env: Environment) -> None:
    zh = env.get_template(f"{stem}.zh.md.j2").render(**{**_RENDER_CONTEXT, "output_lang": "zh"})
    en = env.get_template(f"{stem}.en.md.j2").render(**{**_RENDER_CONTEXT, "output_lang": "en"})
    assert _frontmatter(zh) == _frontmatter(en), (
        f"Frontmatter drift in {stem}: YAML frontmatter must match exactly."
    )


@pytest.mark.parametrize("stem", TRANSLATABLE_STEMS)
def test_provenance_stays_english(stem: str, env: Environment) -> None:
    """Provenance block (label + 3 content lines) MUST be English in both
    languages. The contract is: agents pattern-match on these labels."""
    zh = env.get_template(f"{stem}.zh.md.j2").render(**{**_RENDER_CONTEXT, "output_lang": "zh"})
    en = env.get_template(f"{stem}.en.md.j2").render(**{**_RENDER_CONTEXT, "output_lang": "en"})
    assert _provenance_lines(zh) == _provenance_lines(en), (
        f"Provenance drift in {stem}: must be English-identical in both."
    )
