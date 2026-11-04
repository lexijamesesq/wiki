---
status: active
description: >-
  Wiki stewardship rules — how Wiki maintains itself, mutation discipline,
  writing knowledge, context management.
updated: 'TODO: date'
---
# Wiki

Claude-optimized knowledge layer — query-time system with a thin durable context layer.

This sidecar governs **how Wiki maintains itself as infrastructure** — never the topics or content inside it. Domain knowledge, per-domain working state, and topic data live in the relevant `Contexts/` page (or `Data/`), never here. TODO: link your own architecture doc for space structure, linking mechanisms, hub disposition, and rejected alternatives.

TODO: set `workspace_root` (this vault's root path) in your global Claude Code config, not here — every `{workspace_root}` placeholder throughout this repo's specs and skills resolves against it, to find your vault's `{workspace_root}/Wiki/Knowledge/`, `{workspace_root}/Wiki/Data/`, etc. This repo's own checkout can live anywhere on disk; it doesn't need to sit inside your vault.

---

## Objective

Keep Wiki maintained, fresh, queryable, and trustworthy so every Claude session loads accurate context via domain context files, file descriptions, full-text search and `related` links — without re-deriving prior work.

---

## Design Philosophy

**Query-time, not write-time.** Knowledge/ stores faithful captures at ingest. Synthesis happens when a session loads the relevant files into context — not ahead of time in compiled pages. A compiled wiki layer drifts silently from its sources because no one re-checks the compilation when a source changes. Drift in a wiki reads like authority; drift in raw sources reads like data. This system keeps the data and lets the model synthesize fresh.

**Per-file update modes as mutation discipline.** Every edit to existing substance is a potential corruption vector, so each knowledge file declares how its body may change in its `update` field (`spec/knowledge-files.md`): `append` files take new information alongside old and never lose existing text; `replace` files are rewritten in place to stay current, with no deprecated banners or strikethrough; `never` files do not change, and a successor is a new file. Consolidation (merging, pruning, restructuring) is destructive — it requires human judgment because only a human can decide what's redundant versus what captures a distinct perspective. A file's `## Sources` section is what lets you trace back to ground truth when something feels wrong.

**Prune failure-archaeology; keep clean working data.** Append-bias preserves genuine *knowledge* — distinct, source-attributed captures. It is NOT a mandate to hoard the record of how the work went: postmortems, retros, superseded models, completed-work changelogs, and "ways it failed" logs read as signal but pollute the context every future session loads. Keep what works; prune the archaeology. The test is not "is it true or historical?" — it is "does loading this help the next session or pollute it?"

**Two audiences, two surfaces.** A Claude-facing surface (Knowledge/Contexts) serves dense, described, wikilinked context-window loading. A human-facing surface (TODO: name your own — e.g. Personal/Work) serves structured browsing and quick reference. Claude stewards accuracy on the human surfaces but never restructures them, because the structure serves the user's cognitive model, not Claude's optimization targets.

---

## Desired Outcomes

- Sessions find what they need from context pages, file descriptions (the describe tool) and `related` links — no hand-curated indexes
- Knowledge/ files stay single-question scoped (one question per file) with source attribution
- Context files carry Claude's durable working understanding — updated when understanding shifts, not on every session
- Stale content is flagged, not silently drifted (hygiene at closeout; the librarian agent once live)
- Human-facing pages stay accurate via periodic stewardship

---

## Health Metrics (must not degrade)

- No broken wikilinks inside Wiki/
- No Knowledge/ file without the four contract fields (`description`, `update`, `related`, `updated`)
- No Knowledge/ file without a `## Sources` section (provenance required)
- No Knowledge/ file over TODO: your size threshold without human-approved consolidation review
- No Context file that contradicts current Knowledge/ state
- Every domain with Knowledge/ files should have a corresponding Context file
- Human-facing page facts don't silently drift from Wiki state

---

## Decision Authority

**Autonomous:**

- Writing and refreshing frontmatter per `spec/knowledge-files.md`, including descriptions
- Appending new content to `update: append` Knowledge/ files
- Rewriting `update: replace` files in place to keep them current, when the session holds the context
- Creating new Knowledge/ files for new topics
- Updating Context files when understanding shifted
- Running the contract lint on request or at session closeout
- Patching stale facts on human-facing pages (stewardship)
- TODO: name your automated lanes (if any) and their exact write scope — be explicit about what they may NEVER touch

**Human-initiated:**

- Triggering a stewardship session (contract lint, human-facing page check)
- Removing content (deletion) — user confirms target
- Expanding structured-data domains

**Human-approved:**

- Consolidating Knowledge/ files (merging overlapping content, pruning outdated substance)
- Editing existing text in an `append` file, or any body change to a `never` file (the answer is usually a successor file)
- Changing a file's `update` mode
- Adding a type folder to a project's `Knowledge/`
- Restructuring human-facing pages

---

## Stop Rules

- Halt before deleting any file without explicit user confirmation — deletion has no reliable recovery
- Halt before editing existing text in an `append` file or the body of a `never` file — the file's `update` field forbids it, and mutation is the primary corruption vector. Flag the edit for approval instead.
- Halt before consolidating Knowledge/ files without user confirmation — consolidation is a judgment call on redundancy
- Halt when content doesn't meet the coherence criteria (Writing knowledge, below) — name it to the user rather than filing it
- Halt before restructuring any human-facing page — these are human-navigable surfaces designed for the user's cognitive model

---

## Human-Facing Page Stewardship

TODO: describe your own human/Claude surface split, if you use one. The pattern this repo ships with:

**Claude's stewardship role:** patch facts that have drifted from Wiki state. **What stewardship is not:** reorganizing sections, adding new sections, changing writing style, merging pages, splitting pages, or rewriting for "clarity." These are structural decisions that belong to the page owner.

| Stewardship does | Stewardship doesn't |
| --- | --- |
| Patch stale facts to match Wiki state | Reorganize page structure |
| Flag uncertain corrections for user review | Silently rewrite ambiguous content |
| Add missing data points the session surfaced | Add new sections or categories |
| Remove data confirmed obsolete by the user | Remove content based on Claude's judgment |

**Trigger:** TODO: your trigger condition (e.g., session-closeout when a domain's Knowledge/ files changed).

---

## Self-Management

### Management triggers

| Task | Trigger | Who runs |
| --- | --- | --- |
| Contract lint (`/lint-knowledge`) | TODO: your trigger | Automatic |
| Context update | TODO: your trigger | Automatic |
| Human-facing page stewardship | TODO: your trigger | Automatic |
| Knowledge/ mutation review | Closeout hygiene flags a file over threshold | Flagged for user review |
| Structured-data expansion | Session-initiated | User decides when a domain fits |

---

## Knowledge Sources & Prioritization

When Claude needs information about Wiki's rules, structure, or state:

1. **TODO: your architecture doc** — space structure, linking mechanisms, hub disposition, rejected alternatives
2. **`spec/knowledge-files.md`** — the file contract: four frontmatter fields, update modes, type folders
3. **This `.claude/instance.md`** — stewardship rules, management triggers, decision authority
4. **TODO: your migration/onboarding doc**, if you have one
5. **Wiki's own content** — query via full-text search, descriptions and `related` links

### Writing posture

Agent-optimized. Terse, dense, tables over paragraphs. Wikilinks between pages. Frontmatter as structured metadata.

### Authority hierarchy (for loading domain knowledge)

1. **Context page** (`Contexts/{domain}-context.md`) — canonical working understanding. Check first. When a context page and a Knowledge/ file conflict, the context page wins and the Knowledge/ file is flagged stale.
2. **Knowledge/ files** — source material and research captures. Faithful to their moment of creation. May contain claims superseded by later work in the same domain.
3. **Human-facing pages** — summaries. Patched for accuracy periodically but may lag between sessions.

An automated agent building summaries, populating hubs, or answering domain questions loads the context page first and treats it as the authoritative lens.

**When drift is detected:** name it to the user in the session; the resolution (edit, append, or archive the Knowledge/ file) is a decision with them.

### Freshness signals

`updated` is the date of the last content change — not a frontmatter-only edit. File mtimes are unreliable under sync, so this field is the record.

- Default freshness window: TODO: your window (e.g. 90 days) from `updated`, overridable per domain context page.

### Reading posture

At point-of-use: check the domain's context page first (authority hierarchy). For individual Knowledge/ files, check `updated` against the freshness window. Validate against current state before relying on content past its window.

---

## Key Files

| File | Purpose |
| --- | --- |
| `.claude/instance.md` | This file — Wiki stewardship rules |
| `Knowledge/` | Narrative knowledge, one topic per file |
| `Data/` | Structured per-item records |
| `Contexts/` | Claude's durable working understanding + domain schema |
| `Attachments/` | Binaries |
| `spec/` | The canonical contract — `knowledge-files.md` (frontmatter fields, update modes, type folders), checked by `contract_lint.py` in the `knowledge-description` skill. |

---

## Writing knowledge

A session writes a knowledge file directly when it has durable content with a known home: `Knowledge/{area}-{slug}.md` (or a project's type folder), the four contract fields, and a `## Sources` section. **A data correction** (a recorded fact changed) is applied only when the user stated the change ("switched to X", "the value is now Z"); when it is only inferred, ask first. Then scope it before editing: state the old and new value, find every layer that holds the old value (Data/ → Knowledge/ → Context → human-facing page; often only one or two do), and apply it through each:

- Data/ → update the record's frontmatter.
- Knowledge/ → read the file's `update` field: `append` takes a dated entry with existing text unchanged; `replace` or `never` halts for the user's approval (Stop rules).
- Context page → through the `context-page` skill, if the working understanding shifted.
- Human-facing page → a targeted fact patch under the stewardship rules.

Report which layers changed.

**Coherence criteria:**

- **Self-contained:** a future reader loading the file standalone can understand it
- **Clear subject:** its description can name one specific subject without forcing
- **Additive:** contributes content Wiki doesn't already cover (not a duplicate of an existing Knowledge/ file)
- **Single-question scoped:** the file should answer one identifiable question

If any criterion fails, the content is not filed; name it to the user instead.

---

## Variation from Project pattern

TODO: describe how this space differs from your project-CLAUDE.md convention, if you have one (e.g., its own intake skill, no project-creation flow governing it).

---

## Pending Work

TODO: genuinely-pending infrastructure work only. Completed work is not logged here — it lives in the artifacts themselves. Domain/topic state lives in the relevant Contexts/ page or Data/, and active tasks live in your task tracker — never here.
