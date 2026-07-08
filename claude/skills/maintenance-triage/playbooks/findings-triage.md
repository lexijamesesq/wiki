# Playbook: findings-triage

Steps 1–7 of the maintenance lane's judgment pass — turns Pass 1's staged
lint findings into a fix plan (auto-fixable) and/or `Wiki/Queue/` items
(stuck). Runs on every invocation of this skill. `playbooks/inbox-triage.md`
is the separate, conditional pass (Step 6b) that runs between Steps 6 and 7
when staging carries pending `Inbox/` items — its results fold into this
playbook's Step 7 report.

## Constraints

- **Hard: never apply fixes.** The fix plan is OUTPUT (the last thing in the
  final report), not a write. Application happens only in Pass 3, behind the
  fix-rubric critic gate, by a script with no model in it.
- **Hard: fix-plan ops vocabulary.** Exactly four ops — `add_tag` (one tag
  into the frontmatter `tags` array), `add_field` (one absent frontmatter
  field; `sources` only), `append_line` (one exact line onto an index file),
  `replace_line` (one exact line replaced whole, with ONLY the wikilink
  target changed). Never body-substance edits, never a full or rendered file
  state, never a delete. If a finding classified auto-fixable cannot be
  expressed in these ops, it is stuck — never improvise an op.
- **Hard: fix-plan targets.** Never `Personal/`, `Work/`, `Wiki/Data/`, or
  any `CLAUDE.md` file — findings on those surfaces are always stuck.
- **Hard: every patch carries `pre_state_hash`** (`sha256sum /vault/<target>`
  taken when the target was read) **and a one-line `evidence` entry tracing
  the patched value to the enumerated evidence.**
- **Hard: plan cap — 20 patches per run.** Excess auto-fixable findings
  become ONE `disposition` summary queue item listing the remainder; they get
  planned on a future run.
- **Hard: severity filter.** Only HIGH and MEDIUM mechanical findings, plus
  contradictions from the judgment scan, are processed. WARNING/INFO stay in
  the findings JSON.
- **Hard: item schema** is exactly the shape below (superset of the /queue
  create-item playbook schema; `status: pending` literally — the SessionStart
  debt hook greps that string).
- **Steering: batch per subject.** All stuck findings about one file are ONE
  item — the operator adjudicates subjects, not line numbers. Corpus-level
  findings (no file) use `subject: corpus:<check>`.
- **Steering: overflow.** If more findings subjects qualify than the
  navigator's shared item cap allows, file the 10 highest-severity and ONE
  `disposition` overflow item listing the remaining subjects (unchanged).
  Contradiction scan reads at most 20 delta files, prioritizing `CLAUDE.md`
  files and `Knowledge/` paths; note any truncation in the final report.

## Decision Authority

- **Autonomous:** contradiction identification within the delta scope;
  applying the severity filter; the auto-fixable/stuck classification; patch
  composition within the ops vocabulary; item composition (slug, queue-kind,
  reasons, scope tags, evidence); dedupe skips; overflow selection.
- **Escalate — by filing a queue item (that IS the escalation path):** every
  judgment evidence can't close — which claim wins a contradiction, what an
  ambiguous status should be, whether a dead link should be removed, any
  taxonomy addition, any change to content meaning.

## Protocol

### Step 1 — Load the staged findings

Read `/tmp/pi-cc-staging/delivered-content.json` (the `Read` tool; this path
is outside the vault). Validate shape: `findings[]` (objects with `severity`,
`check`, `file`, `detail`, `suggestion`), `delta{changed[], new[], deleted[]}`,
`summary`. On failure → Stop Rule 1.

The same object may also carry `inbox_items[]` — vault-relative paths to
pending `Inbox/` captures.
Absent or empty is valid — an older dispatcher build or an empty Inbox both
mean Step 6b has nothing to do; `inbox_items` is NOT part of the shape
validation above, only `findings` + `delta` + `summary` gate Stop Rule 1.

Get today's date with `date +%F` (for `created`, item filenames, and the
plan's `created` field).

### Step 2 — Delta-scoped contradiction scan (the judgment pass)

Scope = `delta.changed ∪ delta.new`, `.md` files only, capped at 20
(prioritize `CLAUDE.md` files, then `Knowledge/` paths, then the rest).

