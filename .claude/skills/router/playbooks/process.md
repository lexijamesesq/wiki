# Playbook: process

Sweep the whole Inbox: classify, match, deliver, delete — every capture, one operator-present session.

## Input

- `today` — ISO date (defaults to system date)
- Operator presence (interactive-only; this playbook has a mandatory approval checkpoint)

## Protocol

### 1. Setup

- Resolve the vault root via the `workspace_root` config key (global CLAUDE.md > Configuration; fallback `VAULT_ROOT` env). Unresolvable → halt (Stop rule).
- Enumerate `Inbox/*.md` (`Glob`). Exclude every a generated view — a file whose body is an Obsidian query block (a `base` or `dataview` code fence), such as the Unprocessed Captures dashboard, and any file carrying a `routed:` frontmatter stamp from a prior run (already delivered; surface it as a retained-delivered leftover instead of re-routing).
- **Zero captures after exclusions → stop silently.** No sweep plan, no summary, no deliveries, no "inbox is empty" chatter.

### 2. Discover destinations (runtime)

Per SKILL.md § Destination resolution. Fresh discovery every run — never a cached map.

### 3. Classify every capture (read-only pass)

For each capture, via `Read`:

1. Read full content including existing frontmatter.
2. Classify per spec § Classification Taxonomy — `professional-strategy | professional-operational | personal | meta` — with confidence (high/medium/low). Spec § Classification Examples calibrates the call.
3. Two-axis evaluation per spec § Knowledge Axis Classification: Task and Knowledge fire independently; both, either, or neither are valid outcomes.
4. Detect specialized routes per spec § Contract Resolution: Slack weekly team update (spec's detection criteria), ad-hoc Slack capture (signal-extraction candidate), `professional-strategy` (Incubator seed).
5. **Coverage check:** search for prior coverage before proposing a new delivery — Linear duplicate check per `linear-discipline` § Integrity on Creation, existing seed filenames per spec § Processing Behavior. A capture requesting a capability or artifact that already exists is a **superseded-candidate**: surfaced with evidence, never silently filed, never silently discarded.

### 4. Present the sweep plan (mandatory checkpoint)

One table: capture | classification (confidence) | axes fired | destination + delivery method | proposed end state (delete / retain / ask). Present to the operator and get approval **before any delivery executes**.

- Operator approves the plan → that approval IS the batch confirmation for the deletions the plan lists.
- Operator may instead request per-file confirmation, amend rows, or pull captures out of the sweep (they stay in the Inbox).
- Rows marked "ask" (superseded-candidates, ambiguous items resolvable in a sentence) are settled during this checkpoint.

### 5. Deliver per capture

Route in this order. Task-side: first match wins. Knowledge axis: evaluated under its own rules, independently.

**a. Specialized routes (spec-owned, pre-architecture — execute per spec, do not restate here):**

- `professional-strategy` → a strategy seed per spec § Seed Creation, conforming to the destination project's intake contract (`{workspace_root}/Projects/<strategy-seed-project>/CLAUDE.md` → Intake `### Notes` → its own reference doc; vault-resident, does not ship in this repo). Exact-duplicate check against existing seed filenames first.
- Slack weekly team update → per-designer activity log entries per spec § Team Activity Log Creation, conforming to the destination project's contract (`{workspace_root}/Projects/<team-activity-project>/team-activity-log-spec.md`; vault-resident, does not ship in this repo).
- Ad-hoc Slack capture → signal extraction per spec § Slack Signal Extraction (clear signal → seed; possible signal → summary flag, no seed); the capture itself then continues down the default path below.

**b. Project-owned (confident project match):**

- **Task axis** → Linear issue per `{workspace_root}/System/Knowledge/Reference/unified-ingress-design.md §14` § Default Delivery: Linear Issue (teamId + Project ID from the destination's `### Tasks`), satisfying `linear-discipline` integrity-on-creation. Captures of 3+ sentences or with structure get a `Context/` doc with `## Original Capture` per the Origin Handoff Contract; a ≤2-sentence capture's description must reproduce it completely.
- **Knowledge axis** → ONLY if the destination's CLAUDE.md frontmatter includes `knowledge_intake: true` (Read the frontmatter; absent or false = opt-out, not oversight; the Task axis still fires independently). Hand it to `/gatekeeper assess candidates` as one candidate: `content` = the full verbatim capture, `kind` = the router's knowledge proposal (default `durable-knowledge`), `scope_hint` = the project name, `provenance` = `inbox-capture <date>` and the source filename, `source_attribution` = `Inbox capture <date> (<filename>)`, `trust: registered`, `mode: interactive`. The gatekeeper places it in the project's type folder, writes `## Sources`, and runs the contract lint. Note the dual-axis cross-reference when both axes fired.

**c. Domain-owned (no project match, identifiable domain via lightweight area identification):**

- **Knowledge axis** → hand it to `/gatekeeper assess candidates` as one candidate: `content` = the full verbatim capture, `kind` = the router's knowledge proposal (default `durable-knowledge`), `scope_hint` = the identified Wiki area, `provenance` = `inbox-capture <date>` and the source filename, `source_attribution` = `Inbox capture <date> (<filename>)`, `trust: registered`, `mode: interactive`. Full stop — the gatekeeper owns everything downstream, including a hand-off to `/wiki-intake`'s data-correction chain when the capture is a fact change. Record the gatekeeper report's outcome for the summary; a reported disposition is the delivery confirmation for this axis.
- **Task axis** → append to the domain page's existing task section (`Personal/{Domain Title Case}.md` or `Work/{Domain Title Case}.md`) per spec § Domain Destinations (Task axis): auto-id checklist item via `Edit`, verbatim-overflow rules per the Origin Handoff Contract. Page or task section absent → ask the operator; never create pages or sections.

**d. No home / ambiguous / needs deferred judgment** → ask at the checkpoint. If the operator can't settle it now, the capture stays in the Inbox, unstamped, and the summary lists it with the candidate destinations considered and what was missing. The Inbox is its holding place; nothing is copied elsewhere.

**e. Superseded-candidate** → present the evidence (the existing skill/doc/ticket) at the checkpoint; the operator chooses: **discard** (delete, logged in the summary as an explicit operator discard), **leave** (stays in the Inbox), or **deliver anyway**. Never auto-discard.

### 6. Verify provenance, then delete

Per delivered capture, verify per route before deletion:

| Route | Provenance check |
| --- | --- |
| Incubator seed / signal seed | `## Original Capture` section present, verbatim |
| Linear issue | Description reproduces a ≤2-sentence capture, OR context doc with `## Original Capture` exists |
| Gatekeeper delivery | the gatekeeper report gives the capture a disposition; a filed file has a `## Sources` entry naming the capture and a lint PASS |
| Domain-page task append | Checklist item present; verbatim overflow handled per contract |
| Team activity logs | Per-designer entries created; W: content verbatim |

Then delete with Bash `rm` on the file's absolute path, under the confirmation mode established at the checkpoint (approved plan = batch; otherwise per-file). Declined confirmation or failed verification → the file stays; stamp additive `routed: <destination> (<date>)` frontmatter with `Edit` (body untouched) and record the retained-delivered state in the summary.

### 7. Session summary

Emit per spec § Output Schema: per-item YAML records plus the session summary (classified items, delivery summary, needs-review, duplicates detected, signals extracted, possible signals, statistics, and items remaining in the Inbox with the reason each remains).

## Discipline

- **Zero silent drops.** Every enumerated capture ends the run as exactly one of: delivered artifact, or explicit halt-and-ask recorded in the summary (the capture stays in the Inbox). Discards exist but only as logged operator decisions.
- **Ask vs leave:** halt-and-ask is for ambiguity the present operator can resolve in a sentence; captures needing a design conversation, missing structure, or future judgment stay in the Inbox and are listed in the summary.
- **No delivery before the checkpoint.** Classification is read-only; nothing mutates until the operator has seen the plan.
- **One disposition per capture** (plus independently-fired Task/Knowledge axes, cross-referenced when both land).
- **Failures are loud.** A failed delivery or failed verification is reported per capture — never papered over by proceeding to deletion.

## What this playbook does NOT do

- Does NOT decide knowledge placement, intent, or handler questions — delivery to the gatekeeper ends the Router's knowledge-axis responsibility.
- Does NOT process the `Unprocessed Captures` dashboard or any other generated view.
- Does NOT create destination structure, develop content, or consolidate related captures.
