---
tags:
  - type/data
  - project/system
description: CI-only stand-in for the gitignored, PII-bearing
  tag-taxonomy-rosters.md — carries zero real names, exists only to satisfy
  house-qa's roster-name-leak floor check in public CI.
updated: 2026-09-01
---
# Tag Taxonomy — Rosters (CI placeholder)

**This file carries zero real names.** The real `tag-taxonomy-rosters.md` holds
real person/employer names (PII) and is gitignored — it never exists in a
public CI checkout. house-qa's `qa.py` fails loud without a rosters file at
`Wiki/spec/tag-taxonomy-rosters.md` (roster-name-leak's data source), so the
CI workflow copies this file into that path before running the check.

Consequence, by design: CI's roster-name-leak check only catches a leak of
one of these synthetic placeholder tokens — it can never catch a real-name
leak, because it never has the real roster. The local pre-push hook (which
does have the real, gitignored file) stays the authoritative PII choke —
same redacted-floor principle as `.gitleaks.ci.toml` for gitleaks.

## `person/` roster

Current roster (CI placeholder — not real people): CI Placeholder Alpha, CI Placeholder Beta, CI Placeholder Gamma.

## `area/work/` roster

Current employers (CI placeholder — not real employers): CI Placeholder Employer One, CI Placeholder Employer Two.
