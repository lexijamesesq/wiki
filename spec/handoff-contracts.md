---
tags:
  - type/spec
  - project/system
  - status/active
updated: '2026-07-07'
---
# Filing-Handoff Contracts

Specifies the contract at each **filing handoff** — every boundary where content crosses into a knowledge-layer file. A filing-handoff contract = [[structural-contract]] (the envelope, by reference) **+** a thin handoff-specific layer. This doc holds only the layer; it does not restate the envelope.

Sibling of [[structural-contract]] and [[tag-taxonomy]]: [[tag-taxonomy]] governs which tags are valid; [[structural-contract]] governs the file envelope; this doc governs what each filing boundary adds on top.

**Authority:** derived from `/wiki-intake`, `Projects/Router/router-spec.md`, `/session-closeout`, and — for §§4–5 — the ingress design. The `sources` token vocabulary is defined once in [[structural-contract]] › Provenance and referenced here, not redefined. New decisions are marked **[new]**.

---

## Scope — filing handoffs only

The spike brief identified six handoff points; the ingress design added the two capture surfaces **[new]**. Four produce a knowledge-layer file and therefore have a *structural* contract:

| Handoff | Produces a file? | Covered |
|---|---|---|
| Wiki intake | Yes | Here — §1 |
| Project knowledge filing | Yes | Here — §2 |
| Session capture (`/capture` + closeout query-and-file) | Yes | Here — §4 (absorbs §3) |
| Automated multi-destination capture | Yes — `durable-knowledge` + `meeting-log` kinds only | Here — §5 |
| Cross-project reference | No — a link between existing files | Link-integrity lint rule (lint surface spec) |
| Context loading | No — the read direction | Tracked separately (retrieval reflex) |
| Memory ↔ vault | No — a scope boundary | Tracked separately (associative persistence) |

Non-file dispositions of the two capture surfaces are not filing handoffs and are contracted elsewhere: queue items (`Wiki/Queue/` — transient judgment artifacts, deliberately outside the [[structural-contract]] Location Gate) and the full kind → disposition matrix live in the ingress design; personal-action appends are owned by `router-spec.md`; Linear creation follows `linear-discipline`.

Session closeout also updates project `CLAUDE.md` — not a filing handoff (`CLAUDE.md` is `type/claude-project`, outside [[structural-contract]] scope). Only the query-and-file half is a filing handoff (§4).

---

## Shared shape

Every filing-handoff contract is the same fields:

| Field | Meaning |
|---|---|
| **Base** | [[structural-contract]] — the envelope. Always applies. Not restated below. |
| **Destination** | Where the file lands; selects the [[structural-contract]] destination modifier |
| **Enforcer** | The skill/spec that implements the handoff |
| **Pre-file gate** | Judgment check(s) before filing, each with an explicit pass/fail decision rule |
| **Field derivation** | How the handoff sets the delta values the envelope requires (`sources`, `area/`/`project/`, `topic/`) |
| **Post-file** | Obligations after the file lands (index sync, cross-references) |
| **Validation** | Where the contract is checked. *Today* = what the enforcer verifies now. *Target* = filing-time envelope validation; the mechanism is specified by the lint surface spec (criterion 4) and is not yet built. *Periodic* = lint. |

**Every filing handoff produces the full envelope.** Base = [[structural-contract]]: every filed file must satisfy the complete Invariant Core plus the destination modifier. The per-§ *Field derivation* below lists only fields whose *value* is handoff-specific — fields not listed still apply (a freshly-filed page takes `status/active`; `updated` = today). The pre-existing enforcers' frontmatter schemas predate the structural contract and are incomplete; reconciling an enforcer means raising its schema to the full envelope, not preserving its partial one:

