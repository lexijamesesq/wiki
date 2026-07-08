---
tags:
  - type/reference
  - project/system
  - status/active
updated: '2026-07-07'
status: active
---
# Tag Taxonomy

Canonical reference for the closed set of tag namespaces used across the vault. This doc is the source of truth — other artifacts (specs, skills, lint rules) reference it rather than duplicating the rules.

---

## Principle

Each namespace is an **orthogonal question** Claude can ask about a page. Together they form a closed set of query dimensions. Tags outside the closed set are either malformed or represent a missing dimension (triggers review).

**When you reach for depth in a tag, reach for another namespace first.** Multiple orthogonal tags out-search a deep hierarchical path every time.

---

## The Namespaces

Six namespaces. Each answers one question.

| Namespace | Question | Vocabulary shape | Typical consumer |
|---|---|---|---|
| `type/<x>` | What KIND of page is this? | Closed set | Router (format-specific handling); lint (type-specific rules); search (filter by role) |
| `project/<x>` | Which active Claude project OWNS this? | Closed set, matches `Projects/{Name}/` | Router delivery; cross-project queries; lint scope |
| `area/<hierarchy>` | Which life/work area is this ABOUT? | Hierarchical, semi-closed | Summary construction; Personal/Work filter; domain search |
| `topic/<x>` | What specific SUBJECTS does this cover? | Open, stewarded | Cross-project/cross-area discovery; search refinement |
| `person/<x>` | Who is REFERENCED on this page? | Closed per known roster | Relationship intelligence; meeting prep; entity lookup |
| `status/<x>` | What LIFECYCLE state is this in? | Closed set | Lint; search filter; prioritization |

Most pages carry tags from multiple namespaces. A typical Wiki page has 3+: `type/`, `area/` or `project/`, and one or more `topic/`.

---

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
| `type/scratchpad` | Human-owned persistent scratch space (Personal/Work Scratchpads) — rough notes, research-in-progress, exploratory state |
| `type/working-notes` | Claude's ephemeral session scratch — temporary working space, cleaned up or absorbed into Context when done |
| `type/spec` | Technical specification |
| `type/agent-spec` | Agent definition |
| `type/reference` | Stable reference material |
| `type/log` | Append-only log (progress.md, etc.) |
| `type/dashboard` | Bases view / dashboard page |
| `type/claude-project` | Project CLAUDE.md |
| `type/claude-hub` | Hub CLAUDE.md |
| `type/claude-wiki` | Wiki CLAUDE.md (space-level stewardship sidecar) |
| `type/claude-space` | Space sidecar — a thin pointer at a top-level space root (e.g. `Projects/CLAUDE.md`); links to canonical governance, does not restate it |
| `type/claude-system` | System project CLAUDE.md — vault-wide governance sidecar |
| `type/hub` | General hub page (not Claude-managed) |
| `type/eval` | Evaluation artifact |
| `type/recipe`, `type/workout`, `type/lodging-destination`, `type/travel-profile` | Domain-specific content shapes |
| `type/job_interview`, `type/candidate_interview`, `type/interview`, `type/interview_comms`, `type/interview_questions`, `type/recruiting`, `type/discovery`, `type/onboarding` | Interview/recruiting content shapes |
| `type/meeting-capture` | Curated captures from recurring meetings, organized by product area. Prepend-biased (newest first), one file per subject area per meeting. Consumer: `/capture-meeting` skill. |
| `type/working-doc` | Claude/operator working document — outcome-first analysis in progress, structure operator-owned. Structure-not-imposed tier. |
| `type/exploration` | In-progress authored exploration — a draft thinking-through, not yet maintained knowledge. Structure-not-imposed tier. |
| `type/playbook` | Operational process playbook (e.g. recruiting role playbooks) — human-owned structure. Structure-not-imposed tier. |
| `type/strategy`, `type/docker` | Other domain-specific shapes |

**Threshold:** HIGH. New types require updating this doc + updating consumers (router, lint, skills).

**Depth:** Always 2. Use other namespaces for additional dimension.

### `project/`

**Vocabulary:** Closed set, matches `Projects/{Name}/` folder names in kebab-case.

**Authoritative source for active values:** runtime `list_directory` on `Projects/`. The taxonomy doc deliberately does not enumerate — enumeration drifts, the filesystem does not. `/lint-knowledge` uses the filesystem; so should any other consumer.

**Threshold:** HIGH (procedural). Can't exist without a `Projects/{Name}/` folder. Enforced by `/new-project` skill (folder creation) and `/migrate-domain` / archival flows (folder removal).

**Depth:** 2 preferred; 3 only for durable sub-projects. Historical project tags (`project/bramblesoft/*`, `project/twig/*`) grandfathered at deeper levels.

### `area/`

**Vocabulary:** Hierarchical, semi-closed. New top-level areas rare; sub-areas grow more freely.

