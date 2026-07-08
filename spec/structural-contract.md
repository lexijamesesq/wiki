---
tags:
  - type/spec
  - project/system
  - status/active
updated: '2026-07-07'
---
# Structural Contract

Canonical specification for the **structural dimension** of vault knowledge-layer files — required frontmatter fields, tag validity, discoverability, and the single title.

Sibling of [[tag-taxonomy]]. That doc governs *which tags are valid* (the tag dimension); this doc governs *what envelope a file must have* (the structural dimension). A file is well-formed only when it satisfies both.

Like [[tag-taxonomy]], this is the single source of truth: consumers reference it, never restate its rules. It carries a Downstream Consumers table and a Parsing Contract so `/lint-knowledge` extracts its rules mechanically at runtime.

**Authority:** derived from `target-architecture-v2.md` and [[tag-taxonomy]] (architectural authorities) plus the verifier-side metrics in `/lint-knowledge` and `Wiki/CLAUDE.md`. Rules stricter than lint's current behavior are marked **[tightening]** — escalate severity during the reconciliation pass, do not silently adopt.

**Scope — the envelope, not the content.** This doc governs only the *envelope*: mechanically-verifiable static structure. It does NOT govern *content architecture* — how a body is organized, how a file mutates, when it goes stale. Those vary within every `type/` and are out of scope (see Body & Content Architecture). Every rule here is checkable by lint without judgment.

---

## Principle

Two orthogonal dimensions describe a well-formed file:

- **Tag dimension** — which tags from the closed namespaces the file carries. Governed by [[tag-taxonomy]].
- **Structural dimension (the envelope)** — required frontmatter fields, tag validity, discoverability, single title. Governed by this doc.

Content architecture — body organization, mutation behavior, freshness semantics — is a third concern, governed by neither. Lint verifies the first two mechanically.

---

## Invariant Core

Every knowledge-layer file MUST have:

| Element | Requirement |
|---|---|
| `type/` tag | Exactly one, from the closed `type/` vocabulary ([[tag-taxonomy]]) |
| Scope tag | At least one `project/<name>` OR `area/<hierarchy>` |
| `status/` tag | Exactly one, from the closed `status/` vocabulary **[tightening — lint currently WARNING]** |
| `updated` | `updated: YYYY-MM-DD` frontmatter |
| Title | Exactly one level-1 heading (`# Title`) **[tightening — lint has no H1 check today]** |
| Tag validity | All tags conform to [[tag-taxonomy]] — namespaces, closed vocabularies, depth limits |

Type-agnostic and destination-agnostic. Everything below adds to it.

---

## Per-Type Additions

| `type/` | Also requires | `sources` |
|---|---|---|
| `type/knowledge` | `topic/` — Wiki-hosted only (see Destination Modifiers) | Required |
| `type/context` | — | Optional (Claude synthesis, not captured substance) |
| `type/reference` | — | Optional |
| `type/spec` | — | Optional |
| `type/agent-spec` | — | Optional |
| `type/project-pointer` | `project/`, `topic/` | n/a |
| `type/log` | — | n/a |
| `type/eval` | — | Optional |

**D4 resolution:** `type/spec` and `type/reference` require the invariant core only; `sources` optional (authored, not captured/researched). `type/data` is **out of scope** entirely — domain content with typed domain frontmatter, not a knowledge-layer file (see Scope Boundaries › Type Gate); it carries no structural-contract requirements.

---

## Destination Modifiers

The same `type/` carries slightly different requirements by where it lives.

| Aspect | Wiki-hosted (`{workspace_root}/Wiki/Knowledge`, `Data`, `Contexts`) | Project-hosted (`Projects/<name>/Knowledge`, `System/`) |
|---|---|---|
| Scope tag | `area/<hierarchy>`; exception: `type/project-pointer` carries `project/` (Per-Type row) | `project/<name>` |
| `topic/` on `type/knowledge` | Required, ≥1 **[tightening]** | Optional |
| Index participation | None — `area/` + `topic/` tags ARE the index | An `index.md` entry for the file exists |

**D5 resolution:** index files are a project-Knowledge mechanism; Wiki uses tags-as-index. Each destination class has exactly one discovery mechanism.

**Scope-tag exception (pre-existing tension, now explicit):** `type/project-pointer` is Wiki-hosted (`{workspace_root}/Wiki/Contexts/project-{name}.md`) yet points at a project — its Per-Type Additions row requires `project/`, and that row is authoritative: a Wiki-hosted project pointer satisfies the scope check with `project/`, not `area/`. Every other Wiki-hosted type takes `area/`.

