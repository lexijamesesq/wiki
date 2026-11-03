---
name: capture
description: >-
  Operator's mid-session capture verb — extracts knowledge candidates from the
  live conversation, classifies them via the ingress calibration surface, and
  hands ALL of them to the gatekeeper (interactive mode; trust per
  source — registered for operator-authored content, unregistered for
  third-party pasted material) for disposition; reports filed/queued/discarded
  with paths and reasons. Also the boundary entry for session-closeout query-and-file via
  "/capture batch". Triggers on "/capture", "capture this", "capture that",
  "capture this decision ...", or a batch delegation from /knowledge-layer
  query-and-file.
argument-hint:
  - "(no argument — sweep the live conversation)"
  - "<what to capture — e.g. 'this decision about X'>"
  - "batch <items>"
allowed-tools:
  - Skill
  - Task
  - 'Bash(date:*)'
  - 'Bash(shasum:*)'
---

# /capture — Session Capture

The operator's verb for pulling knowledge out of a live session before it dies in chat history. Extraction here is source-aware — the source is THIS conversation; routing and gatekeeping belong to gatekeeper, and `/capture` never writes a destination itself. Implements the session-capture contract's mid-session entry point.

## Identity

Discipline rules applied on every invocation:

- **Extract → classify → hand off → relay.** ALL candidates go to `/gatekeeper assess candidates` with `mode: interactive` and per-candidate trust (next rule). No candidate skips the gatekeeper; no direct filing.
- **Trust follows the source, per candidate.** Operator-authored / operator-present session content → `trust: registered`. Third-party material pasted or forwarded into the conversation (a colleague's summary, quoted external text) → `trust: unregistered` — the operator forwarded it; they didn't author the claims (surface-defaults table, calibration surface §4). The gatekeeper surfaces unregistered content in-conversation rather than filing it; a pin still guarantees it is never silently dropped.
- **Runs in the session context — never forked.** The live conversation is the extraction source; a forked context cannot see it.
- **Explicit ask pins.** "Capture this/that/X" pins the pointed-at content into the candidate set (`pinned: true`) regardless of extraction judgment. Pinned + coherence-fail lands in the queue with a note — never silently discarded (the gatekeeper enforces the landing; this skill's job is to mark the pin).
- **The calibration surface supplies the judgment** — kind definitions, dimensions, thresholds: `spec/calibration-surface.md` at this plugin's root (three levels above this file). Kind is a PROPOSAL — the gatekeeper may re-grade.
- **This skill writes no vault file.** When it needs vault context (a project's name, an area's context page) it reads with Read and Grep under the session's own permissions; no file tool is pre-approved here.

## Intent

**Objective.** Sessions produce decisions, findings, corrections, and commitments that exist only in chat history unless captured. Without one operator verb, capture happens ad hoc — inconsistent envelopes, bypassed gatekeeping — or not at all. `/capture` makes mid-session capture one cheap utterance, and guarantees everything it captures crosses the same gatekeeper as every other ingress surface.

**Desired outcomes** (observable):

1. "Capture this" costs the operator one utterance; the skill locates the referent, enriches it to self-containment, and reports the terminal outcome with paths.
2. Zero pinned candidates silently dropped — every explicit ask ends in a reported file or queue landing.
3. Every candidate reaches gatekeeper — zero destination writes originate in this skill.
4. Mid-session capture and closeout query-and-file produce identical envelopes and dispositions — same machinery, two entry points.

**Health metrics — must NOT degrade:**

- Zero direct destination writes from this skill (all vault writes happen inside the gatekeeper's machinery).
- Every explicit ask yields ≥1 pinned candidate or an in-conversation clarification — never a shrug.
- The report accounts for every candidate handed off: filed (paths) / queued (item paths + reasons) / discarded (reasons).
- Contract-violating destination overrides never execute without the rule stated + explicit operator confirmation.

**Strategic context.** One of the two session-tier entry points into the unified ingress machinery: `/capture` mid-session; `/session-closeout` query-and-file at the boundary, which delegates here via **`/capture batch`** (invoked by `/knowledge-layer` query-and-file). The closeout preflight capture scan (the self-aware bonus tier — ONE mechanism, attached to the existing boundary) also flows through `batch`.

**Constraints.**

- **Hard:** `mode: interactive` on every handoff, with trust per the source rule (Identity): `registered` for operator-authored session content, `unregistered` for third-party pasted/forwarded material — never `registered` for claims the operator didn't author. A subagent or background worker invoking this machinery has no human in its loop and MUST declare `mode: automated` instead — the gatekeeper then queues rather than files.
- **Hard:** pinned semantics — an explicit ask pins inclusion; the pin travels on the candidate (`pinned: true`).
- **Hard:** operator destination overrides — contract-legal wins silently; contract-violating gets the violated rule stated in one sentence + explicit confirmation (confirmed = user-initiated action; the constraint system binds autonomous action only). a filing-time lint gate FAIL on a user-chosen destination → fix the envelope, keep the destination — orthogonal concerns.
- **Steering:** enrich to self-containment before handoff — resolve pronouns, name subjects and systems, date the claims; the candidate must survive with zero session context. Don't over-sweep: a pointed "capture this" takes the referent, not the whole conversation.

**Decision authority.**

- **Autonomous:** referent location; context enrichment; kind/scope/search-term proposal (via the calibration surface); `content_hash` computation; handoff; report relay; reconciliation check.
- **Operator:** what "this" means when ambiguous (ask, don't guess); destination overrides; mutation-intent confirmations and other asks relayed from the gatekeeper; whether a broad sweep's unpinned extras get handed off.

**Stop rules.**

- No discernible referent for a pointed ask → ask the operator; never guess, and never sweep the whole session as a fallback for a pointed ask.
- Gatekeeper unavailable → halt and report; NEVER file directly as a fallback — the gatekeeper is the point.
- `batch` invoked with zero items → report nothing-to-do to the caller; not an error.
- The gatekeeper's report fails to account for a handed-off candidate → surface the reconciliation gap; do not report success.

## Navigation

Per invocation, identify the operation and load the matching playbook:

| Operation | Input | Output | Playbook |
| --- | --- | --- | --- |
| `capture` (default) | operator utterance + the live conversation | terminal report: filed / queued / discarded, with paths + reasons | `playbooks/extract.md` |
| `batch` | pre-extracted items (boundary callers: `/knowledge-layer` query-and-file, closeout preflight scan) | same report, returned to the caller | `playbooks/batch.md` |

**Boundary invocation string (for orchestrators): `/capture batch <items>`** — items schema and the query-and-file field mapping live in `playbooks/batch.md`.

## What this skill does NOT do

- Does NOT write destinations, run the filing-time lint gate, create queue items, or execute correction chains — all gatekeeper machinery.
- Does NOT re-implement judgment tables — kind and dimension judgments come from the calibration surface, by reference.
- Does NOT do document intake — standalone document deliveries and Inbox routing are `/wiki-intake`'s and `/router`'s entries. Third-party text pasted INTO the live conversation is in scope when the operator asks to capture it — but it hands off as `trust: unregistered`, never as operator-authored content.
- Does NOT run at session boundaries on its own — closeout invokes `batch`; nothing here auto-fires.

## References

- The ingress design — the session-capture contract (what/how/where/validation), including the pinned + override rules this skill carries to the gatekeeper.
- `../gatekeeper/SKILL.md` — the gatekeeper (candidate schema, disposition machinery). Bundled sibling skill.
- `spec/calibration-surface.md` (this plugin) — canonical judgment tables.
- `/knowledge-layer` query-and-file — the boundary caller that delegates here.
