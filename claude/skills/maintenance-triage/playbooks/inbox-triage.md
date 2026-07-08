# Playbook: inbox-triage

Step 6b of the maintenance lane. Runs between `findings-triage.md`'s Step 6
and Step 7 (see that playbook for Steps 1–7) — its results fold into that
Step 7 report. See the Protocol section below for the trigger condition and
scope.

## Constraints

- **Hard: `Inbox/` items are read-only source material.** Read via
  `mcp__obsidian__read_note`; never write, tag, stamp, move, or delete an
  `Inbox/` file from this lane. The item's only output is its `Wiki/Queue/`
  question — the source file stays byte-identical, same as every other
  vault path outside `Wiki/Queue/` (navigator's queue-only write wall).

## Decision Authority

- **Autonomous:** classifying an Inbox item per the Router taxonomy and
  drafting its proposed destination for the ask — drafting the proposal is
  autonomous, executing it never is.
- **Escalate — by filing a queue item (that IS the escalation path):** every
  Inbox item's actual routing decision — this skill only asks, and the
  operator (or a future interactive session) is the sole executor of any
  destination it names.

## Protocol

### Step 6b — Inbox capture triage

Runs only when the staged JSON carries a non-empty `inbox_items[]` (Step 1).
This step never touches Pass 1's findings machinery, the contradiction scan,
or the fix plan — it is a second, independent triage over a different input,
sharing only the queue-write surface and the run's item cap.

1. For each path in `inbox_items`, in order:
   a. **Read the item** (`mcp__obsidian__read_note`).
   b. **Skip silently** if it carries a `routed:` frontmatter stamp or a
      `type/dashboard` tag — defense in depth; the dispatcher's own cheap
      grep already excludes dashboards, but the staged list may be minutes
      stale by the time this step runs. Skipped items are neither counted
      nor reported as stuck.
   c. **Classify per the Router taxonomy** at `Projects/Router/router-spec.md`
      (`mcp__obsidian__read_note` by path) — cross-reference its
      classification categories and Knowledge-axis rules; never restate them
      here. Derive the single most plausible destination and confidence
      exactly as the Router itself would, but perform NONE of the Router's
      delivery steps (seed creation, activity-log split, backlog append,
      Wiki filing) — this step only asks.
   d. **Coverage check.** List `Wiki/Queue/` (`list_directory`); for each
      candidate, check existing items (`get_frontmatter`, or `search_notes`
      scoped to `Wiki/Queue/`) for one with `source: maintenance-inbox`, the
      same `subject` (the item's vault path), and `status: pending` — same
      dedupe discipline as Step 5. A match → SKIP (count as deduped).
   e. **Compose exactly one queue item** per surviving candidate, per the
      `/queue create-item` playbook contract in full — charter gate: this is
      always a vault-knowledge routing question, never a task; context
      floor: "What this is" must quote or paraphrase enough of the item that
      the operator never has to open `Inbox/` to answer.
      - `queue-kind`: `proposal` when the taxonomy yields one specific
        destination and the only open question is yes/no ("file this to the
        Wiki?"); `disposition` when classification is genuinely ambiguous
        (`needs-review`, multiple plausible categories, or no matching
        project) — the same collapsed two-kind enum as Step 6, a different
        fork.
      - `source: maintenance-inbox` — distinct from `maintenance-lane`
        (reserved for Pass 1 findings); the coverage check in (d) keys off it.
      - `subject`: the item's vault-relative path (e.g. `Inbox/foo.md`).
      - The ask **names the proposed destination in plain language** ("this
        looks like knowledge about your audio setup — file it to the
        Wiki?"), per the human-question test — never a project tag, path, or
        taxonomy label in the title or the three parts.
      - `## Mechanics` carries the **full verbatim capture** (the Origin
        Handoff Contract's provenance requirement, applied to a queue
        question instead of a delivery), the derived classification +
        confidence, and the `subject` path.
   f. **Write** via `mcp__obsidian__write_note` (create mode); read back
      frontmatter to confirm `status: pending` (Stop Rule 3 on failure, same
      as Step 6).
2. **Never touch the Inbox file itself** (Constraints) — no tag, no
   `routed:` stamp, no move, no delete. The interactive Router deletes
   delivered items; this lane never delivers, so it never deletes.
3. **Shared cap.** Inbox items count toward the SAME 10-item run cap as
   stuck findings (Constraints), consumed after findings-derived items are
   counted (this step runs after the findings triage). Once the shared cap
   is reached, stop — remaining Inbox items are silently deferred; their
   source files are untouched, so they reappear in next run's `inbox_items`
   (overflow = next night, no separate Inbox overflow item).

## What this playbook does NOT do

- Does NOT deliver an Inbox item anywhere — no `{workspace_root}/Wiki/Knowledge` filing, no
  Personal/Work append, no Linear issue, no backlog entry. This step only
  asks; it never runs the Router's actual routing/delivery steps.
- Does NOT modify, tag, stamp, move, or delete an `Inbox/` file. The queue
  item this step writes is the only output a capture ever produces from
  this lane.