**Index syncing is a process obligation, not a structural property.** The contract rule is only that an `index.md` entry *exists* (lint-checkable, file-at-rest). Keeping the index synced on every create / delete / rename is the responsibility of the filing skills (`/session-closeout`, intake skills) — outside this contract.

---

## Provenance

`sources` frontmatter — an array naming where the file's substance came from: a URL, `user-stated`, `AI research YYYY-MM-DD`, `inbox-capture`, `routine/<action> <run-id>` **[new]**, or `pre-contract` (for legacy files predating this doc — see Migration Legacy). `routine/<action> <run-id>` is automated-lane attribution: it names the unattended routine and the specific run that produced the substance, so every automated write is traceable to its run report. It is the universal, machine-checkable provenance record. Requirement per type: see Per-Type Additions.

A verbatim-preservation body section (`## Original Capture`) is **not** part of this contract. Under this contract it is scoped to *progressive-enhancement document types* — files where structured synthesis accretes on an immutable raw input (Incubator idea/initiative cards, governed by `incubator-reference.md`).

That is the target, not a description of the present. `intake-defaults.md` and `router-spec.md` currently mandate a `## Original Capture` section for **all** Knowledge deliveries vault-wide; those mandates are **superseded** by D1 (see Downstream Consumers). Reconciliation must actively de-scope them — it cannot assume the section is already Incubator-only.

**D1 resolution:** provenance is `sources` frontmatter — universal and mechanically checkable. The verbatim-section mechanism is delegated out of this contract to the progressive-enhancement document types that own it.

---

## Freshness

Two date fields, distinct meanings:

| Field | Meaning | Requirement |
|---|---|---|
| `updated` | File last touched — any edit, including mechanical ops (retag, migration, frontmatter fix) | Required |
| `verified` | Content last reviewed for accuracy — a human or agent confirmed claims are current | Optional |

Both are dates (`YYYY-MM-DD`). Freshness checks use `verified` when present, `updated` when absent.

**D2 resolution:** `verified` is a date, not a flag. Optional; the event that sets it is defined by the lint/stewardship surface, not this contract.

---

## Body & Content Architecture

The contract's only body rule is the Invariant Core's single H1.

Everything else about a file's body — its internal organization, how it mutates (overwrite / append / supersede), whether and how it goes stale — is **content architecture**, and is explicitly **out of scope**. Content architecture varies *within* every `type/`: one `type/knowledge` file may be a decision chain, another a current-state snapshot, another an event series, and a single file may mix these per section. None of it is mechanically checkable; none of it is governed here.