Per lint-surface's judgment-pass contract:

1. Read each in-scope file (`mcp__obsidian__read_note`; batch with
   `read_multiple_notes` ≤ 10).
2. Identify its substantive claims (state, decisions, numbers, statuses).
3. Compare against (a) its scope's `CLAUDE.md` Current State and (b) closely
   related knowledge pages found via `search_notes` on the file's topic/tags.
4. **CLAUDE.md widening rule:** if a scope's `CLAUDE.md` is itself in the
   delta set, widen the scan to all of that scope's knowledge files — a
   Current State edit can retroactively contradict unchanged pages.
5. A contradiction is two live claims that cannot both be true (not a
   superseded-and-archived statement, not different scopes). Best-effort
   tier: when unsure whether two claims conflict, they don't.

Each confirmed contradiction → one `disposition` item candidate quoting BOTH
sides with their file paths. Contradictions are ALWAYS stuck — two live
claims are a meaning question, never a patch.

### Step 3 — Filter and classify

From `findings[]`, keep HIGH and MEDIUM. For each finding, derive the ONE
decisive action the evidence supports, then classify it:

| Finding + evidence | Decisive action | Class |
|---|---|---|
| missing `status/*`; archival/supersession signal in the file | `add_tag` `status/archived` (name the signal) | auto-fix |
| missing `status/*`; no archival signal | `add_tag` `status/active` (the contract default) | auto-fix |
| missing `status/*`; signals point both ways | which status is true? | STUCK |
| missing `sources`; value derivable (git-era session refs, `backlog-item`, doc content) | `add_field` `sources` with the derived value | auto-fix |
| missing `sources`; nothing derivable | `add_field` `sources` with `pre-contract` (the contract fallback) | auto-fix |
| broken wikilink; target search finds exactly ONE rename | `replace_line` repointing `[[old]]` → `[[found]]` | auto-fix |
| broken wikilink; no findable target, or several candidates | remove it, repoint it, or restore the page? | STUCK |
| missing index entry; the exact line is derivable | `append_line` with the ready-to-paste line | auto-fix |
| contradiction (Step 2) | which claim wins? | STUCK (disposition) |
| taxonomy proposal, new tag value, consolidation, anything touching content meaning | — | STUCK |

The table's principle: **metadata the evidence dictates gets fixed; meaning
gets asked.** A fix whose value required weighing, guessing, or preference is
not auto-fixable no matter how small the edit. Group stuck findings by
subject (Constraints); auto-fixable findings stay per-patch.

### Step 4 — Compose the fix plan

For each auto-fixable finding, in severity order, up to 20 patches:

1. Hash the target: `sha256sum /vault/<target>` (the plan carries the
   vault-relative path; the `/vault/` prefix is only for the hash command).
2. Compose the patch in the ops vocabulary, with a one-line `evidence` entry
   naming the finding and the signal that dictates the value.

Auto-fixable findings beyond the 20-patch cap → ONE `disposition` summary queue
item listing subject + intended fix per line, in plain language, so nothing
drops silently.

Plan shape (emitted in Step 7; `value` is always a list for `add_field`):

```json
{
  "fix_plan": {
    "version": 1,
    "created": "YYYY-MM-DD",
    "patches": [
      { "target": "System/Knowledge/example.md",
        "pre_state_hash": "<64-char sha256 hex>",
        "op": "add_tag", "tag": "status/archived",
        "evidence": "missing-status finding; body says 'superseded by v2 design'" },
      { "target": "Wiki/Knowledge/other-example.md",
        "pre_state_hash": "<64-char sha256 hex>",
        "op": "add_field", "field": "sources", "value": ["backlog-item TICKET-123"],
        "evidence": "missing-sources finding; doc header cites TICKET-123" },
      { "target": "System/index.md",
        "pre_state_hash": "<64-char sha256 hex>",
        "op": "append_line", "line": "- [[new-doc]] — one-line description",
        "evidence": "missing-index-entry finding for new-doc.md" },
      { "target": "System/Knowledge/referrer.md",
        "pre_state_hash": "<64-char sha256 hex>",
        "op": "replace_line",
        "old_line": "See [[old-name]] for the containment model.",
        "new_line": "See [[new-name]] for the containment model.",
        "evidence": "broken-link finding; search finds exactly one rename → new-name.md" }
    ]
  }
}
```