| Enforcer | Frontmatter fields it currently omits vs. the envelope |
|---|---|
| `/wiki-intake` | none — already applies `type/` / `area/` / `topic/` / `status/` / `updated` / `sources` |
| `router-spec.md` Knowledge Delivery | `status/`, `sources` |
| `/knowledge-layer` query-and-file (closeout Step 9) | recorded against the earlier Step 6b enforcer: `status/`, `sources`; Wiki-hosted branch also `area/`, `topic/` — re-verify at reconciliation |

This table is frontmatter-scoped; the single-H1 body rule applies via the envelope and has no enforcer conflict today. This is the schema-*completion* half of reconciliation; the §-level **De-scoping** clauses are the other half — behavior an enforcer must stop doing.

---

## §1 — Wiki intake

Content (router-delivered or pasted) → `{workspace_root}/Wiki/Knowledge/`.

This contract covers the **filing branch** of wiki intake only. `/wiki-intake` first classifies capture intent — `knowledge` / `data-correction` / `explore` / `triage` — and only `knowledge` intent reaches a filing decision. `data-correction` mutates existing files; `explore` and `triage` create `Wiki/Queue/` items (`queue-kind: disposition` — the two-kind enum {`disposition`, `proposal`}, canonical at `Wiki/CLAUDE.md` § Self-Management, held "until reality demands more"; `Wiki/backlog.json` frozen). Those branches are wiki-intake's internal routing — upstream of, and outside, this filing contract.

- **Destination:** `{workspace_root}/Wiki/Knowledge/{area}-{slug}.md` — Wiki-hosted modifier (`area/` scope tag, `topic/` required, tags-as-index).
- **Enforcer:** `/wiki-intake`.
- **Pre-file gate — coherence gate** (applies to `knowledge`-intent captures only). Four criteria: self-contained, clear topic, additive, single-question-scoped. These are handoff-layer *judgment* gates, not envelope rules — `single-question-scoped` is content architecture, which [[structural-contract]] deliberately omits from the envelope; the gate may use it as a filing judgment though lint does not enforce it structurally. **Decision rule:** all four pass → file to `{workspace_root}/Wiki/Knowledge/`; any fail → a `Wiki/Queue/` item, `queue-kind: disposition` (two-kind enum, canonical at `Wiki/CLAUDE.md` § Self-Management; `Wiki/backlog.json` frozen). (A capture with no real content yet is classified `explore` at intent classification and never reaches this gate.)
- **De-scoping (size heuristic):** `/wiki-intake` currently *halts* when a Knowledge/ file would exceed 150 lines after append. [[structural-contract]] classifies the 150-line threshold as a lint **INFO heuristic, not a contract rule** (Body & Content Architecture; the `Wiki/CLAUDE.md` 150-line health metric is "Pending — conflict"). This contract does not make 150 lines a filing block — the coherence gate decides filing; size is flagged by lint, not enforced here. Reconciling `/wiki-intake` must downgrade the 150-line Halt to an advisory flag.
- **Field derivation:** `area/` = authoritative classification (load the domain context page + [[tag-taxonomy]]); `topic/` = collapse-bias (prefer an existing topic over a near-synonym); `sources` = capture origin, from the [[structural-contract]] › Provenance vocabulary (`inbox-capture`, a URL, or `user-stated`).
- **Post-file:** no index step (Wiki is tags-as-index). Duplicate scan — append-bias means co-existence is acceptable; report overlap, do not block.
- **Validation:** *Today* — `/wiki-intake` Step 3 runs a *post-filing* tag check. *Target* — filing-time envelope validation (mechanism per criterion 4; **[new]**, not yet built). *Periodic* — lint.

## §2 — Project knowledge filing

Content (router-delivered or session-produced) → a project's Knowledge layer.

