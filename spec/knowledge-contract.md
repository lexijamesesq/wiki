---
tags:
  - type/spec
  - project/system
  - status/active
updated: 2026-07-09
---

# Knowledge Contract

The single source of truth for the vault's knowledge layer: **which tags are valid** (the tag dimension), **what envelope a file must have** (the structural dimension), **what each filing boundary adds** (the handoff dimension), and **what lint verifies** (the surface). Merges the former `tag-taxonomy.md`, `structural-contract.md`, `handoff-contracts.md`, and `lint-surface.md` into one contract; consumers reference this doc (and its parts) rather than duplicating its rules. The PII-bearing instance rosters stay split out in the sibling `tag-taxonomy-rosters.md` (real names/employers/top-level areas), which this contract references and never mirrors — it is the only file that lets this contract publish without PII.

`/lint-knowledge`'s `lint.py` parses two parts of this doc at runtime — the tag namespaces/vocabularies (Part I) and the structural envelope (Part II) — via the Parsing Contract at the end. It never hardcodes a rule value. The parsed section headers and table shapes are load-bearing; see **Machine-Parse Invariants** (end of doc) before editing.

Authority: derived from `target-architecture-v2.md` (space model, freshness design), `unified-ingress-design.md` (the ingress design, canonical for judgment tables and the mode/trust matrix), and the verifier-side metrics in `/lint-knowledge` + `Wiki/CLAUDE.md`. Rules stricter than lint's current behavior are marked **[tightening]** — escalate severity during reconciliation, do not silently adopt. New decisions are marked **[new]**.

---

## Part I — Tags

Each namespace is an **orthogonal question** Claude can ask about a page. Together they form a closed set of query dimensions. Tags outside the closed set are either malformed or a missing dimension (triggers review). **When you reach for depth in a tag, reach for another namespace first** — multiple orthogonal tags out-search a deep hierarchical path every time.

## The Namespaces

Six namespaces. Each answers one question.

| Namespace | Question | Vocabulary shape | Typical consumer |
|---|---|---|---|
| `type/<x>` | What KIND of page is this? | Closed set | Router (format handling); lint (type-specific rules); search (filter by role) |
| `project/<x>` | Which active Claude project OWNS this? | Closed set, matches `Projects/{Name}/` | Router delivery; cross-project queries; lint scope |
| `area/<hierarchy>` | Which life/work area is this ABOUT? | Hierarchical, semi-closed | Summary construction; Personal/Work filter; domain search |
| `topic/<x>` | What specific SUBJECTS does this cover? | Open, stewarded | Cross-project/cross-area discovery; search refinement |
| `person/<x>` | Who is REFERENCED on this page? | Closed per known roster | Relationship intelligence; meeting prep; entity lookup |
| `status/<x>` | What LIFECYCLE state is this in? | Closed set | Lint; search filter; prioritization |

Most pages carry tags from multiple namespaces. A typical Wiki page has 3+: `type/`, `area/` or `project/`, and one or more `topic/`.

## Per-Namespace Rules

### `type/`

**Vocabulary (closed set):**

| Value | Meaning |
|---|---|
| `type/knowledge` | Maintained narrative knowledge (`{workspace_root}/Wiki/Knowledge/` or project `Knowledge/`) |
| `type/raw` | **Deprecated.** Retag to `type/knowledge`. Reserved for truly immutable external source snapshots if needed. |
| `type/data` | Structured per-item record (Wiki/Data/, domain-scoped) — entity, event, or observation with typed frontmatter fields |
| `type/context` | Domain schema + Claude's durable working understanding (`{workspace_root}/Wiki/Contexts/`) — user context, principles, approach, distilled insights. Can span domains. |
| `type/project-pointer` | `{workspace_root}/Wiki/Contexts/` redirect to an active project |
| `type/summary` | Human-readable page (Personal/ or Work/) — human-owned structure, Claude-stewarded accuracy |
| `type/scratchpad` | Human-owned persistent scratch space — rough notes, research-in-progress, exploratory state |
| `type/working-notes` | Claude's ephemeral session scratch — temporary working space, cleaned up or absorbed into Context when done |
| `type/spec` | Technical specification |
| `type/agent-spec` | Agent definition |
| `type/reference` | Stable reference material |
| `type/log` | Append-only log (progress.md, etc.) |
| `type/dashboard` | Bases view / dashboard page |
| `type/claude-project` | Project CLAUDE.md |
| `type/claude-hub` | Hub CLAUDE.md |
| `type/claude-wiki` | Wiki CLAUDE.md (space-level stewardship sidecar) |
| `type/claude-space` | Space sidecar — a thin pointer at a top-level space root; links to canonical governance, does not restate it |
| `type/claude-system` | System project CLAUDE.md — vault-wide governance sidecar |
| `type/hub` | General hub page (not Claude-managed) |
| `type/eval` | Evaluation artifact |
| `type/recipe`, `type/workout`, `type/lodging-destination`, `type/travel-profile` | Domain-specific content shapes |
| `type/job_interview`, `type/candidate_interview`, `type/interview`, `type/interview_comms`, `type/interview_questions`, `type/recruiting`, `type/discovery`, `type/onboarding` | Interview/recruiting content shapes |
| `type/meeting-capture` | Curated captures from recurring meetings, organized by product area. Prepend-biased (newest first), one file per subject area per meeting. Consumer: `/capture-meeting`. |
| `type/working-doc` | Claude/operator working document — outcome-first analysis in progress, structure operator-owned. Structure-not-imposed tier. |
| `type/exploration` | In-progress authored exploration — a draft thinking-through, not yet maintained knowledge. Structure-not-imposed tier. |
| `type/playbook` | Operational process playbook — human-owned structure. Structure-not-imposed tier. |
| `type/strategy`, `type/docker` | Other domain-specific shapes |

**Threshold:** HIGH. New types require updating this contract + updating consumers (router, lint, skills).

**Depth:** Always 2. Use other namespaces for additional dimension.

### `project/`

