"""Seed-contract parity tests.

A subset of translatable templates contains ``` fenced code blocks that
hold *seeds* — verbatim text that downstream `/hx-*` commands write into
the project (e.g. `constitution.md`, knowledge-base docs, `progress.md`,
ADR / proposal / design / plan / tasks / review report templates,
how-to/* recipes, eval samples).

These seed bodies are **L-CONTRACT**, not L-NARRATIVE: the precise
wording is what `/hx-review`, `/hx-analyze`, `/hx-doctor`, `/hx-implement`
pattern-match against. Translating a seed (even if the surrounding zh
prose is translated) silently degrades AI-coding accuracy because the
agent loses the lexical cues it was trained on.

The contract: **fenced code-block content MUST be byte-identical between
`<stem>.zh.md.j2` and `<stem>.en.md.j2`** after Jinja rendering. Outer
prose, headings, and Provenance may differ; only ``` block bodies are
covenant text.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

# Re-use the parity test's render context so the two files stay in sync
# on the Jinja-variable contract.
from tests.templates.test_localization_parity import (
    _RENDER_CONTEXT,
    TEMPLATES_DIR,
)

# Templates whose ``` blocks carry seed contracts. The full TRANSLATABLE
# set lives in test_localization_parity; this list is the subset whose
# fenced blocks are seeds for project artifacts. Slash-command adapter
# templates (claude / codex command + CLAUDE.md) are intentionally NOT
# here — their code blocks are usage examples, not project seeds.
SEED_TEMPLATE_STEMS = [
    "harness/playbooks/00-constitution",
    "harness/playbooks/10-baseline",
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
    "harness/evals/README",
]

_FENCE = re.compile(r"^```")


def _fenced_blocks(rendered: str) -> list[str]:
    """Return the body of every ``` fenced code block, in document order.

    The block's body is the lines between the opening and closing fence,
    joined with `\\n`. The fence info-string (e.g. ```markdown,
    ```mermaid) is preserved on the first line of the captured block so
    that a missing or changed language tag is a parity failure too.
    """
    blocks: list[str] = []
    current: list[str] | None = None
    for line in rendered.splitlines():
        if _FENCE.match(line.lstrip()):
            if current is None:
                # Capture the fence line so the info-string is compared.
                current = [line]
            else:
                current.append(line)
                blocks.append("\n".join(current))
                current = None
            continue
        if current is not None:
            current.append(line)
    if current is not None:
        # Unclosed fence — flag by appending what we have; the test will
        # surface the asymmetry on the en/zh comparison.
        blocks.append("\n".join(current))
    return blocks


@pytest.fixture(scope="module")
def env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.mark.parametrize("stem", SEED_TEMPLATE_STEMS)
def test_seed_blocks_identical(stem: str, env: Environment) -> None:
    """Fenced code blocks in zh and en variants MUST be byte-identical.

    Translating prose outside the fence is encouraged; translating
    content inside the fence breaks the AI-coding contract and is
    blocked by this test."""
    zh = env.get_template(f"{stem}.zh.md.j2").render(
        **{**_RENDER_CONTEXT, "output_lang": "zh"}
    )
    en = env.get_template(f"{stem}.en.md.j2").render(
        **{**_RENDER_CONTEXT, "output_lang": "en"}
    )
    zh_blocks = _fenced_blocks(zh)
    en_blocks = _fenced_blocks(en)
    assert len(zh_blocks) == len(en_blocks), (
        f"Fenced-block count drift in {stem}: zh has {len(zh_blocks)}, "
        f"en has {len(en_blocks)}. The seed-contract layer requires the "
        f"same number of ``` blocks in both languages."
    )
    for idx, (zh_block, en_block) in enumerate(zip(zh_blocks, en_blocks)):
        assert zh_block == en_block, (
            f"Seed-contract drift in {stem}, fenced block #{idx + 1}.\n"
            f"Code-block content is the AI-coding contract and MUST be "
            f"byte-identical between zh and en. Translate prose outside "
            f"the ``` fence, not inside.\n"
            f"\n--- zh ---\n{zh_block}\n--- en ---\n{en_block}\n"
        )


def test_seed_stems_are_subset_of_translatable() -> None:
    """Guard: every seed stem must appear in TRANSLATABLE_STEMS so the
    heading/frontmatter/Provenance parity tests also run on it."""
    from tests.templates.test_localization_parity import TRANSLATABLE_STEMS

    missing = [s for s in SEED_TEMPLATE_STEMS if s not in TRANSLATABLE_STEMS]
    assert not missing, (
        f"Seed stems must also be in TRANSLATABLE_STEMS: {missing}"
    )


def _list_md_zh_stems() -> list[str]:
    """All translatable Markdown template stems present on disk."""
    found: list[str] = []
    for path in TEMPLATES_DIR.rglob("*.zh.md.j2"):
        rel = path.relative_to(TEMPLATES_DIR).as_posix()
        found.append(rel.removesuffix(".zh.md.j2"))
    return sorted(found)


def test_no_seed_stem_silently_dropped() -> None:
    """Guard: if a template has ``` blocks, it is most likely a seed
    holder. This test surfaces newly-added templates that contain code
    blocks but were never added to SEED_TEMPLATE_STEMS, so a reviewer
    consciously decides whether the new template's blocks are seeds
    (add to the list) or usage examples (leave out)."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    candidates: list[str] = []
    # Adapter command stems carry usage examples, not seeds — exempt.
    exempt = {
        "adapters/claude/CLAUDE",
        "adapters/claude/command",
        "adapters/codex/command",
        "harness/principle-packs/generic",
        "shared/AGENTS",
    }
    for stem in _list_md_zh_stems():
        if stem in SEED_TEMPLATE_STEMS or stem in exempt:
            continue
        try:
            rendered = env.get_template(f"{stem}.zh.md.j2").render(
                **{**_RENDER_CONTEXT, "output_lang": "zh"}
            )
        except Exception:
            continue
        if _fenced_blocks(rendered):
            candidates.append(stem)
    assert not candidates, (
        "New translatable templates with ``` fenced blocks must be "
        "classified as seed (add to SEED_TEMPLATE_STEMS) or usage "
        f"example (add to `exempt`): {candidates}"
    )
