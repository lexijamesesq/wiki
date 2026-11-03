---
tags:
  - type/claude-repo
description: "Claude Code skills that maintain an Obsidian-vault knowledge base — capture routing, gatekeeping, the knowledge-file contract and its lint tool, and per-session maintenance."
docs_home: "{workspace_root}/Wiki"
---

# wiki

The machinery half of a personal knowledge-base system: capture routing (`/wiki-intake`, `/router`), gatekeeping (`/gatekeeper`), the knowledge-file kit (`/knowledge-description`, `/context-page`), maintenance (`/knowledge-layer`, `/lint-knowledge`), and an operator-judgment queue (`/queue`). The notes half — `Knowledge/`, `Data/`, `Contexts/`, `Attachments/`, `Queue/` — lives in the operator's vault, addressed via `{workspace_root}`; this repo never tracks it. Public repo: also the source `wiki` plugin published for other Claude Code sessions to consume.

## Setup

Clone the repo. `.claude/` ships tracked and committed — review its contents (see Security below) before opening the directory in Claude Code. Copy the instance config sample and fill in your own values:

```bash
cp .claude/instance.sample.md .claude/instance.md
```

See `.claude/instance.sample.md` for the full configuration contract (architecture doc link, human-facing surface, stewardship trigger, intake skill name, consolidation threshold, queue taxonomy, freshness window) with placeholder values.

## Configuration

Skills read instance-specific values from `.claude/instance.md`'s Configuration section by key name, not hardcoded, and resolve vault paths from the global Claude Code Configuration block's `workspace_root` and `projects_root` keys. The file contract is `spec/knowledge-files.md`; skills read it, `spec/calibration-surface.md` and `spec/integration-modes.md` from this plugin's own `spec/` folder, never through a vault path. `spec/knowledge-contract.md` is the superseded tag-based rulebook; no skill reads it.

## Build / Test

```bash
python3 .claude/skills/knowledge-description/tests/run_tests.py   # describe and contract-lint tests
pre-commit run --all-files                                         # gitleaks-staged + track-list-guard + the standard hook set
```

## CI

`.github/workflows/ci.yml`, required via the "Protect main" ruleset: the estate's shared `floor` job (`estate-ci.yml` — the shared pre-commit chain, house-code, house-scaffold), plus this repo's own `gate` job (`claude plugin validate --strict` on the plugin manifests) and `release-check` (plugin version discipline). The ruleset requires each job's check directly (`ci / checks`, `ci / gate`, `ci / release-check`); a new job needs its check added to the ruleset in dotty's `rulesets/default-branch.json`. PR-time secret scanning is the trusted lane's `trusted-scan` (`gate.yml`), a separate required check.

## Conventions

- Skills are self-contained `SKILL.md` files under `.claude/skills/{name}/` — no shared runtime beyond the Configuration keys above.
- Instance-specific values are always config keys, never hardcoded — a skill that hardcodes a path breaks for every other fork.
- `.track-list-guard.sh` (a pre-commit hook, not a `.gitignore` pattern) fails the commit if any staged path's top-level component isn't on its explicit allow-list — general drift defense against an undeclared new top-level path landing here, independent of and in addition to `.gitignore`.
- Commits: gitleaks-staged/-pre-push/-commit-msg (dotty's exported hooks) gate every commit and push locally; CI re-proves the outgoing PR range independently.
- This repo root is the published `wiki` plugin: a skill rename or removal here changes what every installed consumer loads on its next `claude plugin update wiki@wiki`; check before renaming.

## Key Files

| File | Purpose |
| ---- | ------- |
| `.claude/instance.sample.md` | Configuration contract template — copy to `.claude/instance.md` and fill in your instance's values |
| `.claude/skills/` | The ingress (`wiki-intake`, `router`, `queue`), gatekeeping (`gatekeeper`), knowledge-file kit (`knowledge-description`, `context-page`), and maintenance (`knowledge-layer`, `lint-knowledge`) skills |
| `.claude-plugin/` | The `wiki` marketplace and plugin manifests — this repo root is the plugin; `plugin.json`'s `skills` field points at `.claude/skills/` |
| `spec/knowledge-files.md` | The knowledge-file contract — four frontmatter fields, three update modes, type folders |
| `spec/knowledge-contract.md` | The superseded tag-based rulebook, kept until it is retired; no skill reads it |
| `spec/calibration-surface.md`, `spec/integration-modes.md` | Ingress judgment tables and per-destination write discipline |
