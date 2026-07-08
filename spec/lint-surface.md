---
tags:
  - type/spec
  - project/system
  - status/active
updated: 2026-05-22
---

# Lint Surface

The complete set of integrity checks that verify vault content against its contracts. **Lint is the executable form of the contracts.** `/lint-knowledge` derives its rule *values* at runtime from the contracts' Parsing Contracts — [[tag-taxonomy]] for tags, [[structural-contract]] for the envelope — rather than hardcoding them.

Sibling of [[structural-contract]], [[handoff-contracts]], and [[tag-taxonomy]]. This doc specs the *surface* — every check, its rule source, execution mode, which pass runs it, severity, and whether it exists today. It does not re-derive the rules; those live in the contracts.

**Scope:** integrity checks only (Layers 1–2). Associative-layer integrity — stale relationships, retrieval-reflex coverage — is tracked separately.

---

## Two execution modes

A check runs at filing-time, periodically, or both. The split follows one principle: **single-file-at-creation → filing-time; drift-over-time or corpus-scale → periodic.**

| Mode | Catches | Mechanism |
|---|---|---|
| **Filing-time** | Envelope violations on a new file, before they persist | The `filing-validator` critic-subagent validates the filed file against [[structural-contract]]'s Parsing Contract + the relevant [[handoff-contracts]] §. Single-file, cheap. Built — ships with the `/lint-knowledge` skill in the public dotty repo. |
| **Periodic** | Drift that emerges after filing — staleness, broken links, index drift, contradictions; `[tightening]` rules flagging legacy files | **Two passes.** A **mechanical pass** (a script, no model) runs every deterministic check; a **judgment pass** (a model) runs the contradiction scan. See below. |

Envelope-compliance checks run **both** — filing-time on the new file, and in the periodic mechanical pass as `[tightening]` rules escalate against the legacy corpus.

---

## Periodic mode — mechanical pass + judgment pass

The periodic surface was originally specced as a single Claude session reading every governed file (~370+) on every run. That is mis-designed: it AI-ifies deterministic work, and re-reads a mostly-static corpus with model reasoning every run — prohibitively expensive, and never costed. The periodic mode is **two passes**, split on one line:

> **If a check is deterministic, a script runs it. If a check needs judgment, a model runs it.**

This is the dividing line the methodology already draws — *if a rule needs judgment to check, it is not a contract rule*. The contracts were built so every contract rule is mechanically checkable; the mechanical pass is that promise kept. The split is **orthogonal** to the contract-derived (SC/TT) vs. lint-heuristic (LINT) source split — most LINT-sourced checks (broken links, orphan index entries, status coherence) are still mechanical. Exactly one periodic check is genuine judgment: the contradiction scan.

### Mechanical pass — a script, full-corpus, no model

A standalone script (`lint.py`, bundled with the `/lint-knowledge` skill) runs every deterministic check in the inventory below. It:

- **Derives rule values at runtime from the contracts.** It reads the closed `type/`/`status/` vocabularies, depth limits, namespace prefixes, the exemption tiers, per-type additions, and destination modifiers by parsing [[tag-taxonomy]] and [[structural-contract]] per their **Parsing Contract** sections. The contracts stay the single source of truth; the script holds no copy of a vocabulary or a limit. The script *does* encode the parsing recipe and the check implementations — that is what a Parsing Contract is *for*: the stable doc↔tooling interface. Adding a new *kind* of check is a script change, exactly as it is a spec change today (`/lint-knowledge` Decision Authority is unchanged). What the script never does is hardcode a rule *value* that a contract owns.
- **Runs on the full corpus every run.** The mechanical pass has no API cost — it is local CPU, seconds for the whole vault. And it *must* be full-corpus: the relational checks (broken wikilinks, cross-project refs, `index.md` integrity, stub drift, context-page coverage, `topic/` consolidation) are corpus-scale by nature — a file's wikilink breaks when its *target* is deleted, not when the file itself changes. Delta-scoping a relational check to changed-files-only produces false negatives. Because the pass is free, run it whole.
- **Uses no model. Read-only.** Emits structured JSON (findings + the computed delta set) and a human-readable report.

### Judgment pass — a model, delta-scoped

One periodic check is genuine judgment: the **contradiction scan** — claims contradicted by a scope's `CLAUDE.md` Current State or by other knowledge pages (`/lint-knowledge` Step 6), plus, for a hub/subproject scope, the hub cross-reference (Step 7). It stays a best-effort INFO heuristic and is not contract-derived. It is the only component that costs model tokens.

