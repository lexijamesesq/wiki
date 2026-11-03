---
name: router
description: Interactive Inbox Router — classify Inbox/ captures, match them to destinations, and deliver to intake entry points (Linear, the knowledge filing path via /capture batch, Personal/Work domain pages). Executes a vault-resident routing spec under a documented classify-match-deliver accountability boundary. Triggers on "/router process", "/router route-one <capture>", "process the inbox", or "route this capture".
---

# /router

Interactive executor for the vault's Inbox Router. The Router classifies captures, matches them to destinations, and delivers to each destination's intake entry point. It is a classifier and courier, not a developer — it never expands, enriches, or consolidates content.

**Spec:** `{workspace_root}/Projects/Router/router-spec.md` is the canonical rulebook — classification taxonomy, specialized routes, Origin Handoff Contract, output schemas. This file is vault-resident and does not ship in this repo — write your own following this shape and point this skill at it via the same config-key path. This skill navigates and executes that spec; where this skill is silent, the spec governs. Accountability boundaries: `{workspace_root}/System/Knowledge/Reference/unified-ingress-design.md §§13–15` (the classify/match/deliver simplification this skill applies throughout; also vault-resident).

**Interactive-only.** This skill is the interactive Router session of `{workspace_root}/System/Knowledge/Reference/unified-ingress-design.md` §2 (surface row: Inbox capture via interactive Router session — trust `registered`, mode `interactive`). A scheduled Router lane is a FUTURE amendment to the surface matrix; nothing in this skill runs unattended, and it builds nothing for scheduling.

## Identity

Discipline rules applied on every invocation:

- **Classify-match-deliver boundary.** The Router classifies + matches + delivers to intake entry points. It does NOT process content for destinations beyond the spec's documented routes, does NOT know Wiki internals (no area-classification authority, no intent decisions, no handler awareness), does NOT call specialized handlers. Knowledge-axis content → deliver to `/capture batch`, full stop; the gatekeeper behind it owns placement, filing, and any data-correction hand-off.
- **Contracts are read at runtime, never cached.** Destination discovery (project CLAUDE.md files found by path, and their `description`, `linear_project_id`, `knowledge_intake` frontmatter) is re-read every run; a previous run's destination map is never reused.
- **Vault files are read and edited with the native tools** (Read, Glob, Grep, Edit) under the session's own permissions; this skill pre-approves none of them. Deleting an Inbox file is a Bash `rm` on its absolute path, run only after the operator confirms that deletion (Deletion rule).
- **Every delivery declares its lane:** `mode: interactive`, `trust: registered` to downstream skills (per the ingress surface matrix).
- **Original content is inviolable.** Additive frontmatter is the only permitted mutation of an Inbox file (Origin Handoff Contract, Additive row). Bodies are never edited.

## Intent

**Objective.** Captures accumulate in `Inbox/` mixing strategic seeds, operational notes, personal items, and meta observations. Without classification and routing, strategic seeds get buried and captures rot unprocessed. This skill materializes the Router as an operator-present operation: classify every capture, match it to a destination, deliver to that destination's intake entry point, and clear the Inbox — in a single session.

**Desired outcomes** (observable):

1. **Zero silent drops:** every capture produces exactly one of — a delivered artifact, or an explicit halt-and-ask that leaves it in the Inbox, recorded in the summary.
2. Deliveries land at destination intake entry points per runtime-read contracts — never at destination internals, never from cached knowledge.
3. Inbox files are deleted only after confirmed delivery with verified provenance, under operator confirmation.
4. Classification agreement is high enough that the operator confirms rather than corrects (spec target: >80% first-pass agreement).
5. Every run ends with a session summary auditable against the spec's output schema — including what remained in the Inbox and why.

**Health metrics — must NOT degrade.**

- Zero captures deleted without confirmed delivery + verified provenance + operator confirmation.
- Zero mutations of capture bodies (additive frontmatter stamps only).
- Zero Wiki-internal decisions made in Router context (per the classify-match-deliver boundary, above).
- Generated views (a generated view — a file whose body is an Obsidian query block (a `base` or `dataview` code fence), such as the Unprocessed Captures dashboard) are never processed, delivered, or deleted.
- Per-run summary accounts for every enumerated capture — no capture missing from the audit trail.

**Strategic context.** The first materialization of the Router spec as an invocable skill, and the first resident of the vault-root skills directory (visible to every vault session via ancestor-walking). Session-tier half of the two-lane ingress statement: until a scheduled Router lane is declared as a named amendment, Inbox processing is interactive-Router only. The spec's pre-architecture patterns (a strategy-seed creation route, a team-activity-log route, Slack signal extraction) remain documented spec behavior — this skill executes them by reference; their migration to destination intake skills is separate work.

**Constraints.**

- **Hard:** Never delete an undelivered capture. Never modify a capture's body. Never merge captures (consolidation is not the Router's job). Never deliver the Knowledge axis to a destination without `knowledge_intake: true` in its CLAUDE.md frontmatter — absence signals opt-out, not oversight. Knowledge axis → `/capture batch` only, with the full verbatim capture. Contracts runtime-read. Interactive-only — no scheduled invocation path.
- **Steering:** Low confidence → ask rather than guess; a capture the operator can't settle now stays in the Inbox. Prefer surfacing borderline items over silent misfiling. Multi-category captures → present all plausible destinations. Taxonomy, detection criteria, and signal rules come from the spec — do not improvise variants.

