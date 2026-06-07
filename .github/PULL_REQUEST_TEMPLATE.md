## Summary

<!-- One or two sentences: what changes and why. Link the issue this
     PR addresses: Fixes #N / Refs #N. -->

## Changes

<!-- Bullet list of the concrete changes a reviewer should look for. -->

-
-

## Verification

<!-- How did you confirm this works? "All tests pass" is not enough;
     name the specific behaviors you exercised. -->

- [ ] `uv run ruff check src tests` passes
- [ ] `uv run ruff format --check src tests` passes
- [ ] `uv run mypy src` passes
- [ ] `uv run pytest` passes
- [ ] Manual check: <describe>

## Localization

<!-- Only required if you touched anything under
     src/harness/templates/. Delete this section otherwise. -->

- [ ] Both `.zh.md.j2` and `.en.md.j2` variants updated
- [ ] Structural items (headings, frontmatter, Provenance) byte-identical
- [ ] `test_localization_parity.py` still passes

## Changelog

- [ ] Added an entry under `## [Unreleased]` in `CHANGELOG.md`
      (delete if this is a docs-only / internal-only change)