**Vocabulary:** Closed set, matches `Projects/{Name}/` folder names in kebab-case.

**Authoritative source for active values:** runtime `list_directory` on `Projects/`. This contract deliberately does not enumerate — enumeration drifts, the filesystem does not. `/lint-knowledge` uses the filesystem; so should any other consumer.

**Threshold:** HIGH (procedural). Can't exist without a `Projects/{Name}/` folder. Enforced by `/new-project` (folder creation) and `/migrate-domain` / archival flows (folder removal).

**Depth:** 2 preferred; 3 only for durable sub-projects. Historical project tags (`project/bramblesoft/*`, `project/twig/*`) grandfathered at deeper levels.

### `area/`

**Vocabulary:** Hierarchical, semi-closed. New top-level areas rare; sub-areas grow more freely.

**Top-level roster:** the closed set of top-level `area/` values is operative lint data, not contract prose — it lives in `tag-taxonomy-rosters.md`, same treatment as the `person/` roster and the `area/work/` employer roster (real top-level areas are instance data). `/lint-knowledge` reads it at runtime; never mirror it here.

**Sub-areas:** open growth under a recognized top-level, not roster-governed. Authoritative source: the live tag graph — run `list_all_tags` before minting a new sub-area.

**Illustrative examples only (not real vocabulary):** `area/work/{employer}` — `area/work/acorndyne`; `area/foraging` with sub-areas `area/foraging/mushrooms`, `area/foraging/berries`.

**Threshold:** MEDIUM. Claude proposes new values; user confirms. New top-level areas get more scrutiny than new sub-areas.

**Depth:** 2-3 natural. Max 3. Depth 4+ is a code smell — use multiple tags across namespaces instead.

### `topic/`

**Vocabulary:** Open, stewarded. **Collapse is the default bias** — growth is restrained, not encouraged.

**Threshold:** LOW (stewarded). **Default action is NOT to create.** Before creating a new topic: (1) fuzzy-match existing topics, prefer existing over near-synonym; (2) query-axis test — "Would I plausibly search for this topic specifically across the vault?" If no, fold; (3) facet/sub-variant test — a method, retailer, brand, or framework within an existing broader topic folds into the broader.

**Common fold patterns:** methods/retailers/brands/frameworks within a domain → fold into the domain topic (`topic/gray-market` + `topic/counterfeit-detection` → `topic/fragrance`); material/style sub-variants → the category (`topic/sneakers` + `topic/leather-shoes` → `topic/shoes`); named frameworks within a discipline → fold; active ingredients/product types → fold into domain.

**Single-page topics allowed ONLY IF** they capture a query axis no existing topic does AND ≥2-3 pages will plausibly carry the topic in a reasonable timeline. Otherwise fold.

**Cross-project scope:** a topic is only useful if it's meaningful across the vault, not just within one domain.

**Depth:** Always 2. Hierarchy in topics is usually an area in disguise.

**Periodic consolidation:** `/lint-knowledge` runs a sub-variant-proliferation check; common stems surface as candidates.

### `person/`

**Vocabulary:** Closed per known roster. Kebab-case: `person/first-last`.

**Roster:** the closed vocabulary lives in `tag-taxonomy-rosters.md`, not here — real colleague names are instance data, split out so this contract can publish without PII. Illustrative examples only (not real vocabulary): `person/hazel-acorn`, `person/chip-chestnut`.

**Publication note:** `tag-taxonomy-rosters.md` holds real names/employers and is excluded from any published or republished form of this contract (e.g. a future public `knowledge-contract.sample.md`) — never mirror its content anywhere git-tracked.

**Threshold:** MEDIUM. Create on second+ appearance in working context — not for drive-by mentions.

**Depth:** Always 2.

### `status/`

**Vocabulary (closed set):**

| Value | Meaning |
|---|---|
| `status/stub` | Pending research, placeholder exists |
| `status/active` | Current, maintained, load-bearing |
| `status/current` | In-use / on the current list (domain-content lifecycle — e.g. a lens currently in the kit). Distinct from `status/active`, which marks a maintained knowledge-layer doc. |
| `status/archived` | Kept for history, no longer current |
| `status/deprecated` | Superseded, refer elsewhere |
| `status/draft` | In-progress, not yet active |

**Threshold:** HIGH. New statuses require updating all lifecycle consumers.

**Depth:** Always 2.

## Growth Thresholds (Summary)

| Namespace | Threshold | Enforcement |
|---|---|---|
| `type/` | HIGH | This contract; changes require spec + consumer updates |
| `status/` | HIGH | This contract; changes require lifecycle consumer updates |
| `project/` | HIGH (procedural) | `/new-project` enforces |
| `area/` | MEDIUM | Claude proposes, user confirms; `/lint-knowledge` flags unrecognized |
| `person/` | MEDIUM | Create on second+ appearance; `/lint-knowledge` flags unrecognized |
| `topic/` | LOW (stewarded) | Fuzzy-match before create; periodic consolidation via `/lint-knowledge` |

## Depth Limits (Summary)

| Namespace | Typical | Max |
|---|---|---|
| `type/` | 2 | 2 |
| `status/` | 2 | 2 |
| `project/` | 2 | 3 (historical tags grandfathered deeper) |
| `area/` | 2-3 | 3 (depth 4+ → split into multiple tags) |
| `topic/` | 2 | 2 |
| `person/` | 2 | 2 |

## The Depth Escape Hatch

When tempted to go deeper than the max, reach for another namespace first:

| Tempting deep path | Better: multiple tags |
|---|---|
| `area/hobby/astronomy/telescopes` | `area/hobby/astronomy` + `topic/telescopes` |
| `area/work/acorndyne/design/gms` | `area/work/acorndyne` + `project/cachetrack` |
| `area/territory/riverbank/willow-bend` | `area/territory` + `topic/riverbank` + `topic/willow-bend` |
| `topic/baking/sourdough` | `topic/baking` + `topic/sourdough` |

---

## Part II — The Structural Envelope