- **Destination:** `Projects/{name}/Knowledge/{slug}.md`, or `{workspace_root}/System/Knowledge/` / `System/` root (System is a project) — project-hosted modifier (`project/` scope tag, `index.md` entry required).
- **Enforcer:** `router-spec.md` "Knowledge Delivery Rules" (Router-driven) today; the target architecture specifies a dedicated project intake skill as the future enforcer (`routing-architecture.md`) — **[new]**, not yet built.
- **Pre-file gate — opt-in + candidacy.** The destination project must declare a `### Knowledge` Intake subsection (opt-in), AND the content must be a Knowledge candidate per `router-spec.md` Knowledge Axis Classification. **Decision rule:** both true → file; `### Knowledge` absent → Task-axis only; not a Knowledge candidate → no Knowledge-axis delivery. The gatekeeper's destination resolution honors this gate on every project-hosted resolution — the `### Knowledge` declaration is a mechanical check; absent → a `Wiki/Queue/` item proposing the declaration, never a file (§§4–5 inherit this).
- **De-scoping (D1):** the §2 enforcer MUST NOT write a `## Original Capture` body section. Two current specs mandate it — `router-spec.md`'s "Knowledge Delivery Rules" ("non-negotiable") and `intake-defaults.md`'s Knowledge-file body shape; the §2 enforcer reads `intake-defaults.md` at runtime, so **both** must be de-scoped. Both mandates are **superseded** by [[structural-contract]] D1 — provenance is `sources` frontmatter. Reconciling the enforcer must actively remove the section from both, not retain it.
- **Field derivation:** `project/` = the destination project; `sources` = capture origin, [[structural-contract]] › Provenance vocabulary; the project's `### Knowledge` declaration may extend the per-type schema — read it at runtime and conform.
- **Post-file:** append and sync the `index.md` entry; on dual-axis captures, cross-reference (`backlog-item` ↔ `context_doc`).
- **Validation:** *Today* — none (router-spec Knowledge Delivery Rules has no contract check). *Target* — filing-time envelope validation (mechanism per criterion 4; **[new]**, not yet built). *Periodic* — lint (envelope + `index.md` entry exists).

## §3 — Session-closeout query-and-file *(superseded)*

Superseded by §4. Session-boundary query-and-file is one of §4's two entry points; §3's durable-synthesis gate and field derivation are folded into §4. The `Step 6b` enforcer designation was a fossil from an earlier reconciliation — the current enforcer is `/knowledge-layer` query-and-file, invoked by `/session-closeout` Step 9.

## §4 — Session capture

Knowledge produced during a live session (operator present) → `{Project}/Knowledge/` or `{workspace_root}/Wiki/Knowledge/`. Two entry points, one machinery — `/capture` mid-session; query-and-file at the session boundary. Absorbs §3 **[new]**.

- **Destination:** the host project's Knowledge layer, or `{workspace_root}/Wiki/Knowledge/` — destination modifier per where it lands. Destination resolution and operator override per the ingress design; project-hosted resolutions honor §2's opt-in gate.
- **Enforcer:** `/capture` (mid-session) and `/knowledge-layer` query-and-file invoked by `/session-closeout` Step 9 (boundary). Both emit candidates through the knowledge-integration gatekeeper; neither routes candidates itself.
- **Pre-file gate — coherence at interactive thresholds.** Candidate identification at the boundary keeps §3's durable-synthesis question: did the session produce synthesis (findings, methodology, decisions, validated patterns) a future session would need to consult, that would otherwise be lost to chat history? Each candidate passes the four dimensions at interactive thresholds — dimensions, thresholds, and worked examples live in the calibration surface (canonical home; referenced, never restated here). An explicit operator "capture this" pins inclusion. **Decision rule:** pass → file; uncertain → surface as a candidate for the operator to decide; fail unpinned → discard (logged); fail pinned → a `Wiki/Queue/` item, `queue-kind: disposition`, with note — never silent discard.
- **Field derivation:** per the ingress design's canonical homes — this § holds envelope + derivation only. `sources` = the session, from the [[structural-contract]] › Provenance vocabulary (`AI research YYYY-MM-DD`; `user-stated` for user-provided facts); `project/` or `area/` per host destination; on the Wiki-hosted branch also `topic/` ≥1 (Wiki-hosted modifier). Enforcer schemas must produce the full envelope (enforcer-gap table above).
- **Post-file:** `index.md` sync on project-hosted filings; `updated` bump on touched pages; the capture report lists filed / queued / discarded with reasons.
- **Validation:** *Today* — filing-validator PASS per filed page (interactive mode may file-then-fix, cap 3) — this handoff ships with the filing-time envelope validation §§1–2 still list as *Target*. *Periodic* — lint.