- Mutation discipline (the overwrite / append / supersede decision, keyed to content architecture) is a separate concern — see `target-architecture-v2.md` "Knowledge mutation discipline" and its planned extension.
- Body-size and source-count heuristics (lint's `>150`-line and `>6`-source INFO flags) are lint's own QA heuristics, not contract rules. Lint may run checks beyond this contract; only the rules in the Parsing Contract are *contract* rules.

---

## Scope Boundaries

This contract governs **genuine knowledge-layer documents only** — maintained synthesis: methodology, specs, references, durable Claude working understanding, and Wiki Knowledge narrative. It does **not** govern domain content, operational records, archives, or raw captures. Those have their own conventions (or none); the knowledge-layer envelope must not be applied to them.

The boundary is **mechanically determinable** — lint decides governed vs. ungoverned for every file from two signals, location and `type/` tag, with no judgment. A file is **in governed scope only if it passes the Location Gate AND carries a governed `type/`** (or, in a governed location, carries no `type/` at all — that is a genuine missing-classification defect). Everything else is out of scope and produces no findings.

### Location Gate

A file is in a **governed location** only if its vault path matches one of:

| Governed location | What lives there |
|---|---|
| `System/*.md` and `System/Knowledge/**` | Vault knowledge-layer reference/spec/methodology docs |
| `System/Context/**` | System-project Claude working-context docs |
| `Projects/<name>/Knowledge/**` | Per-project knowledge-layer docs |
| `Projects/<name>/Context/**` | Per-project Claude working-context docs |
| `Wiki/Knowledge/**` | Wiki maintained narrative knowledge |
| `Wiki/Contexts/**` | Wiki domain context docs |

Every other location is **ungoverned** and lint skips it entirely — no envelope checks, no tag-validity checks, no `no-type-tag` finding. This explicitly excludes:

- **Domain content** — `Wiki/Data/**` (gear, products, technology, recipes), and any per-project domain-content folder. Data records carry typed domain frontmatter by nature; the knowledge-layer envelope (`status/` from the closed set, single H1, `sources`) does not apply.
- **Operational records** — `Projects/Recruiting/Roles/**`, `Projects/Recruiting/Playbooks/**`, `Projects/Recruiting/Candidates/**`, candidate/role/interview files generally. These follow recruiting-domain conventions, not the knowledge-layer envelope.
- **Archives** — any file named `*-archive.md` or under an `Archived/` / `archive/` path segment. Frozen history; not maintained, not re-linted.
- **Raw captures and operational scratch** — `Projects/<name>/` non-`Knowledge`/`Context` working folders (e.g. `Research/`, `Activity/`, `Ideas/`, `Eval/`, `NPS/`, `Usage/`, meeting-notes folders). Raw inputs and operational records, not synthesis.
- **Incubator idea/initiative cards** — self-governed by `incubator-reference.md` (distinct scalar `type:` + `stage:` schema; not a closed-vocabulary `type/` tag).

A file in an ungoverned location is out of scope **even if it carries a `type/` tag** — location is the outer gate. Conversely, a file in a governed location with no `type/` tag is a genuine missing-classification defect and is flagged.

### Type Gate — governed vs. ungoverned `type/`

Within a governed location, the file's `type/` tag determines its tier. Governed `type/` values are those in the Invariant Core / Per-Type model. Two `type/` values name content that is out of scope wherever it sits — `type/data` (domain content) and `type/meeting-capture` (raw recurring-meeting capture); a file carrying either is ungoverned regardless of location.

**Outside the `type/` model entirely:**

- **Content architecture** — body organization, mutation, freshness semantics (see Body & Content Architecture above). A separate concern, not a `type/`.

**Exemption tiers** — a governed file's `type/` places it in exactly one tier. Lint derives the tier from this table:

| Tier | Lint treatment | `type/` values |
|---|---|---|
| **Fully governed** | Invariant Core + the file's Per-Type Additions row | every `type/` in the Per-Type Additions table |
| **Invariant-core-only** | Invariant Core enforced; Per-Type Additions skipped | `type/recipe`, `type/workout`, `type/dashboard`, `type/hub` — and, by default, any other closed-vocabulary `type/` value in neither the Per-Type Additions table nor the Structure-not-imposed tier |
| **Structure-not-imposed** | No structural-contract check applies; only [[tag-taxonomy]] tag validity | `type/claude-project`, `type/claude-hub`, `type/claude-wiki`, `type/claude-space`, `type/claude-system`, `type/summary`, `type/scratchpad`, `type/working-notes`, `type/working-doc`, `type/exploration`, `type/playbook` |
| **Out of scope** | No check at all — file is ungoverned | `type/data`, `type/meeting-capture` (domain content / raw capture — see Location Gate) |

- **Invariant-core-only** types are content shapes and dashboard/hub pages. They carry the full envelope (`type/`, scope tag, `status/`, `updated`, single H1, valid tags) but no per-type additions; body and any further structure are the owning mechanism's call.
- **Structure-not-imposed** types are CLAUDE.md / hub / space sidecars (governed by the project / hub templates), human-surface pages (`type/summary`, `type/scratchpad`), ephemeral Claude scratch (`type/working-notes`, `type/working-doc`), in-progress authored drafts (`type/exploration`), and process playbooks (`type/playbook` — operational, human-owned structure). The structural contract does not impose an envelope on them; lint verifies only that any tags they carry are valid per [[tag-taxonomy]].
- **Out of scope** types (`type/data`, `type/meeting-capture`) get no lint check at all — they are domain content / raw capture, surfaced here so the Type Gate is complete.

A `type/` listed in the Per-Type Additions table is **fully governed** — Invariant Core + its per-type row.

---

## Migration Legacy

The contract describes the target. The existing corpus predates it and is substantially non-compliant. Reconciliation is a backfill pass, surfaced as a worklist by `/lint-knowledge` — not a silent assumption that the corpus already conforms.

- **`sources` backfill** — most existing `type/knowledge` files carry no `sources` field. Backfill: the real origin where recoverable; `sources: [pre-contract]` where the origin is unrecoverable. Lint surfaces the non-compliant set.
- **Single-H1 normalization** — some legacy files have no H1, or open with a body tag or a `##` heading. A normalization pass adds the H1.
- **`status/` tag migration** — legacy files use a scalar `status:` field; D3 makes `status/` a tag. Migration retags; the scalar is dropped once the tag is present.

These are tracked reconciliation work, not blockers to adopting the contract.

---

## Downstream Consumers

| Artifact | Consumes / Conflict | Status |
|---|---|---|
| [[tag-taxonomy]] | Sibling authority — the tag dimension | Sibling |
| `target-architecture-v2.md` | Upstream authority — space model, freshness design | Source |
| `intake-defaults.md` | Frontmatter schema, body shape — shrinks to router-intake rules on this base; its `## Original Capture` mandate is superseded (D1) | Pending |
| `router-spec.md` | Its "Knowledge Delivery Rules" clause declaring `## Original Capture` "non-negotiable" **directly contradicts D1** — must be removed, not layered | Pending — conflict |
| `Wiki/CLAUDE.md` | Two items to reconcile, both content-architecture not structural rules: the "no Knowledge/ file over 150 lines" health metric (line count is a lint INFO heuristic), and the "single-question scoped" coherence criterion (body shape is content architecture) | Pending — conflict |
| `/wiki-intake` | Applies the contract when filing Wiki Knowledge | Pending |
| `/lint-knowledge` | Verifies the contract; extracts rules at runtime via the Parsing Contract | Pending |
| `/session-closeout` | Query-and-file applies the contract; index sync | Pending |
| Project CLAUDE.md `### Knowledge` declarations | Extend the per-type schema for their layer | Pending |

A `references.structural_contract` config key should be added to global CLAUDE.md so skills resolve this doc by key, as they do `references.tag_taxonomy`.

---

## Parsing Contract

`/lint-knowledge` extracts structural rules from this doc at runtime — never hardcodes them. Every rule below is mechanically checkable. No rule appears elsewhere in this doc without a row here; if it can't be parsed, it isn't a contract rule.

| What to extract | Where | How to parse |
|---|---|---|
| Invariant-core frontmatter elements | "Invariant Core" table — `type/`, Scope tag, `status/`, `updated` rows | Each row = one frontmatter presence/cardinality check; col 1 = element, col 2 = rule |
| Invariant-core tag validity | "Invariant Core" table — "Tag validity" row | Delegates: run every tag through [[tag-taxonomy]]'s own parsing contract |
| Invariant-core body element | "Invariant Core" table — "Title" row | Body check: exactly one level-1 (`#`) heading |
| Per-type required additions | "Per-Type Additions" table | Row keyed by `type/` value (col 1); col 2 = required additional tags (`—` = none; a destination-conditional tag such as `topic/` is governed by Destination Modifiers, which is authoritative for the condition), col 3 = `sources` requirement |
| `sources` requirement per type | "Per-Type Additions" table, `sources` column | Values: Required / Optional / n/a |
| Destination modifiers | "Destination Modifiers" table | Rows = aspects; cols = Wiki-hosted vs project-hosted; each cell is a static file-at-rest check (scope tag value, `topic/` presence, `index.md` entry existence) — except the Wiki-hosted "Index participation" cell, which yields no check: Wiki discovery is tag-based and is verified by the tag-validity rule. The Wiki-hosted Scope-tag cell carries one named exception, stated in the cell: a file tagged `type/project-pointer` satisfies the Wiki-hosted scope check with `project/` per its Per-Type Additions row |
| Freshness fields | "Freshness" table | `updated` required, `verified` optional; both `YYYY-MM-DD` |
| Location Gate | "Scope Boundaries" › Location Gate table | Lint runs envelope/tag checks only on files whose vault path matches a governed location; every other path is skipped entirely (no findings). Each row's left cell is a path glob; the union is the governed set. |
| Exemption tiers | "Scope Boundaries" › Exemption tiers table | Four tiers, keyed by `type/`. **Fully governed**: Invariant Core + Per-Type row. **Invariant-core-only**: Invariant Core enforced, Per-Type Additions skipped. **Structure-not-imposed**: no structural-contract check, only [[tag-taxonomy]] tag validity. **Out of scope**: no check at all (`type/data`, `type/meeting-capture`). A `type/` in none of the rows nor the Per-Type Additions table defaults to Invariant-core-only. |

`[tightening]` markers indicate rules stricter than lint's current behavior — escalate severity during reconciliation, do not silently adopt.
