---
tags:
  - type/data
  - project/system
description: CI-only stand-in for the gitignored, PII-bearing
  tag-taxonomy-rosters.md — carries zero real names, exists only to satisfy
  house-qa's roster-name-leak floor check in public CI.
updated: 2026-09-03
---
# Tag Taxonomy — Rosters (CI placeholder)

**This file carries zero real names.** The real roster (person/employer names,
PII) is declared in `dotty-private`'s repo root and blueprint-applied to
`${XDG_CONFIG_HOME:-$HOME/.config}/estate/tag-taxonomy-rosters.md` on every
machine (`references.tag_taxonomy_rosters`, LEX-718 Piece B) — this repo no
longer carries a real copy at all, gitignored or otherwise. house-qa's `qa.py`
fails loud without a rosters file at its resolved `--rosters-path`, so the CI
workflow copies this file into the pre-key fallback path
(`Wiki/spec/tag-taxonomy-rosters.md`) before running the check, for
environments (like CI) that cannot reach the real fixed path.

Consequence, by design: CI's roster-name-leak check only catches a leak of
one of these synthetic placeholder tokens — it can never catch a real-name
leak, because it never has the real roster. The local pre-push hook (which
does have the real, gitignored file) stays the authoritative PII choke —
same redacted-floor principle as `.gitleaks.ci.toml` for gitleaks.

## `person/` roster

Current roster (CI placeholder — not real people): CI Placeholder Alpha, CI Placeholder Beta, CI Placeholder Gamma.

## `area/work/` roster

Current employers (CI placeholder — not real employers): CI Placeholder Employer One, CI Placeholder Employer Two.