## §5 — Automated capture

Typed candidates from the unattended capture lane (Pi) → knowledge-layer files, no operator in the loop. Only two kinds produce files — `durable-knowledge` and `meeting-log`; the full kind → disposition matrix is defined in the ingress design (the automated column is the complete automated write authority). Every other disposition queues or discards — outside this contract (Scope table above) **[new]**.

- **Destination:** `durable-knowledge` → project `Knowledge/` or `{workspace_root}/Wiki/Knowledge/` by scope, only on destination resolution = resolved-unique (resolved-multiple / unresolved → queue); `meeting-log` → the registered meeting's per-area rolling log (`type/meeting-capture` — outside [[structural-contract]]'s Type Gate; the registered playbook owns its shape). Project-hosted resolutions honor §2's opt-in gate (mechanical check; declaration absent → queue proposal, never a file).
- **Enforcer:** knowledge-integration, automated mode — router + gatekeeper for all candidate disposition.
- **Pre-file gate — pre-commit write-plan validation.** The gatekeeper emits a write plan (new files: full composed content + enumerated content sources; existing targets: `{target, pre_state_hash, append_suffix}` only — whole-file overwrite structurally impossible); critic rubric v2 validates the plan + composed artifacts before any vault write; apply is a deterministic script, not a model. **Decision rule:** PASS → apply; FAIL → nothing commits, plan + reasons → quarantine queue item, heartbeat suppressed.
- **Field derivation:** per the ingress design's canonical homes. Attribution is mandatory on every automated write **[new]**: `sources` carries `routine/<action> <run-id>` ([[structural-contract]] › Provenance) plus the human-readable source attribution (e.g. `Canopy Triad Sync 2026-05-28`); scope tag (`project/` or `area/`) per resolution; `topic/` ≥1 on Wiki-hosted `durable-knowledge`.
- **Post-file:** post-apply verify — filing-validator on new files; suffix-presence check on appends; FAIL → quarantine queue item (file + expected-vs-found), heartbeat suppressed, no further writes this run — never silent, no auto-revert. `index.md` sync on project-hosted filings. Queue fallback is mandatory: every candidate ends as exactly one of filed / `Wiki/Queue/` item / logged discard.
- **Validation:** *Today* — the pre-commit critic gate + post-apply filing-validator (this lane ships filing-time validation; §§1–2's *Target* mechanism remains pending for their enforcers). *Periodic* — lint.

---

## Downstream Consumers

| Skill / spec | Implements | Status |
|---|---|---|
| `/wiki-intake` | §1 — must satisfy this contract on the `knowledge`-intent filing branch | Pending — reconcile to §1 |
| `router-spec.md` Knowledge Delivery Rules | §2 — Router-driven project filing; must drop the superseded `## Original Capture` mandate ([[structural-contract]] D1, §2 De-scoping) | Pending — reconcile |
| project intake skill | §2 — target architecture; not yet built (`routing-architecture.md`) | Not built |
| `/knowledge-layer` query-and-file (via `/session-closeout` Step 9) | §4 — session capture, boundary entry point | Pending — reconcile to §4 |
| `/capture` | §4 — session capture, mid-session entry point | Pending — not yet built |
| knowledge-integration (automated mode) | §5 — automated capture; gatekeeper for all candidate disposition | Pending — reconcile to §5 |

A `references.handoff_contracts` config key should be added to global CLAUDE.md alongside `references.structural_contract`.