**Top-level roster:** the closed set of top-level `area/` values is operative lint data, not contract prose — it lives in `tag-taxonomy-rosters.md`, same treatment as the `person/` roster and the `area/work/` employer roster (real top-level areas are instance data; see `person/` section above for the publication note). `/lint-knowledge` reads it at runtime; never mirror it here.

**Sub-areas:** open growth under a recognized top-level, not roster-governed. Authoritative source: the live tag graph — run `list_all_tags` to see what sub-areas already exist under a top-level before minting a new one.

**Illustrative examples only (not real vocabulary):**
- `area/work/{employer}` — `area/work/acorndyne`.
- `area/foraging` — a plain top-level with two sub-areas: `area/foraging/mushrooms`, `area/foraging/berries`.

**Threshold:** MEDIUM. Claude proposes new values; user confirms. New top-level areas get more scrutiny than new sub-areas.

**Depth:** 2-3 natural. Max 3. Depth 4+ is a code smell — use multiple tags across namespaces instead.

### `topic/`

**Vocabulary:** Open, stewarded. **Collapse is the default bias** — growth is restrained, not encouraged.

**Threshold:** LOW (stewarded). **Default action is NOT to create.** Before creating a new topic:
1. Fuzzy-match existing topics. Prefer existing over near-synonym.
2. Query-axis test: "Would I plausibly search for this topic specifically across the vault?" If no, fold into a broader existing topic.
3. Facet/sub-variant test: Does this describe a facet, method, retailer, brand, or framework within an existing broader topic? If yes, use the broader.

**Common fold patterns** (from pilot experience):
- Methods, retailers, brands, frameworks within a domain → fold into the domain topic (e.g., `topic/gray-market` + `topic/counterfeit-detection` + `topic/sourcing` → `topic/fragrance`)
- Material/style sub-variants → fold into the category (`topic/sneakers` + `topic/leather-shoes` → `topic/shoes`)
- Named frameworks within a discipline → fold (`topic/kibbe` + `topic/style-discovery` + `topic/stylist-methodology` → `topic/style-direction`)
- Active ingredients, product types within a domain → fold into domain (`topic/retinoid` + `topic/vitamin-c` + `topic/anti-aging` → `topic/skincare`)

**Single-page topics allowed ONLY IF:**
- They capture a query axis no existing topic does
- AND at least 2-3 pages will plausibly carry the topic within a reasonable timeline
- Otherwise, fold

**Cross-project scope:** Wiki spans projects and domains. Topics should scale globally — a topic is only useful if it's meaningful across the vault, not just within one domain's pages.

**Depth:** Always 2. Hierarchy in topics is usually an area in disguise.

**Periodic consolidation:** `/lint-knowledge` includes a sub-variant-proliferation check. Common stems surface as consolidation candidates.

### `person/`

**Vocabulary:** Closed per known roster. Kebab-case: `person/first-last`.

**Roster:** the closed vocabulary lives in `tag-taxonomy-rosters.md`, not here — real colleague names are instance data, split out so this contract can publish without PII. Illustrative examples only (not real vocabulary): `person/hazel-acorn`, `person/chip-chestnut`.

**Publication note:** `tag-taxonomy-rosters.md` holds real names/employers and is excluded from any published or republished form of this contract (e.g. a future public `tag-taxonomy.sample.md`) — never mirror its content anywhere git-tracked.

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

---

## Growth Thresholds (Summary)

| Namespace | Threshold | Enforcement |
|---|---|---|
| `type/` | HIGH | This doc is the contract; changes require spec + consumer updates |
| `status/` | HIGH | This doc is the contract; changes require lifecycle consumer updates |
| `project/` | HIGH (procedural) | `/new-project` skill enforces |
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

## Downstream Consumers

Artifacts that reference this document (rather than duplicating the rules):

| Artifact | What it consumes | Status |
|---|---|---|
| `target-architecture-v2.md` | Namespace definitions, Wiki/ space tagging conventions | Current |
| `/new-project` skill | `project/` threshold (procedural enforcement); `topic/` for pointer stub tag suggestions | Done |
| `router-spec.md` | Routes Tasks by `project/`; routes Knowledge by `project/` OR `area/` | Pending |
| `intake-defaults.md` | Frontmatter schema references this doc | Pending |
| `/lint-knowledge` | Validates namespace membership; enforces depth limits; flags unrecognized `area/` / `person/` tags; fuzzy-matches `topic/` orphans; flags Knowledge/ files over size/source thresholds | Pending |
| `/wiki-intake` | Applies `type/knowledge` + `area/*` + `topic/*` + `status/*` to incoming Knowledge/ files | Pending |
| `routing-architecture.md` | References namespace definitions, destination contract pattern, handler accountability | Current |
| `/capture-meeting` | Applies `type/meeting-capture` + `area/*` + `topic/*` + `status/*` to meeting capture files | Current |
| Project CLAUDE.md templates | Reference this doc; don't enumerate tag rules inline | Pending |