The judgment pass is **delta-scoped** — it runs only over files changed since the last run. This is the cost fix. It is **cost-sound, and best-effort on coverage** — consistent with the contradiction scan's INFO, best-effort status: delta-scoping narrows where the scan looks, it does not change its severity tier. A contradiction *comes into existence* only when a file changes (or when the scope's `CLAUDE.md` changes), so scanning the delta set catches newly-introduced contradictions at their source — when file A changes, A is scanned against current state. **CLAUDE.md rule:** if the scope's `CLAUDE.md` is itself in the delta set, widen the judgment pass to all of that scope's knowledge files — a Current State edit can retroactively contradict unchanged pages. **Two accepted coverage gaps:** a contradiction between a changed file A and an *unchanged* non-`CLAUDE.md` page B is caught only if A's scan loads B; and contradictions predating the first run are caught by the first run (delta = whole scope) or an occasional `--full` pass.

### Change detection — the manifest

The vault is not git-tracked (Obsidian-synced), so the delta is computed against a **manifest**: a JSON file mapping each in-scope file's vault-relative path → SHA-256 content hash, plus the run timestamp. Each run, the script walks the scope, hashes every file, and diffs against the stored manifest:

- hash differs → **changed**; path absent from manifest → **new**; path in manifest, gone from disk → **deleted**.
- **Delta set** = changed ∪ new. Deleted files are reported (they matter to the relational mechanical checks) but not re-linted.