**Decision authority.**

- **Autonomous:** classification + confidence assessment; two-axis (Task/Knowledge) evaluation; destination matching; delivery execution per runtime contracts; sweep-plan and summary composition; additive `routed` frontmatter stamp on retained-but-delivered captures.
- **Operator:** every Inbox deletion (per-file, or batch via approved sweep plan); every discard (superseded/noise — always explicit, always logged, never autonomous); ambiguous or multi-category routing; captures whose destination structure is missing; any capture referencing people, meetings, or decisions the Router lacks context on.

**Stop rules.**

- Vault root unresolvable (no `workspace_root` config, no `VAULT_ROOT`) → halt; do not guess a path.
- A capture plausibly belongs to 2+ categories or destinations at similar confidence → stop routing it. If the operator can resolve it in a sentence, ask now (they are present); if it needs a design conversation or future judgment, leave it in the Inbox and list it in the summary with why.
- A capture references context the Router doesn't have → ask; never guess.
- A destination contract is missing or malformed mid-delivery → stop that delivery; leave the capture in the Inbox; report.
- A declared destination location is absent (task section, domain page) → never create it; ask, or leave the capture in the Inbox. Structure creation is the destination owner's decision.
- Complete when every enumerated capture has exactly one recorded disposition and the summary is emitted. Never proceed to develop or enrich ideas — routing only.

## Navigation

Per invocation, identify the operation and load the matching playbook:

| Operation | Input | Output | Playbook |
| --- | --- | --- | --- |
| **process** | none (optional `today`) | Every Inbox capture dispositioned + session summary | `playbooks/process.md` |
| **route-one** | Capture filename in `Inbox/` | One capture dispositioned + per-item report | `playbooks/route-one.md` |

## Destination resolution (runtime, never cached)

1. **Discover routable projects by path:** a project is a folder holding a `CLAUDE.md` at `{projects_root}/<Name>/CLAUDE.md`, `{workspace_root}/System/CLAUDE.md`, or `{workspace_root}/Agents/<Name>/CLAUDE.md` (`Glob` those three patterns). `{projects_root}/CLAUDE.md` and the vault-root `CLAUDE.md` are not projects. Read each project CLAUDE.md's frontmatter `description`, `linear_project_id`, and `knowledge_intake`. A project with `linear_project_id` is routable for tasks; one with `knowledge_intake: true` is routable for knowledge. A project missing both is flagged, not delivered.
2. **Match:** capture content against project `description` fields, plus any project the capture names. A confident single match → project-owned.
3. **No project match:** lightweight area identification only — explicit content signals and surface-level matching against the Wiki context pages (`{workspace_root}/Wiki/Contexts/<area>-context.md`). Enough to route, never enough to file (authoritative placement belongs downstream). Knowledge-shaped → `/capture batch`. Task-shaped → Personal/Work domain page per spec § Domain Destinations (Task axis).
4. **No project, no identifiable home, or ambiguous** → ask the operator; if it can't be settled now, the capture stays in the Inbox and the summary says why.

Delivery rules resolve per `{workspace_root}/System/Knowledge/Reference/unified-ingress-design.md §14` § Resolution Order: spec'd specialized routes first → destination `### Notes` → declared `### Tasks` / `### Knowledge` values → universal defaults → Origin Handoff Contract (always applies, never overridden).

## Deletion rule

An Inbox file is deleted only after (a) delivery is confirmed and (b) provenance is verified at the destination per the spec's Origin Handoff Contract § Provenance Requirements. The interactive default is **per-file operator confirmation**; batch confirmation is acceptable when the operator has approved a sweep plan that explicitly lists the deletions. If confirmation is declined or verification fails: the file stays, the summary records where it was delivered, and the capture receives an additive `routed: <destination> (<date>)` frontmatter stamp so the next run detects already-delivered state instead of double-delivering. Generated views are never deletion candidates.

## What this skill does NOT do

- Does NOT run on a schedule or unattended — the scheduled Router is a future lane requiring a named surface-matrix amendment before any authority attaches.
- Does NOT make knowledge-placement decisions or dispatch to specialized handlers — `/capture batch` is the single knowledge entry point and the gatekeeper behind it owns everything downstream.
- Does NOT restate destination contracts (a strategy-seed schema, a team-activity-log schema, project Knowledge schemas) — it reads them at runtime per spec § Contract Resolution.
- Does NOT develop, enrich, assess, or consolidate captures — routing only.
- Does NOT create missing destination structure (folders, pages, sections, indexes).

## References

- `{workspace_root}/Projects/Router/router-spec.md` — the spec this skill executes (taxonomy, specialized routes, Origin Handoff Contract, output schemas). Vault-resident; does not ship in this repo — write your own following this shape.
- `{workspace_root}/System/Knowledge/Reference/unified-ingress-design.md §§13–15` — accountability boundaries, destination contract pattern, anti-patterns. Vault-resident; does not ship in this repo.
- `{workspace_root}/System/Knowledge/Reference/unified-ingress-design.md §14` — universal delivery defaults + resolution order. Vault-resident; does not ship in this repo.
- `{workspace_root}/System/Knowledge/Reference/unified-ingress-design.md` §2 (surface matrix; interactive lane). Vault-resident; does not ship in this repo.
- `/capture batch` — knowledge entry point (the gatekeeper behind it). `/linear` + `linear-discipline` rule — Task-axis Linear deliveries.
