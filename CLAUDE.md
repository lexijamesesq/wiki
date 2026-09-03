---
tags:
  - type/claude-repo
description: "Claude Code skills that maintain an Obsidian-vault knowledge base — capture routing, gatekeeping, lint, and maintenance, plus the contracts that generate the lint rules."
docs_home: "{workspace_root}/Wiki"
---

# wiki

The machinery half of a personal knowledge-base system: capture routing (`/wiki-intake`, `/capture`, `/capture-meeting`, `/router`), gatekeeping (`/gatekeeper`), maintenance (`/knowledge-layer`, `/lint-knowledge`, `/maintenance-triage`), and an operator-judgment queue (`/queue`). The notes half — `Knowledge/`, `Data/`, `Contexts/`, `Attachments/`, `Queue/` — lives in the operator's vault, addressed via `{workspace_root}`; this repo never tracks it. Public repo: also the source `wiki` plugin published for other Claude Code sessions to consume.

## Setup

Clone the repo. `.claude/` ships tracked and committed — review its contents (see Security below) before opening the directory in Claude Code. Copy the instance config sample and fill in your own values:

```
cp .claude/instance.sample.md .claude/instance.md
```

See `.claude/instance.sample.md` for the full configuration contract (architecture doc link, human-facing surface, stewardship trigger, intake skill name, consolidation threshold, automated-lane scope, queue taxonomy, freshness window) with placeholder values.

## Configuration

Skills read instance-specific values from `.claude/instance.md`'s Configuration section by key name, not hardcoded. `spec/knowledge-contract.md` (tag taxonomy, envelope rules) and `spec/tag-taxonomy-rosters.md` (real person/employer names, gitignored — every fork creates its own) are resolved by three consumers via config key, never a hardcoded path: `references.tag_taxonomy` / `references.structural_contract` / `references.handoff_contracts` / `references.lint_surface` (four aliases, one file) and `references.tag_taxonomy_rosters`, both in the global Claude Code Configuration block — set once, consumed by `lint.py`, `qa.py`, and the three ingress/gatekeeping skills. `spec/tag-taxonomy-rosters.md` itself is gitignored; a CI-safe placeholder (`spec/tag-taxonomy-rosters.ci-placeholder.md`) stands in for it in CI.

## Build / Test

```bash
python3 .claude/skills/lint-knowledge/tests/run_tests.py   # 135 lint.py unit tests
pre-commit run --all-files                                  # gitleaks-staged + track-list-guard + the standard hook set
```

## CI

`.github/workflows/ci.yml`, required via the "Protect main" ruleset: the `lint-knowledge` test suite, house-qa's mechanical check (`qa.py`, scoped to `.claude/skills`, gated on this PR's changed files — pre-existing debt never blocks), and gitleaks (full outgoing PR-range scan via dotty's shared `setup-gitleaks` composite action, base rules only + `--redact` — public repo, the operator's PII ruleset never reaches CI). All three required to merge.

## Conventions

- Skills are self-contained `SKILL.md` files under `.claude/skills/{name}/` — no shared runtime beyond the Configuration keys above.
- Instance-specific values are always config keys, never hardcoded — a skill that hardcodes a path breaks for every other fork.
- `.track-list-guard.sh` (a pre-commit hook, not a `.gitignore` pattern) fails the commit if any staged path's top-level component isn't on its explicit allow-list — general drift defense against an undeclared new top-level path landing here, independent of and in addition to `.gitignore`.
- Commits: gitleaks-staged/-pre-push/-commit-msg (dotty's exported hooks) gate every commit and push locally; CI re-proves the outgoing PR range independently.
- This repo is a shared-skill source consumed by the `wiki` plugin — a skill/agent rename or removal here can break that consumer; check before renaming.

## Key Files

| File | Purpose |
|------|---------|
| `.claude/instance.sample.md` | Configuration contract template — copy to `.claude/instance.md` and fill in your instance's values |
| `.claude/skills/` | The ingress (`wiki-intake`, `capture`, `capture-meeting`, `router`, `queue`), gatekeeping (`gatekeeper`), and maintenance (`knowledge-layer`, `lint-knowledge`, `maintenance-triage`) skills |
| `spec/knowledge-contract.md` | The consolidated rulebook — tag namespaces, file envelope, write ownership, lint rules, parsing contract |
| `spec/tag-taxonomy-rosters.md` | Real-name rosters, gitignored — every fork creates its own |
| `spec/calibration-surface.md`, `spec/integration-modes.md` | Ingress judgment tables and per-destination write discipline |