The manifest is the last-run marker. Content hashing — not mtime — is used because Obsidian Sync rewrites mtimes on every sync; mtime would produce spurious deltas, while hashing is exact and, in a script, costs milliseconds. One manifest per scope, stored in a local state directory outside both the vault and the [dotty](https://github.com/lexijamesesq/dotty) repo (default `~/.cache/lint-knowledge/`, keyed by scope path; `--state-dir` overrides). First run for a scope = no manifest → every file is "new" → delta = whole scope (the expected legacy / first pass).

### Cost

| Work | Before (specced) | After |
|---|---|---|
| Mechanical (~all checks) | Claude session, full-corpus read of ~370+ files — bodies read for H1; hundreds of K to >1M tokens/run, multi-turn | Local script, ~0 API cost, seconds |
| Judgment (contradiction scan) | Same session, full-corpus | Model, **delta-scoped** — typically 0–~15 files/run; empty delta → pass skipped → $0 |
| Per-run cost | Several USD, every run | **$0** when nothing changed; cents when it did |

Two-plus orders of magnitude, with a **$0 floor** on a no-change run. The mechanical pass no longer needs a Claude session at all — it is cron-able directly. Only the judgment pass needs a model. **This resizes the trigger design:** the periodic lint is mostly a free script, not an expensive AI session — the trigger only has to wake a model when the delta is non-empty.

### Script ↔ skill interface

| Surface | Responsibility |
|---|---|
| `lint.py` (script) | The mechanical pass + delta computation. Args: scope path; `--json` / `--format text`; `--state-dir`; `--no-manifest` (stateless full run, no delta — for CI / one-offs). Emits mechanical findings + the delta set. |
| `/lint-knowledge` (skill) | Orchestrates: runs `lint.py`, then runs the judgment pass over the delta set (or the whole scope under `--full`), and merges both into the unified report. Flags: `--scope`, `--mechanical-only` (skip the judgment pass — pure script, $0), `--full` (judgment pass over the whole scope — first runs, migration validation, on-demand deep checks). |

The legacy `--taxonomy-only` and `--metadata-first` flags are retired: the mechanical pass is cheap enough that subsetting it has no purpose, and the script reads files directly so the metadata-first optimization is moot.

---

## Check inventory

Source: **SC** = [[structural-contract]] · **TT** = [[tag-taxonomy]] · **HC** = [[handoff-contracts]] · **LINT** = lint's own QA heuristic, not contract-derived. Pass: **M** = mechanical (script) · **J** = judgment (model). Today: ✓ exists in `/lint-knowledge` · ◐ partial · ✗ missing.

### Envelope — Invariant Core (SC)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Exactly one valid `type/` tag | Both | M | HIGH | ✓ |
| ≥1 scope tag (`project/` or `area/`) | Both | M | HIGH | ✓ |
| Scope tag matches destination | Both | M | HIGH | ✗ |
| Exactly one `status/` tag | Both | M | HIGH `[tightening]` | ◐ (WARNING today) |
| `updated: YYYY-MM-DD` present | Both | M | HIGH | ✓ |
| Exactly one H1 (`# Title`) | Both | M | HIGH `[tightening]` | ✗ |
| All tags valid per [[tag-taxonomy]] | Both | M | per the Tag-taxonomy block | ✓ |

These checks apply only to files in **governed scope** — [[structural-contract]]'s **Location Gate** is the outer filter: lint runs envelope/tag checks only on files under the governed locations (`System/*.md`, `System/Knowledge/`, `System/Context/`, `Projects/*/Knowledge/`, `Projects/*/Context/`, `Wiki/Knowledge/`, `Wiki/Contexts/`). Every other path — domain content (`Wiki/Data/`), operational records (`Recruiting/Roles|Playbooks|Candidates`), archives (`*-archive.md`, `Archived/`), raw/operational scratch (`Projects/*/Research|Activity|Ideas|...`), Incubator cards — is skipped entirely: no envelope check, no tag-validity check, no `no-type-tag` finding.

Within governed scope, the file's `type/` places it in an **Exemption tier**: fully-governed knowledge-layer types and *Invariant-core-only* types are held to the Invariant Core; *Structure-not-imposed* types (`claude-*` sidecars, `type/summary`, `type/scratchpad`, `type/working-notes`, `type/working-doc`, `type/exploration`, `type/playbook`) get only tag-validity; *Out-of-scope* types (`type/data`, `type/meeting-capture`) get no check at all. The mechanical-pass script derives the Location Gate globs and the tier sets from the contract's Scope Boundaries tables at runtime — it does not hardcode them.

### Envelope — Per-Type (SC)

Rows only for types with a required addition beyond the invariant core. All other governed types are invariant-core-only.

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| `type/knowledge` carries `sources` | Both | M | HIGH | ✓ |
| `type/knowledge` Wiki-hosted carries `topic/` ≥1 | Both | M | HIGH `[tightening]` | ✗ |
| `type/project-pointer` carries `project/` + `topic/` | Periodic | M | HIGH | ✗ |

`type/project-pointer` is `Periodic`-only: no filing handoff produces a pointer (§1/§2/§3 all file `type/knowledge`/`type/context`/synthesis), so the filing-time critic never validates one. Per-type checks apply only to the knowledge-layer types in [[structural-contract]]'s Per-Type table; types in either Exemption tier are exempt from per-type additions — the script reads the Exemption tiers table at runtime to know which.

### Tag taxonomy (TT — all exist)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Namespace membership; closed `type/`·`status/`·`project/` vocab | Both | M | HIGH | ✓ |
| Depth limits | Both | M | HIGH | ✓ |
| `area/` · `person/` recognition | Both | M | WARNING | ✓ |
| Legacy `people/*` · `phase/*` | Both | M | MEDIUM | ✓ |
| `topic/` consolidation candidates | Periodic | M | INFO | ✓ |

`topic/` consolidation is corpus-scale (it compares topics across all files) — periodic only. Its matching is a deterministic algorithm (Jaccard on character 3-grams + same-stem grouping), so it is mechanical despite producing advisory output: the script *generates* candidates; a human *reviews* them.

### Structural integrity

| Check | Source | Mode | Pass | Severity | Today |
|---|---|---|---|---|---|
| Broken `[[wikilinks]]` | LINT | Periodic | M | MEDIUM | ✓ |
| Cross-project references are wikilinks + resolve | LINT | Periodic | M | MEDIUM | ✗ |
| Stub drift (`type/project-pointer` → missing project) | TT | Periodic | M | HIGH | ✓ |
| Project-hosted file has an `index.md` entry (SC index modifier) | SC | Periodic | M | MEDIUM | ✗ |
| No orphan `index.md` entries (each entry resolves to a file) | LINT | Periodic | M | MEDIUM | ✗ |
| Context-page coverage (`area/` with Knowledge but no Context) | SC | Periodic | M | WARNING | ✓ |
| Stale-suspects targets exist (`stale_suspects` paths resolve) | LINT | Periodic | M | WARNING | ✓ |
| Status coherence (frontmatter `status:` scalar matches `status/` tag) | LINT | Periodic | M | HIGH | ✓ |

Status coherence is a migration-era check — a contract-compliant new file carries only the `status/` tag, with no scalar to mismatch — so it is periodic only.

The broken-wikilink check covers `[[wikilinks]]` only — `![[embeds]]` are excluded. An embed is a distinct construct that may legitimately target a non-`.md` attachment (image, PDF) outside the link graph; resolving those is out of scope for this check.

**Broken-wikilink is MEDIUM, not HIGH.** A broken wikilink is vault entropy — a target was renamed, moved, or not yet created — not a violation of the knowledge-layer *envelope* (the contract HIGH checks govern frontmatter/tag/title structure). It is real and worth fixing, but it does not make a file structurally non-compliant, and HIGH-tiering it crowds the genuine envelope defects in the worklist. MEDIUM is the correct tier for link entropy.

### Freshness (SC)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Stale — `verified`/`updated` past the window | Periodic | M | WARNING | ✓ |
| Unverified — `updated` present, `verified` absent | Periodic | M | INFO `[suppressed]` | ◐ |

**`unverified` is suppressed** — `verified` is an optional field with no producer today; nothing in the vault sets it. Until a `verified`-writing step exists (a stewardship/review pass that stamps the date), `verified`-absent is the universal state and the check would fire on essentially every governed file — pure noise, not signal. The mechanical pass MUST NOT emit `unverified` findings until a `verified` producer exists; the row stays in the inventory so re-enabling it is a one-line change once that producer ships.

### Contradiction (LINT — the judgment pass)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Claims contradicted by `CLAUDE.md` Current State / other pages | Periodic | J | INFO | ✓ |
| Hub cross-reference (hub/subproject scopes only) | Periodic | J | INFO | ✓ |

The sole judgment-pass checks — best-effort, not contract-derived. Delta-scoped per the judgment-pass rule above.

### Filing-handoff (HC)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Filed file satisfies the full envelope (per the handoff's §) | Filing | — | HIGH | ✓ (`filing-validator`) |

Filing-time validation is the `filing-validator` critic-subagent — single-file and cheap, not part of the periodic mechanical/judgment split. Unaffected by this rework.

---

## Build status

The original build worklist's keystone items are done; this doc's rework adds the mechanical-pass split on top.

1. **Reconcile `/lint-knowledge` to derive structural checks from [[structural-contract]]'s Parsing Contract** — ✓ done. Lint derives structural rules, not just tag rules, at runtime.
2. **Build the filing-time critic** — ✓ done: the `filing-validator` agent.
3. **Mechanical pass — the `lint.py` script** — the deterministic checks, full-corpus, no model, deriving values from the contracts' Parsing Contracts. The script is a fresh implementation of the *entire* mechanical inventory above, so the previously-missing checks (✗ rows — scope-tag-matches-destination, single-H1, Wiki-`topic/`, `project-pointer` tags, cross-project link-integrity, `index.md` integrity, invariant-core presence across all governed types) are covered by construction. **This doc's deliverable.**
4. **Escalate the `[tightening]` checks** — `status/` from WARNING to HIGH; H1 and Wiki-`topic/` enter as HIGH. The first periodic run produces the [[structural-contract]] Migration Legacy worklists (`sources` backfill, H1 normalization, `status/`-tag migration) — expected output, not failure. Implemented in the script.
5. **Stand up the trigger chain** — a scheduler wakes the periodic run. Depends on the automation-gateway Pi build. The mechanical pass is cron-able with no model; only the judgment pass needs a Claude session — the trigger design should reflect that (see Cost, above).

---

## Cross-project-reference link-integrity

Routed here from the structural inventory — it produces no file, so it is not a filing-handoff contract. The rule:

- A reference from one project's Knowledge into another's is a `[[wikilink]]`, not a bare path or prose mention — wikilinks are vault-navigable and lint-checkable.
- The wikilink target must resolve to an existing file.
- Periodic check, MEDIUM severity, mechanical pass. Mechanically it is the broken-wikilink check scoped to links that cross a `project/` boundary; the added rule is that the cross-project reference must *be* a wikilink in the first place. The script detects path-shaped cross-project references (bare `Projects/Other/...` paths); freeform prose mentions with no path are out of mechanical scope.

---

## Downstream Consumers

| Artifact | Role | Status |
|---|---|---|
| `lint.py` | The mechanical pass — bundled with the `/lint-knowledge` skill in [dotty](https://github.com/lexijamesesq/dotty); derives check values from the contracts' Parsing Contracts | This doc's deliverable |
| `/lint-knowledge` | Orchestrates the periodic surface — runs `lint.py`, runs the delta-scoped judgment pass, merges the report | Pending — reconcile to this rework |
| `filing-validator` | Implements the **filing-time** surface | Built |
| Scheduler / trigger chain | Wakes the periodic run; mechanical pass is cron-able, judgment pass needs a model session | Depends on the Pi build |

`references.lint_surface` resolves this doc by key in global CLAUDE.md, alongside `references.structural_contract` and `references.handoff_contracts`.