Governs the **envelope**: mechanically-verifiable static structure — required frontmatter fields, tag validity, discoverability, single title. It does NOT govern *content architecture* (how a body is organized, how it mutates, when it goes stale) — that varies within every `type/` and is out of scope (see Body & Content Architecture). Every rule here is checkable by lint without judgment. A file is well-formed only when it satisfies both the tag dimension (Part I) and this envelope.

## Invariant Core

Every knowledge-layer file MUST have:

| Element | Requirement |
|---|---|
| `type/` tag | Exactly one, from the closed `type/` vocabulary (Part I) |
| Scope tag | At least one `project/<name>` OR `area/<hierarchy>` |
| `status/` tag | Exactly one, from the closed `status/` vocabulary **[tightening — lint currently WARNING]** |
| `updated` | `updated: YYYY-MM-DD` frontmatter |
| Title | Exactly one level-1 heading (`# Title`) **[tightening — lint has no H1 check today]** |
| Tag validity | All tags conform to Part I — namespaces, closed vocabularies, depth limits |

Type-agnostic and destination-agnostic. Everything below adds to it.

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

`type/spec` and `type/reference` require the invariant core only; `sources` optional (authored, not captured/researched). `type/data` is **out of scope** entirely — domain content with typed domain frontmatter, not a knowledge-layer file (see Scope Boundaries); it carries no structural-contract requirements.

## Destination Modifiers

The same `type/` carries slightly different requirements by where it lives.

| Aspect | Wiki-hosted (`{workspace_root}/Wiki/Knowledge`, `Data`, `Contexts`) | Project-hosted (`Projects/<name>/Knowledge`, `System/`) |
|---|---|---|
| Scope tag | `area/<hierarchy>`; exception: `type/project-pointer` carries `project/` (Per-Type row) | `project/<name>` |
| `topic/` on `type/knowledge` | Required, ≥1 **[tightening]** | Optional |
| Index participation | None — `area/` + `topic/` tags ARE the index | An `index.md` entry for the file exists |

Each destination class has exactly one discovery mechanism: Wiki uses tags-as-index, project-hosted uses `index.md`. **Scope-tag exception:** `type/project-pointer` is Wiki-hosted yet points at a project — its Per-Type Additions row requires `project/`, and that row is authoritative: a Wiki-hosted project pointer satisfies the scope check with `project/`, not `area/`. Every other Wiki-hosted type takes `area/`.

**Index syncing is a process obligation, not a structural property.** The contract rule is only that an `index.md` entry *exists* (lint-checkable, file-at-rest). Keeping it synced on every create/delete/rename is the filing skills' responsibility (Part III), outside this envelope.

## Provenance

`sources` frontmatter — an array naming where the file's substance came from: a URL, `user-stated`, `AI research YYYY-MM-DD`, `inbox-capture`, `routine/<action> <run-id>` **[new]**, or `pre-contract` (legacy files predating this contract — see Migration Legacy). `routine/<action> <run-id>` is automated-lane attribution: it names the unattended routine and the specific run that produced the substance, so every automated write is traceable to its run report. It is the universal, machine-checkable provenance record. Requirement per type: see Per-Type Additions.

Provenance is `sources` frontmatter — universal and mechanically checkable. A verbatim-preservation body section (`## Original Capture`) is **not** part of this contract; it is scoped to *progressive-enhancement document types* (e.g. Incubator idea/initiative cards, governed by `incubator-reference.md`), which own that mechanism. Any prior mandate for a `## Original Capture` section on all Knowledge deliveries is **superseded** — reconciliation must de-scope it, not assume it is already Incubator-only.

## Freshness

Two date fields, distinct meanings:

| Field | Meaning | Requirement |
|---|---|---|
| `updated` | File last touched — any edit, including mechanical ops (retag, migration, frontmatter fix) | Required |
| `verified` | Content last reviewed for accuracy — a human or agent confirmed claims are current | Optional |

Both are dates (`YYYY-MM-DD`). Freshness checks use `verified` when present, `updated` when absent. The event that sets `verified` is defined by the lint/stewardship surface, not this contract.

## Body & Content Architecture

The contract's only body rule is the Invariant Core's single H1. Everything else about a file's body — its internal organization, how it mutates (overwrite / append / supersede), whether and how it goes stale — is **content architecture**, and is explicitly **out of scope**. It varies *within* every `type/` (one `type/knowledge` file is a decision chain, another a current-state snapshot, another an event series). None is mechanically checkable; none is governed here.