### Step 5 — Dedupe stuck candidates against pending items

List `Wiki/Queue/` (`list_directory`). For each stuck candidate, check
existing items (frontmatter via `get_frontmatter`, or `search_notes` scoped
to `Wiki/Queue/`): an item with `source: maintenance-lane`, the same
`subject`, and `status: pending` already exists → SKIP the candidate (count
it as deduped in the report). Resolved/expired items do not block re-filing.
Fix-plan patches are not deduped against queue items — a pending item about
a subject does not block fixing a different, evidence-decided defect on it.

### Step 6 — Create stuck queue items

Apply the caps (Constraints). For each surviving stuck candidate, write
`Wiki/Queue/{YYYY-MM-DD}-{queue-kind}-{slug}.md` (slug: 3–6 lowercase
hyphenated words naming the subject topic, not the lane; on filename
collision append `-2`, `-3`, …):

```markdown
---
queue-kind: disposition
source: maintenance-lane
proposed_action: <ONE decisive imperative, executable exactly as written>
reasons:
  - <why evidence can't close this, one line per reason>
created: 'YYYY-MM-DD'
status: pending
subject: <vault-relative path, or corpus:<check>>
checks:
  - <lint check name(s), or contradiction-scan>
tags:
  - <project/* or area/* scope tag derived from the subject's location/domain>
---

# <Title naming the judgment, in content language>

**What this is:** <the page/topic in plain content language — what it says,
what it is for>
**Why it's stuck:** <the specific fork evidence can't close — the ways it
could go, and what's missing to pick one>
**What your answer causes:** <the concrete effect of deciding — what gets
changed, kept, or removed once you pick>

## Evidence

<Quotes and search results, in the content's own words — enough to
adjudicate with zero session context.>

*Mechanics: <check name(s), severity, exact path(s) — one line.>*
```

The three-part ask is the body's contract: a reader who has never heard of
lint, frontmatter, or tags can adjudicate the item. Every mechanical detail
(check names, severities, paths) lives in the frontmatter and the single
italic footnote line — never in the ask itself.

**`proposed_action` is mandatory and must be decisive.** One imperative the
operator can approve as-written — never a menu. For a stuck item this is the
best-supported branch of the fork, stated with its evidence; the body's
"why it's stuck" names what keeps it from being auto-fixable. For contradiction
items: propose which claim wins WITH the evidence — the operator confirms,
never reconstructs. If no branch is better-supported, use
`proposed_action: INVESTIGATE — <what's missing>` (rare; a fork is not an
excuse to skip the analysis). List genuine alternatives under an
`## Alternatives` body section (fallbacks, not a decision menu).

`queue-kind`: `disposition` for every item this lane creates from Pass 1
findings — mechanical-finding, contradiction, and overflow/summary items
alike (the collapsed 2-kind enum folds the former `conflict`/`triage` kinds
into `disposition`). Inbox items (Step 6b) may additionally use `proposal` —
a different fork, not a change to this rule. `subject` and `checks` extend
the /queue playbook schema — they are this lane's dedupe identity; keep them.

After each write, read back the frontmatter and confirm `status: pending`
and `queue-kind` are present (Stop Rule 3 on failure).

### Step 7 — Report, then emit the plan

Print a final plain-text report: delta size (and truncation, if any),
contradictions found, patches planned, stuck items created (paths),
candidates deduped, overflow count, and — when `inbox_items` was non-empty —
Inbox items processed, skipped (dashboard/`routed:`), queued (paths),
deduped, and deferred past the shared cap.

If (and only if) the plan has ≥1 patch, end the response with the single
`fix_plan` JSON object from Step 4 — valid JSON, nothing after it. The
dispatch extracts it by the `fix_plan` key; prose after the object, or a
second JSON object, breaks the handoff. Zero patches → emit no JSON object
at all.

## What this playbook does NOT do

- Does NOT queue auto-fixable defects — the system fixing what it knows how
  to fix is the point of the split.
- Does NOT plan judgment calls — a patch value the evidence doesn't dictate
  belongs in a queue item, however small the edit.
- Does NOT create WARNING/INFO items or re-report full lint output — the
  session-tier `/lint-knowledge` surface owns those; item count per run
  stays small (cap above).
