---
tags:
  - type/claude-wiki
status: active
description: >-
  Wiki stewardship rules — how Wiki maintains itself, mutation discipline,
  intake pipeline, context management.
updated: 'TODO: date'
---
# Wiki

Claude-optimized knowledge layer — query-time system with a thin durable context layer.

This sidecar governs **how Wiki maintains itself as infrastructure** — never the topics or content inside it. Domain knowledge, per-domain working state, and topic data live in the relevant `Contexts/` page (or `Data/`), never here. TODO: link your own architecture doc for space structure, linking mechanisms, hub disposition, and rejected alternatives.

TODO: set `workspace_root` (this vault's root path) in your global Claude Code config, not here — every `{workspace_root}` placeholder throughout this repo's specs and skills resolves against it, and this repo itself must be cloned in as `Wiki/` at that root for those placeholders to resolve correctly.

---

## Objective

Keep Wiki maintained, fresh, queryable, and trustworthy so every Claude session loads accurate context via topic-scoped tag queries + domain context files — without re-deriving prior work.

---

## Design Philosophy

**Query-time, not write-time.** Knowledge/ stores faithful captures at ingest. Synthesis happens when a session loads topic-scoped files into context — not ahead of time in compiled pages. A compiled wiki layer drifts silently from its sources because no one re-checks the compilation when a source changes. Drift in a wiki reads like authority; drift in raw sources reads like data. This system keeps the data and lets the model synthesize fresh.

**Append-bias as mutation discipline.** Every edit to existing substance is a potential corruption vector. New information appends alongside old, preserving the record. Consolidation (merging, pruning, restructuring) is destructive — it requires human judgment because only a human can decide what's redundant versus what captures a distinct perspective. Sources in frontmatter are what let you trace back to ground truth when something feels wrong.

**Prune failure-archaeology; keep clean working data.** Append-bias preserves genuine *knowledge* — distinct, source-attributed captures. It is NOT a mandate to hoard the record of how the work went: postmortems, retros, superseded models, completed-work changelogs, and "ways it failed" logs read as signal but pollute the context every future session loads. Keep what works; prune the archaeology. The test is not "is it true or historical?" — it is "does loading this help the next session or pollute it?"

**Two audiences, two surfaces.** A Claude-facing surface (Knowledge/Contexts) serves dense, tagged, wikilinked context-window loading. A human-facing surface (TODO: name your own — e.g. Personal/Work) serves structured browsing and quick reference. Claude stewards accuracy on the human surfaces but never restructures them, because the structure serves the user's cognitive model, not Claude's optimization targets.

---

## Desired Outcomes

- Session-start context loading finds what it needs via tag queries — no hand-curated indexes
- Captures graduate through a deliberate intake pipeline: TODO: name your router/intake skill
- Knowledge/ files stay topic-scoped (one question per file) with source attribution
- Context files carry Claude's durable working understanding — updated when understanding shifts, not on every session
- Stale content is flagged by lint, not silently drifted
- Human-facing pages stay accurate via periodic stewardship

---

## Health Metrics (must not degrade)

- No broken wikilinks inside Wiki/
- No Knowledge/ file without an accepted type tag + scope tags
- No Knowledge/ file without source-attribution frontmatter (provenance required)
- No Knowledge/ file over TODO: your size threshold without human-approved consolidation review
- No Context file that contradicts current Knowledge/ state
- Every domain with Knowledge/ files should have a corresponding Context file
- Human-facing page facts don't silently drift from Wiki state

---

## Decision Authority

**Autonomous:**
- Applying frontmatter per the tag taxonomy
- Appending new content to existing Knowledge/ files (append-bias)
- Creating new Knowledge/ files for new topics
- Updating Context files when understanding shifted
- Running the lint/health-check skill on request or at session-closeout signal
- Filing router-delivered captures via the intake skill (skill owns the coherence decision)
- Creating queue items for judgments the system can't or won't decide autonomously
- Patching stale facts on human-facing pages (stewardship)
- TODO: name your automated lanes (if any) and their exact write scope — be explicit about what they may NEVER touch

**Human-initiated:**
- Triggering a stewardship session (lint sweep + queue triage)
- Promoting a queue item to Knowledge/
- Removing content (deletion) — user confirms target
- Expanding structured-data domains

**Human-approved:**
- Consolidating Knowledge/ files (merging overlapping content, pruning outdated substance)
- Editing existing substance in Knowledge/ files (vs. appending new content)
- Marking Knowledge content superseded
- New taxonomy values added
- Restructuring human-facing pages

---

## Stop Rules

- Halt before deleting any file without explicit user confirmation — deletion has no reliable recovery
- Halt before editing existing substance in a Knowledge/ file — mutation is the primary corruption vector; appending preserves the record. Flag the edit for approval instead.
- Halt before consolidating Knowledge/ files without user confirmation — consolidation is a judgment call on redundancy
- Halt when intake can't classify a capture cleanly — an honest queue item beats a wrong placement
- Halt when a taxonomy decision isn't resolvable by existing tag values — ad-hoc tags fragment the namespace
- Halt before restructuring any human-facing page — these are human-navigable surfaces designed for the user's cognitive model

---

## Human-Facing Page Stewardship

TODO: describe your own human/Claude surface split, if you use one. The pattern this repo ships with:

**Claude's stewardship role:** patch facts that have drifted from Wiki state. **What stewardship is not:** reorganizing sections, adding new sections, changing writing style, merging pages, splitting pages, or rewriting for "clarity." These are structural decisions that belong to the page owner.

| Stewardship does | Stewardship doesn't |
|---|---|
| Patch stale facts to match Wiki state | Reorganize page structure |
| Flag uncertain corrections for user review | Silently rewrite ambiguous content |
| Add missing data points the session surfaced | Add new sections or categories |
| Remove data confirmed obsolete by the user | Remove content based on Claude's judgment |

**Trigger:** TODO: your trigger condition (e.g., session-closeout when a domain's Knowledge/ files changed).

---

## Self-Management

### Operator-judgment queue (`Queue/`)

One file per pending judgment — the single operator-attention surface for everything the system can't or won't decide autonomously. **Not task management**: queue items are pending judgments about routing, integrity, or staging — never work items.

Item kinds — TODO: define your own taxonomy. This repo's convention (kept minimal, expand only when reality demands it):

| queue-kind | Meaning |
|---|---|
| `disposition` | Here is a finding/item; operator decides what happens to it |
| `proposal` | Here is a specific proposed change; operator approves or rejects it |

**Item shape:** filename `{YYYY-MM-DD}-{queue-kind}-{slug}.md`; frontmatter `queue-kind`, `source`, `reasons` (array), `created`, `status: pending | resolved | expired`, scope-hint tags; body carries the payload + search evidence.

**Triage:** pull-only — session boundaries are not task surfaces. TODO: name your triage verb/skill and its passive signal (e.g. a statusline count).

### Management triggers

| Task | Trigger | Who runs |
|---|---|---|
| Lint (taxonomy check, orphan scan, size/source flags) | TODO: your trigger | Automatic |
| Context update | TODO: your trigger | Automatic |
| Human-facing page stewardship | TODO: your trigger | Automatic |
| Knowledge/ mutation review | Lint flags a file over threshold | Flagged for user review |
| Queue triage | Operator-invoked only | User decides when |
| Structured-data expansion | Session-initiated | User decides when a domain fits |

---

## Knowledge Sources & Prioritization

When Claude needs information about Wiki's rules, structure, or state:

1. **TODO: your architecture doc** — space structure, linking mechanisms, hub disposition, rejected alternatives
2. **`spec/knowledge-contract.md` Part I** — closed tag namespaces, thresholds, depth limits, parsing contract
3. **This `CLAUDE.md`** — stewardship rules, management triggers, decision authority
4. **TODO: your migration/onboarding doc**, if you have one
5. **Wiki's own content** — query via content/tag search

### Writing posture

Agent-optimized. Terse, dense, tables over paragraphs. Wikilinks between pages. Frontmatter as structured metadata.

### Authority hierarchy (for loading domain knowledge)

1. **Context page** (`Contexts/{domain}-context.md`) — canonical working understanding. Check first. When a context page and a Knowledge/ file conflict, the context page wins and the Knowledge/ file is flagged stale.
2. **Knowledge/ files** — source material and research captures. Faithful to their moment of creation. May contain claims superseded by later work in the same domain.
3. **Human-facing pages** — summaries. Patched for accuracy periodically but may lag between sessions.

An automated agent building summaries, populating hubs, or answering domain questions loads the context page first and treats it as the authoritative lens.

**When drift is detected:** Add the file to `stale_suspects` in the domain's context page (frontmatter array of file paths). This is autonomous — flagging is not mutation. Resolution happens with a human (edit, append, or archive the Knowledge/ file).

### Freshness signals

Two frontmatter dates, different meanings:

| Field | Meaning | Set when |
|-------|---------|----------|
| `updated` | File last touched | Any edit, including mechanical ops (retagging, migration, frontmatter fixes) |
| `verified` | Content last reviewed for accuracy | Human or agent confirmed claims are current |

- Lint checks freshness against `verified` when present, `updated` when absent.
- Default freshness window: TODO: your window (e.g. 90 days) from `verified` (or `updated` as fallback), overridable per domain context page.

### Reading posture

At point-of-use: check the domain's context page first (authority hierarchy). For individual Knowledge/ files, check `verified` (or `updated` fallback) against the freshness window. Validate against current state before relying on content past its window.

---

## Key Files

| File | Purpose |
|---|---|
| `CLAUDE.md` | This file — Wiki stewardship rules |
| `Queue/` | Operator-judgment queue — one item file per pending judgment |
| `Knowledge/` | Narrative knowledge, one topic per file |
| `Data/` | Structured per-item records |
| `Contexts/` | Claude's durable working understanding + domain schema |
| `Attachments/` | Binaries |
| `spec/` | The canonical contract — `knowledge-contract.md` (Part I tags, Part II envelope, Part III filing handoffs, Part IV lint surface, Part V parsing contract) — governed, lint-parsed. TODO: your instance-data roster (real names/employers, if your taxonomy has a `person/`-style namespace) belongs in a gitignored sibling file, never here. |

---

## Intake

TODO: name your single entry point for Wiki-axis content. The Router delivers here; this skill owns area classification, coherence gating, and internal dispatch.

### Default path

- **Coherent + additive** → `Knowledge/{area}-{slug}.md` with type + area + topic + status + `updated` + `sources` tags
- **Data correction** → propagate through affected layers (Data/ → Knowledge/ → Context → human-facing page)
- **Explore-later topic** → `Queue/` item, `queue-kind: disposition`
- **Half-thought / incoherent** → `Queue/` item, `queue-kind: disposition`

**Coherence criteria:**
- **Self-contained:** a future reader loading the file standalone can understand it
- **Clear topic:** can be tagged with a non-trivial topic tag without forcing
- **Additive:** contributes content Wiki doesn't already cover (not a duplicate of an existing Knowledge/ file)
- **Single-question scoped:** the file should answer one identifiable question

If any criterion fails → a `Queue/` item, not Knowledge/.

### Specialized handlers

TODO: list your own specialized intake handlers (e.g., a recurring-meeting capture skill), if any. Handlers are overrides, not peers — the default intake skill is always the fallback.

### Scope boundary

TODO: describe where task-axis captures (work items with no project owner) route in your system — Queue/ items are pending judgments (routing, integrity, staging), never work items.

---

## Variation from Project pattern

TODO: describe how this space differs from your project-CLAUDE.md convention, if you have one (e.g., a distinct `type/claude-wiki` tag, its own intake skill, no project-creation flow governing it).

---

## Pending Work

TODO: genuinely-pending infrastructure work only. Completed work is not logged here — it lives in the artifacts themselves. Domain/topic state lives in the relevant Contexts/ page or Data/, and active tasks live in your task tracker — never here.