- Mutation discipline (the overwrite / append / supersede decision) is a separate concern — canonical home: `integration-modes.md` (Wiki/spec); architectural narrative in `target-architecture-v2.md` "Knowledge mutation discipline".
- Body-size and source-count heuristics (lint's `>150`-line and `>6`-source INFO flags) are lint's own QA heuristics, not contract rules. Lint may run checks beyond this contract; only the rules in the Parsing Contract are *contract* rules.

## Scope Boundaries

This contract governs **genuine knowledge-layer documents only** — maintained synthesis: methodology, specs, references, durable Claude working understanding, and Wiki Knowledge narrative. It does **not** govern domain content, operational records, archives, or raw captures. The boundary is **mechanically determinable** — lint decides governed vs. ungoverned from two signals, location and `type/` tag, with no judgment. A file is **in governed scope only if it passes the Location Gate AND carries a governed `type/`** (or, in a governed location, carries no `type/` at all — a genuine missing-classification defect). Everything else is out of scope and produces no findings.

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
| `Wiki/spec/*.md` | Governed contract docs (this file + `tag-taxonomy-rosters.md` + `calibration-surface.md` + `integration-modes.md`), depth-1 only |

Every other location is **ungoverned** and lint skips it entirely — no envelope checks, no tag-validity checks, no `no-type-tag` finding. This explicitly excludes:

- **Domain content** — `Wiki/Data/**` (gear, products, technology, recipes), and any per-project domain-content folder. Data records carry typed domain frontmatter by nature; the knowledge-layer envelope does not apply.
- **Operational records** — `Projects/Recruiting/Roles|Playbooks|Candidates/**`, candidate/role/interview files generally. Recruiting-domain conventions, not the knowledge-layer envelope.
- **Archives** — any file named `*-archive.md` or under an `Archived/` / `archive/` path segment. Frozen history; not maintained, not re-linted.
- **Raw captures and operational scratch** — `Projects/<name>/` non-`Knowledge`/`Context` working folders (`Research/`, `Activity/`, `Ideas/`, `Eval/`, `NPS/`, `Usage/`, meeting-notes folders). Raw inputs and operational records, not synthesis.
- **Incubator idea/initiative cards** — self-governed by `incubator-reference.md` (distinct scalar `type:` + `stage:` schema; not a closed-vocabulary `type/` tag).
- **Queue items** — `Wiki/Queue/**` — transient operator-judgment artifacts, deliberately ungoverned (Part III); their hygiene is owned by the queue mechanics, not lint.

A file in an ungoverned location is out of scope **even if it carries a `type/` tag** — location is the outer gate. Conversely, a file in a governed location with no `type/` tag is a genuine missing-classification defect and is flagged.

### Type Gate — governed vs. ungoverned `type/`

Within a governed location, the file's `type/` determines its tier. Two `type/` values name content out of scope wherever it sits — `type/data` (domain content) and `type/meeting-capture` (raw recurring-meeting capture); a file carrying either is ungoverned regardless of location.

**Exemption tiers** — a governed file's `type/` places it in exactly one tier. Lint derives the tier from this table:

| Tier | Lint treatment | `type/` values |
|---|---|---|
| **Fully governed** | Invariant Core + the file's Per-Type Additions row | every `type/` in the Per-Type Additions table |
| **Invariant-core-only** | Invariant Core enforced; Per-Type Additions skipped | `type/recipe`, `type/workout`, `type/dashboard`, `type/hub` — and, by default, any other closed-vocabulary `type/` value in neither the Per-Type Additions table nor the Structure-not-imposed tier |
| **Structure-not-imposed** | No structural-contract check applies; only Part I tag validity | `type/claude-project`, `type/claude-hub`, `type/claude-wiki`, `type/claude-space`, `type/claude-system`, `type/summary`, `type/scratchpad`, `type/working-notes`, `type/working-doc`, `type/exploration`, `type/playbook` |
| **Out of scope** | No check at all — file is ungoverned | `type/data`, `type/meeting-capture` (domain content / raw capture — see Location Gate) |

- **Invariant-core-only** types carry the full envelope but no per-type additions; body and further structure are the owning mechanism's call.
- **Structure-not-imposed** types are CLAUDE.md/hub/space sidecars, human-surface pages, ephemeral Claude scratch, in-progress drafts, and process playbooks; lint verifies only that any tags they carry are valid.
- **Out of scope** types get no lint check at all — surfaced here so the Type Gate is complete.

A `type/` in none of the tier rows nor the Per-Type Additions table defaults to Invariant-core-only.

## Migration Legacy

The contract describes the target. The existing corpus predates it and is substantially non-compliant. Reconciliation is a backfill pass, surfaced as a worklist by `/lint-knowledge`.

- **`sources` backfill** — most existing `type/knowledge` files carry no `sources`. Backfill the real origin where recoverable; `sources: [pre-contract]` where unrecoverable.
- **Single-H1 normalization** — legacy files with no H1, or opening with a body tag or `##` heading, get an H1.
- **`status/` tag migration** — legacy files use a scalar `status:` field; the tag is authoritative. Migration retags; the scalar is dropped once the tag is present.

Tracked reconciliation work, not blockers to adopting the contract.

---

## Part III — Filing Handoffs

Specifies the contract at each **filing handoff** — every boundary where content crosses into a knowledge-layer file. A filing-handoff contract = the Part II envelope (by reference) **+** a thin handoff-specific layer. This part holds only the layer; it does not restate the envelope.

Authority: `/wiki-intake`, `Projects/Router/router-spec.md`, `/session-closeout`, and — for §§4–5 — the ingress design (`unified-ingress-design.md`, canonical for the full kind→disposition matrix, judgment tables, and canonical-home discipline).

## Scope — filing handoffs only

Eight handoff points; four produce a knowledge-layer file and therefore have a *structural* contract:

| Handoff | Produces a file? | Covered |
|---|---|---|
| Wiki intake | Yes | §1 |
| Project knowledge filing | Yes | §2 |
| Session capture (`/capture` + closeout query-and-file) | Yes | §4 (absorbs former §3) |
| Automated multi-destination capture | Yes — `durable-knowledge` + `meeting-log` kinds only | §5 |
| Cross-project reference | No — a link between existing files | Link-integrity lint rule (Part IV) |
| Context loading | No — the read direction | Tracked separately (retrieval reflex) |
| Memory ↔ vault | No — a scope boundary | Tracked separately (associative persistence) |

Non-file dispositions are contracted elsewhere: queue items (`Wiki/Queue/`, ungoverned), the full kind→disposition matrix, and destination resolution live in the ingress design; personal-action appends in `router-spec.md`; Linear creation follows `linear-discipline`. Session closeout also updates project `CLAUDE.md` — not a filing handoff (`CLAUDE.md` is `type/claude-project`, Structure-not-imposed). Only the query-and-file half is a filing handoff (§4).

## Shared shape

Every filing-handoff contract has the same fields: **Base** (Part II envelope — always applies, not restated); **Destination** (selects the destination modifier); **Enforcer** (the skill/spec implementing it); **Pre-file gate** (judgment check(s) with an explicit pass/fail rule); **Field derivation** (how the handoff sets the delta values the envelope requires — `sources`, `area/`/`project/`, `topic/`); **Post-file** (index sync, cross-references); **Validation** (*Today* = what the enforcer verifies now; *Target* = filing-time envelope validation; *Periodic* = lint).

**Every filing handoff produces the full envelope.** The per-§ *Field derivation* lists only fields whose *value* is handoff-specific — fields not listed still apply (a freshly-filed page takes `status/active`; `updated` = today). Pre-existing enforcer schemas predate this contract and are incomplete; reconciling an enforcer raises its schema to the full envelope:

| Enforcer | Frontmatter fields it currently omits vs. the envelope |
|---|---|
| `/wiki-intake` | none — already applies `type/` / `area/` / `topic/` / `status/` / `updated` / `sources` |
| `router-spec.md` Knowledge Delivery | `status/`, `sources` |
| `/knowledge-layer` query-and-file (closeout Step 9) | `status/`, `sources`; Wiki-hosted branch also `area/`, `topic/` |

## §1 — Wiki intake

Content (router-delivered or pasted) → `{workspace_root}/Wiki/Knowledge/`. Covers the **filing branch** only — `/wiki-intake` first classifies intent (`knowledge` / `data-correction` / `explore` / `triage`); only `knowledge` intent reaches filing.

- **Destination:** `{workspace_root}/Wiki/Knowledge/{area}-{slug}.md` — Wiki-hosted modifier (`area/` scope, `topic/` required, tags-as-index).
- **Enforcer:** `/wiki-intake`.
- **Pre-file gate — coherence gate** (knowledge-intent only). Four criteria: self-contained, clear topic, additive, single-question-scoped (`single-question-scoped` is content architecture the envelope omits; the gate may use it as filing judgment though lint does not enforce it). **Decision rule:** all four pass → file; fails resolve per the calibration surface (§0 disposition philosophy + §2 mode bias): fixable fails are fixed and filed, duplicates and noise discard (logged), genuinely-stuck fails → a `Wiki/Queue/` item, `queue-kind: disposition`.
- **De-scoping (size heuristic):** the 150-line threshold is a lint **INFO heuristic, not a filing block**. Reconciling `/wiki-intake` must downgrade its 150-line halt to an advisory flag.
- **Field derivation:** `area/` = authoritative classification (load the domain context page + Part I); `topic/` = collapse-bias; `sources` = capture origin (`inbox-capture`, a URL, or `user-stated`).
- **Post-file:** no index step (tags-as-index). Duplicate scan — report overlap, do not block (append-bias).
- **Validation:** *Today* — post-filing tag check. *Target* — filing-time envelope validation via `lint.py --filing` (**[new]**, built — reached via the shared gatekeeper write-execution path). *Periodic* — lint.

## §2 — Project knowledge filing

Content (router-delivered or session-produced) → a project's Knowledge layer.

- **Destination:** `Projects/{name}/Knowledge/{slug}.md`, or `{workspace_root}/System/Knowledge/` / `System/` root — project-hosted modifier (`project/` scope, `index.md` entry required).
- **Enforcer:** `router-spec.md` "Knowledge Delivery Rules" today; a dedicated project intake skill is the future enforcer (**[new]**, not yet built).
- **Pre-file gate — opt-in + candidacy.** The destination project must declare a `### Knowledge` Intake subsection (opt-in), AND the content must be a Knowledge candidate. **Decision rule:** both true → file; `### Knowledge` absent → Task-axis only; not a Knowledge candidate → no Knowledge delivery. The `### Knowledge` declaration is a mechanical check; absent → a `Wiki/Queue/` proposal item, never a file (§§4–5 inherit this).
- **De-scoping:** the §2 enforcer MUST NOT write a `## Original Capture` body section — superseded by Provenance (Part II). Reconciling the enforcer must actively remove it.
- **Field derivation:** `project/` = the destination project; `sources` = capture origin; the project's `### Knowledge` declaration may extend the per-type schema — read it at runtime and conform.
- **Post-file:** append and sync the `index.md` entry; on dual-axis captures, cross-reference (`backlog-item` ↔ `context_doc`).
- **Validation:** *Today* — none. *Target* — filing-time envelope validation (**[new]**). *Periodic* — lint (envelope + `index.md` entry exists).

## §4 — Session capture

Knowledge produced during a live session (operator present) → `{Project}/Knowledge/` or `{workspace_root}/Wiki/Knowledge/`. Two entry points, one machinery — `/capture` mid-session; query-and-file at the session boundary. Absorbs the former §3 (session-closeout query-and-file): its durable-synthesis gate and field derivation are folded in here; the current enforcer is `/knowledge-layer` query-and-file, invoked by `/session-closeout` Step 9.

- **Destination:** the host project's Knowledge layer, or `{workspace_root}/Wiki/Knowledge/` — modifier per where it lands. Resolution and operator override per the ingress design; project-hosted resolutions honor §2's opt-in gate.
- **Enforcer:** `/capture` (mid-session) and `/knowledge-layer` query-and-file via `/session-closeout` Step 9 (boundary). Both emit candidates through the gatekeeper; neither routes candidates itself.
- **Pre-file gate — coherence at interactive thresholds.** Did the session produce synthesis a future session would need, that would otherwise be lost to chat history? Each candidate passes the four dimensions at interactive thresholds (dimensions, thresholds, worked examples live in the gatekeeper's calibration surface — canonical home; referenced, not restated). An explicit operator "capture this" pins inclusion. **Decision rule:** pass → file; uncertain → surface as a candidate for the operator; fail unpinned → discard (logged); fail pinned → a `Wiki/Queue/` item, `queue-kind: disposition`, with note — never silent discard.
- **Field derivation:** `sources` = the session (`AI research YYYY-MM-DD`; `user-stated` for user-provided facts); `project/` or `area/` per host destination; on the Wiki-hosted branch also `topic/` ≥1.
- **Post-file:** `index.md` sync on project-hosted filings; `updated` bump on touched pages; the capture report lists filed / queued / discarded with reasons.
- **Validation:** *Today* — the filing-time lint gate (`lint.py --filing`) PASS per filed page (interactive mode may file-then-fix, cap 3). *Periodic* — lint.

## §5 — Automated capture

Typed candidates from the unattended capture lane (Pi) → knowledge-layer files, no operator in the loop. Only two kinds produce files — `durable-knowledge` and `meeting-log`; the full kind→disposition matrix is defined in the ingress design (the automated column is the complete automated write authority). Every other disposition queues or discards.

- **Destination:** `durable-knowledge` → project `Knowledge/` or `{workspace_root}/Wiki/Knowledge/` by scope, on destination resolution per the calibration surface §5 (resolved-unique, or defensible best home with the alternative noted; unresolved → queue/discard per §0.3); `meeting-log` → the registered meeting's per-area rolling log (`type/meeting-capture` — out of scope per the Type Gate; the registered playbook owns its shape). Project-hosted resolutions honor §2's opt-in gate.
- **Enforcer:** the gatekeeper, automated mode — router + gatekeeper for all candidate disposition.
- **Pre-file gate — pre-commit write-plan validation.** The gatekeeper emits a write plan (new files: full composed content + enumerated content sources; existing targets: `{target, pre_state_hash, append_suffix}` only — whole-file overwrite structurally impossible); a context-free critic (rubric v2) validates the plan + composed artifacts before any vault write; apply is a deterministic script, not a model. **Decision rule:** PASS → apply; FAIL → nothing commits, plan + reasons → quarantine queue item, heartbeat suppressed.
- **Field derivation:** attribution mandatory on every automated write **[new]** — `sources` carries `routine/<action> <run-id>` (Provenance) plus the human-readable source attribution; scope tag per resolution; `topic/` ≥1 on Wiki-hosted `durable-knowledge`.
- **Post-file:** post-apply verify — `lint.py --filing` on new files; suffix-presence check on appends; FAIL → quarantine queue item, heartbeat suppressed, no further writes this run, no auto-revert. `index.md` sync on project-hosted filings. Every candidate ends as exactly one of filed / `Wiki/Queue/` item / logged discard.
- **Validation:** *Today* — pre-commit critic + post-apply `lint.py --filing`. *Periodic* — lint.

---

## Part IV — Lint Surface

The complete set of integrity checks that verify vault content against this contract. **Lint is the executable form of the contract.** `/lint-knowledge`'s `lint.py` derives rule *values* at runtime from Parts I–II via the Parsing Contract — it never hardcodes them. Scope: integrity checks only (Layers 1–2). Associative-layer integrity is tracked separately.

## Two execution modes

A check runs at filing-time, periodically, or both. **Single-file-at-creation → filing-time; drift-over-time or corpus-scale → periodic.**

- **Filing-time** — `lint.py --filing` (the same script as the periodic mechanical pass, run single-file with `[tightening]` rules escalated to HIGH) validates a filed file against Part II + the relevant Part III §. PASS = zero HIGH findings. Single-file, cheap. Built (ships with `/lint-knowledge` in dotty).
- **Periodic** — **two passes.** A **mechanical pass** (a script, no model) runs every deterministic check; a **judgment pass** (a model) runs the contradiction scan.

Envelope-compliance checks run **both** — filing-time on the new file, and in the periodic mechanical pass as `[tightening]` rules escalate against the legacy corpus.

## Periodic mode — mechanical pass + judgment pass

> If a check is deterministic, a script runs it. If a check needs judgment, a model runs it.

This is the methodology's dividing line — *if a rule needs judgment to check, it is not a contract rule.* The contracts were built so every contract rule is mechanically checkable; the mechanical pass is that promise kept. The split is **orthogonal** to the contract-derived vs. lint-heuristic source split — most LINT-sourced checks (broken links, orphan index entries, status coherence) are still mechanical. Exactly one periodic check is genuine judgment: the contradiction scan.

- **Mechanical pass** — a standalone script (`lint.py`, bundled with `/lint-knowledge`) runs every deterministic check, full-corpus, no model, read-only, emitting structured JSON + a human report. It **derives rule values at runtime** by parsing Parts I–II per the Parsing Contract; it holds no copy of a vocabulary or limit. It *does* encode the parsing recipe and check implementations — that is what a Parsing Contract is *for*. It **must** be full-corpus: the relational checks (broken wikilinks, cross-project refs, `index.md` integrity, stub drift, context coverage, `topic/` consolidation) are corpus-scale (a file's wikilink breaks when its *target* is deleted). Because it has no API cost, run it whole.
- **Judgment pass** — one check is genuine judgment: the **contradiction scan** (claims contradicted by a scope's `CLAUDE.md` Current State or other pages), plus the hub cross-reference for hub/subproject scopes. Best-effort INFO, not contract-derived, the only component that costs model tokens. It is **delta-scoped** — runs only over files changed since the last run (a contradiction comes into existence only when a file changes). **CLAUDE.md rule:** if the scope's `CLAUDE.md` is in the delta, widen the pass to all of that scope's knowledge files. Two accepted coverage gaps: a contradiction between a changed file A and an unchanged non-`CLAUDE.md` page B is caught only if A's scan loads B; contradictions predating the first run are caught by the first run (delta = whole scope) or an occasional `--full` pass.

**Change detection — the manifest.** The vault is Obsidian-synced (not git-tracked), so the delta is computed against a **manifest**: a JSON mapping each in-scope file's vault-relative path → SHA-256 content hash, plus the run timestamp. Each run, the script hashes every file and diffs: hash differs → changed; path absent → new; path in manifest gone from disk → deleted. **Delta set** = changed ∪ new. Deleted files are reported (they matter to relational checks) but not re-linted. Content hashing (not mtime) is used because Obsidian Sync rewrites mtimes. One manifest per scope, stored outside the vault and dotty (default `~/.cache/lint-knowledge/`, keyed by scope path; `--state-dir` overrides). First run = no manifest → every file "new" → delta = whole scope.

**Cost:** mechanical pass ≈ $0 (local CPU, seconds); judgment pass costs model tokens only over the delta (0–~15 files/run typical; empty delta → skipped → $0). The mechanical pass is cron-able directly; only the judgment pass needs a model session — the trigger only has to wake a model when the delta is non-empty.

**Script ↔ skill interface:** `lint.py` runs the mechanical pass + delta computation (args: scope path; `--json` / `--format text`; `--state-dir`; `--no-manifest` stateless full run; `--vault-root`). `/lint-knowledge` orchestrates: runs `lint.py`, runs the judgment pass over the delta (or whole scope under `--full`), merges the report. Flags: `--scope`, `--mechanical-only` ($0), `--full`.

## Check inventory

Source: **SC** = envelope (Part II) · **TT** = tags (Part I) · **HC** = filing handoffs (Part III) · **LINT** = lint's own QA heuristic. Pass: **M** = mechanical · **J** = judgment. Today: ✓ exists · ◐ partial · ✗ missing.

### Envelope — Invariant Core (SC)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Exactly one valid `type/` tag | Both | M | HIGH | ✓ |
| ≥1 scope tag (`project/` or `area/`) | Both | M | HIGH | ✓ |
| Scope tag matches destination | Both | M | HIGH | ✓ |
| Exactly one `status/` tag | Both | M | HIGH `[tightening]` | ✓ |
| `updated: YYYY-MM-DD` present | Both | M | HIGH | ✓ |
| Exactly one H1 (`# Title`) | Both | M | HIGH `[tightening]` | ✓ |
| All tags valid per Part I | Both | M | per the Tag-taxonomy block | ✓ |

These apply only to files in **governed scope** — the Location Gate is the outer filter. Within governed scope, the file's `type/` places it in an **Exemption tier**: fully-governed and *Invariant-core-only* types are held to the Invariant Core; *Structure-not-imposed* types get only tag-validity; *Out-of-scope* types get no check. The script derives the Location Gate globs and tier sets from the Scope Boundaries tables at runtime.

### Envelope — Per-Type (SC)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| `type/knowledge` carries `sources` | Both | M | HIGH | ✓ |
| `type/knowledge` Wiki-hosted carries `topic/` ≥1 | Both | M | HIGH `[tightening]` | ✓ |
| `type/project-pointer` carries `project/` + `topic/` | Periodic | M | HIGH | ✓ |

`type/project-pointer` is periodic-only: no filing handoff produces a pointer, so the filing-time critic never validates one. Per-type checks apply only to types in the Per-Type table; either Exemption tier is exempt from per-type additions.

### Tag taxonomy (TT — all exist)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Namespace membership; closed `type/`·`status/`·`project/` vocab | Both | M | HIGH | ✓ |
| Depth limits | Both | M | HIGH | ✓ |
| `area/` · `person/` recognition | Both | M | WARNING | ✓ |
| Legacy `people/*` · `phase/*` | Both | M | MEDIUM | ✓ |
| `topic/` consolidation candidates | Periodic | M | INFO | ✓ |

`topic/` consolidation is corpus-scale (compares topics across all files) — periodic only; deterministic (Jaccard on char 3-grams + same-stem grouping), so mechanical despite advisory output.

### Structural integrity

| Check | Source | Mode | Pass | Severity | Today |
|---|---|---|---|---|---|
| Broken `[[wikilinks]]` | LINT | Periodic | M | MEDIUM | ✓ |
| Cross-project references are wikilinks + resolve | LINT | Periodic | M | MEDIUM | ✗ |
| Stub drift (`type/project-pointer` → missing project) | TT | Periodic | M | HIGH | ✓ |
| Project-hosted file has an `index.md` entry | SC | Periodic | M | MEDIUM | ✓ |
| No orphan `index.md` entries | LINT | Periodic | M | MEDIUM | ✓ |
| Context-page coverage (`area/` with Knowledge but no Context) | SC | Periodic | M | WARNING | ✓ |
| Stale-suspects targets exist (`stale_suspects` paths resolve) | LINT | Periodic | M | WARNING | ✓ |
| Status coherence (scalar `status:` matches `status/` tag) | LINT | Periodic | M | HIGH | ✓ |

The broken-wikilink check covers `[[wikilinks]]` only — `![[embeds]]` excluded (an embed may legitimately target a non-`.md` attachment). **Broken-wikilink is MEDIUM, not HIGH** — link entropy is real and worth fixing, but it does not make a file structurally non-compliant, and HIGH-tiering it crowds genuine envelope defects. Status coherence is migration-era (a contract-compliant new file carries only the tag).

### Freshness (SC)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Stale — `verified`/`updated` past the window | Periodic | M | WARNING | ✓ |
| Unverified — `updated` present, `verified` absent | Periodic | M | INFO `[suppressed]` | ◐ |

**`unverified` is suppressed** — `verified` has no producer today, so the check would fire on essentially every governed file (pure noise). The mechanical pass MUST NOT emit `unverified` findings until a `verified` producer ships; the row stays so re-enabling it is a one-line change.

### Contradiction (LINT — the judgment pass)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Claims contradicted by `CLAUDE.md` Current State / other pages | Periodic | J | INFO | ✓ |
| Hub cross-reference (hub/subproject scopes only) | Periodic | J | INFO | ✓ |

The sole judgment-pass checks — best-effort, not contract-derived, delta-scoped.

### Filing-handoff (HC)

| Check | Mode | Pass | Severity | Today |
|---|---|---|---|---|
| Filed file satisfies the full envelope (per the handoff's §) | Filing | — | HIGH | ✓ (`lint.py --filing`, single-file) |

Filing-time validation is `lint.py --filing` — single-file, not part of the periodic split; the same script as the periodic mechanical pass, filing mode.

## Cross-project-reference link-integrity

A reference from one project's Knowledge into another's must be a `[[wikilink]]`, not a bare path or prose mention — wikilinks are vault-navigable and lint-checkable. The target must resolve. Periodic, MEDIUM, mechanical — the broken-wikilink check scoped to links crossing a `project/` boundary, plus the rule that the cross-project reference must *be* a wikilink. The script detects path-shaped cross-project references (bare `Projects/Other/...` paths); freeform prose mentions with no path are out of mechanical scope.

---

## Part V — Parsing Contract

`/lint-knowledge`'s `lint.py` extracts rules from Parts I–II at runtime — never hardcodes them. Every rule below is mechanically checkable. No rule appears elsewhere in this contract without a row here; if it can't be parsed, it isn't a contract rule. `[tightening]` markers indicate rules stricter than lint's current behavior — escalate during reconciliation.

### Tag rules (Part I)

| What to extract | Where | How to parse |
|---|---|---|
| Namespace prefixes | "The Namespaces" table, col 0 | Each entry `` `x/<…>` `` → prefix `x`; expect ≥6 |
| Closed `type/` vocabulary | `type/` › "Vocabulary (closed set)" table, col 0 | Backticked `type/*` values; rows whose Meaning cell says "Deprecated" also feed the deprecated set |
| Closed `status/` vocabulary | `status/` › first table, col 0 | Backticked `status/*` values |
| Depth limits | "Depth Limits (Summary)" table | col 0 = namespace, col 1 = typical, col 2 = max (first integer) |
| `area/` · `person/` sections | presence of the `area/` and `person/` sub-sections | Normative rules live here; instance rosters in `tag-taxonomy-rosters.md` (parsed separately, PII-excluded) |
| Grandfathered `project/` prefixes | `project/` section | `` `project/<x>/*` `` patterns |

### Envelope rules (Part II)

| What to extract | Where | How to parse |
|---|---|---|
| Invariant-core elements | "Invariant Core" table | Each row = one presence/cardinality check; col 0 = element, col 1 = rule; `[tightening]` in col 1 escalates severity |
| Invariant-core tag validity | "Invariant Core" › "Tag validity" row | Delegates to Part I |
| Invariant-core body element | "Invariant Core" › "Title" row | Body: exactly one level-1 (`#`) heading |
| Per-type required additions | "Per-Type Additions" table | Row keyed by `type/` (col 0); col 1 = extra tags (`—` = none; a `topic/` marked "Wiki-hosted" is destination-conditional per Destination Modifiers, else unconditional), col 2 = `sources` (Required / Optional / n/a) |
| Destination modifiers | "Destination Modifiers" table | Rows = aspects; the "Scope tag" row's Wiki/project cells yield `wiki_scope_tag` / `project_scope_tag`; each cell is a static file-at-rest check except Wiki-hosted "Index participation" (tag-based, no check) |
| Freshness fields | "Freshness" table | `updated` required, `verified` optional; both `YYYY-MM-DD` |
| Location Gate | "Scope Boundaries" › Location Gate table | Each row's col 0 = backticked path glob(s); the union is the governed set. Lint runs checks only on governed paths; every other path is skipped (no findings) |
| Exemption tiers | "Scope Boundaries" › Exemption tiers table | Four tiers, col 0 = tier, col 2 = `type/` values. **Fully governed**: Invariant Core + Per-Type row. **Invariant-core-only**: Invariant Core, Per-Type skipped. **Structure-not-imposed**: no structural check, only tag validity. **Out of scope**: no check (`type/data`, `type/meeting-capture`). A `type/` in none of the rows nor Per-Type defaults to Invariant-core-only |

---

## Consumers & config keys

Skills resolve this contract by config key (global CLAUDE.md › Configuration). Post-merge, four keys point at this one file (kept as distinct names to avoid churn; a future single `references.knowledge_contract` is optional cleanup):

- `references.tag_taxonomy`, `references.structural_contract`, `references.handoff_contracts`, `references.lint_surface` → `Wiki/spec/knowledge-contract.md`
- `tag-taxonomy-rosters.md` is unchanged and is NOT resolved by any of these keys — `lint.py` and `qa.py` locate it directly at `Wiki/spec/tag-taxonomy-rosters.md`.

Primary consumers: `/lint-knowledge` + `lint.py` (Parts I–II Parsing Contract, periodic surface Part IV; `--filing` mode is the filing-time surface, Part II + the named Part III §), `/wiki-intake` (§1), `router-spec.md` Knowledge Delivery (§2), `/knowledge-layer` query-and-file (§4), `/gatekeeper` (§§1/4/5), `/capture` (§4), `/queue` (Location Gate — queue is ungoverned), `/house-qa` (rosters split), `/sample-universe` (grandfathered `project/*` + `area/work/*` examples), `target-architecture-v2.md` (namespace definitions), project CLAUDE.md templates.

---

## Machine-Parse Invariants

`lint.py` parses this file for BOTH the tag rules (Part I) and the envelope rules (Part II); `main()` points its `taxonomy_path` and `sc_path` at this one file, `rosters_path` at the sibling `tag-taxonomy-rosters.md`. The following must survive any future edit verbatim (the merge may reorder around them, but not alter them):

1. **Exact section headers**, byte-for-byte: `## The Namespaces`; `### \`type/\``; `### \`status/\``; `## Depth Limits (Summary)`; `### \`area/\``; `### \`person/\``; `### \`project/\``; `## Invariant Core`; `## Per-Type Additions`; `## Destination Modifiers`; `## Scope Boundaries` (containing a Location Gate table then an Exemption tiers table, in that order). Do not restate any of these as a line-start header anywhere else in the file — the parsers take the first match.
2. **`## The Namespaces` must not appear inline** anywhere above its real section (its presence check is unanchored). All other header searches are line-anchored.
3. **Table shapes:** column counts and backtick formatting per the Parsing Contract. The `type/` vocab table must retain the `**Vocabulary (closed set):**` marker before it and keep "Deprecated" in the `type/raw` Meaning cell. The Exemption tiers table must keep all four rows (Invariant-core-only, Structure-not-imposed, Out of scope non-empty — lint fails loud on any empty tier) with `type/` values in backticks in column 3. The Location Gate table must keep ≥1 backticked glob in column 1.
4. **Namespace sub-section order** (`type/` → `project/` → `area/` → `topic/` → `person/` → `status/`) keeps the `project/` grandfather scan bounded by the following `area/` header — preserve at least one `### \`…/\`` header after `### \`project/\``.
5. **Part headers are H2** (`## Part N — …`); only the document title is H1. This file is itself governed (Location Gate: `Wiki/spec/*.md`) and must satisfy its own single-H1 rule.
