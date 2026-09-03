---
name: maintenance-triage
description: >-
  Judgment pass of the Pi maintenance lane. Reads the staged lint findings JSON,
  runs the delta-scoped contradiction scan (knowledge-contract Part IV judgment pass), derives
  each finding's decisive action, and splits the results: deterministic envelope
  fixes become a fix plan for the gated model-free apply pass; genuinely-stuck
  judgments become Wiki/Queue/ items. When staging also carries pending Inbox/
  captures, classifies each per the Router taxonomy and asks one Wiki/Queue/
  question per item — queue-only, zero deliveries. Writes NOTHING outside
  Wiki/Queue/.
argument-hint:
  - (no argument — reads findings JSON from /tmp/pi-cc-staging/)
context: fork
allowed-tools:
  - Read
  - 'Bash(date:*)'
  - 'Bash(sha256sum:*)'
  - mcp__obsidian__read_note
  - mcp__obsidian__read_multiple_notes
  - mcp__obsidian__search_notes
  - mcp__obsidian__get_frontmatter
  - mcp__obsidian__get_notes_info
  - mcp__obsidian__list_directory
  - mcp__obsidian__write_note
---

# /maintenance-triage — Maintenance Lane Judgment Pass

## Identity

The model half of the maintenance lane's two-pass design: Pass 1 (`lint.py`)
finds structural drift across the vault for ~$0, but its findings are a JSON
file nobody reads, and exactly one lint check is genuine judgment (the
contradiction scan). This skill owns two write-only-to-`Wiki/Queue/` passes
run in one invocation: **findings triage** (every run) and **Inbox capture
triage** (Step 6b — only when staging carries pending `Inbox/` items).

## Intent

**Objective.** This skill splits every finding along one line: **can the
evidence alone decide the fix?**

- **Auto-fixable** — the decisive action is a deterministic envelope patch
  whose value the evidence dictates (a derived status tag, derived sources,
  an exact index line, a link repoint to a found rename). These go into a
  FIX PLAN this skill emits but never applies: the dispatch validates the
  plan against the fix rubric (context-free critic, hard gate) and a
  model-free script applies it (Pass 3). A defect the system knows how to
  fix gets fixed — it never reaches the operator.

  Calibration example: a missing index
  entry where the index's section AND entry format already exist, and the
  doc's placement is unambiguous, IS auto-fixable — the evidence dictates
  the exact line. Queue it only when the placement itself needs judgment
  (no matching section, competing sections, or the doc's index-worthiness
  is the question). Over-classifying mechanical adds as judgment wastes
  operator attention — the failure the auto-fix split exists to prevent.
- **Stuck** — the evidence doesn't decide it (contradictions, genuinely
  ambiguous status, unfindable link targets, taxonomy proposals, anything
  touching what content MEANS). These become operator-adjudicable
  `Wiki/Queue/` items — this skill's ONLY write surface.

**Constraints.**
- **Hard: queue-only write wall.** The write surface is `Wiki/Queue/`
  only — one new `.md` item file per stuck judgment, via
  `mcp__obsidian__write_note` (create); never modify, resolve, or expire an
  existing item; never touch any other vault path. The container mounts the
  vault read-only with a single writable mount at `Wiki/Queue/` — but that
  mount is the backstop, not the control: attempting a write elsewhere at
  all means the skill's own discipline already failed. The vault outside
  `Wiki/Queue/` is byte-identical before and after every run of this skill —
  mutations happen only in Pass 3, after the fix-rubric gate.
- **Hard: shared item cap.** Max 10 new detailed items per run, shared
  across findings-derived items and Inbox-derived items (Step 6b) — one
  budget, not two. Per-branch overflow handling is in each playbook.
- **Steering: plain-language, self-contained items.** A stuck item's body
  speaks content, not mechanics — no lint check names, severities, tag
  paths, or vault jargon in the ask; mechanics live in the frontmatter plus
  one footnote line. Every item must pass the 3-weeks-later test:
  adjudicable from the file alone, with zero session context, without
  knowing what a lint check or a frontmatter tag is. Applies to every
  `Wiki/Queue/` item this skill creates, from either pass.

**Decision authority.** Autonomous: everything within each pass's own
protocol — classification, composition, dedupe/overflow calls
(`findings-triage.md`); classifying an Inbox item and drafting its proposed
destination, never executing it (`inbox-triage.md`). Escalate — by filing a
queue item, the only escalation path: any judgment the evidence can't
close, and every Inbox item's actual routing decision. This skill never
adjudicates meaning and never mutates anything outside `Wiki/Queue/`.

## Stop Rules

- **A declared FAIL is a loud FAIL.** Any stop rule below that reports `FAIL`
  must surface it as the sentinel: your FINAL output's first line must begin
  `FAIL:` — the dispatcher greps the pass log for that sentinel and withholds
  the heartbeat; a FAIL declared anywhere later in prose but not as the
  first-line sentinel may be missed. A degraded run whose output carries no
  sentinel fires the heartbeat and buries the failure. Suppressed heartbeat IS the alarm; never soften it.
- **Tool substrate unavailable** (obsidian MCP tools not connected, or vault
  visibility narrower than the expected mount) → report
  `FAIL: substrate degraded` (first-line sentinel) naming what's missing, and
  stop. Do NOT fall back to partial checks and report success.
- **Staging missing or unparseable** (`/tmp/pi-cc-staging/delivered-content.json`
  absent, or not a JSON object with `findings` + `delta` + `summary`) → report
  `FAIL: no staged findings` and stop. Zero writes, zero plan.
- **First `write_note` to `Wiki/Queue/` fails** → report `FAIL` with the
  attempted path and error, and stop. Never retry into another location; a
  failing queue write means the lane's substrate is broken, and the suppressed
  heartbeat is the alarm.
- **Read-back verification fails** (created item's frontmatter missing
  `status: pending`) → report `FAIL`; do not continue creating items.
- **Classification is uncertain** for a specific finding → that finding is
  stuck. Uncertainty is never resolved toward the plan.
- **Delta set empty AND no HIGH/MEDIUM findings** → report `no-op` and stop
  cleanly (the dispatcher normally gates this run out; if invoked anyway, do
  nothing loudly).

## Navigation

| Pass | Fires when | Playbook |
|---|---|---|
| **Findings triage** | Every invocation (Steps 1–7, incl. the final report) | `playbooks/findings-triage.md` |
| **Inbox capture triage** | Staging carries non-empty `inbox_items[]` (Step 6b, between Steps 6 and 7) | `playbooks/inbox-triage.md` |

Both passes share the Stop Rules and write-only-to-`Wiki/Queue/` surface above.

## What this skill does NOT do

- Does NOT apply, stamp, or delete anything — anywhere, ever. Fixes are
  applied by Pass 3's model-free script, only after the fix-rubric critic
  gate passes.
- Does NOT resolve, expire, or edit existing queue items (drain is
  session-tier, operator-present).
- Does NOT read or write the lint manifest/state — that is Pass 1's surface.
- Does NOT create Linear issues (automated lanes never write task systems).

Branch-specific negatives are in each playbook's own "What this playbook
does NOT do."
