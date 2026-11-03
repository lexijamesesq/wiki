# Playbook: assess-candidates

Protocol for `assess candidates` and `assess single` (a single candidate is a batch of one). Load `spec/calibration-surface.md` (this plugin's root) before the first candidate — every judgment below (kind definitions, dimensions, thresholds, the disposition matrix, resolution guidance, worked examples) lives there and is referenced, never restated.

## 0. Validate the invocation

- Candidates present? None → halt (stop rule). Do not invent candidates.
- Read `trust` and `mode` per candidate.
  - `mode` missing/undeclared → process that candidate at **automated strictness, queue-only** (no filing, no mutation) and set `undeclared_mode` in report `flags[]` (SKILL.md stop rule; the why lives there).
  - `trust` missing/unknown → treat as `unregistered` — only the literal `registered` grants autonomous filing (hard constraint).
- Resolve run metadata: `run_id` (caller-provided, else `{source-slug}-{YYYY-MM-DD}` via `Bash(date:*)`) and `source`.

## 1. Per candidate — re-grade check

Read `content` against the proposed `kind` (calibration surface §3). Wrong proposal → re-grade; full authority, any kind → any kind.

**Lattice rule (automated mode):** any re-grade INTO durable-knowledge from any other kind → force disposition `queue` with reason `re-grade-forced`, regardless of the new kind's matrix cell. Re-grades among queue-bound kinds, or into `noise`, execute normally. Interactive mode: re-grade freely; the new kind's interactive column governs.

Record `{kind_proposed, kind_final, regrade_forced: bool}` per candidate for the report.

## 2. Per candidate — one vault search

One search pass feeds BOTH routing and assessment:

1. **Scope determination** — verify or derive `scope_hint`: a project (a folder under `{projects_root}`, or `{workspace_root}/System`) or a Wiki area (a `{workspace_root}/Wiki/Contexts/<area>-context.md` page)? Read the candidate project's `description` in its CLAUDE.md frontmatter, or the area's context page. A project scope claim, when one exists, resolves scope (calibration surface §5).
2. **Target search** — existing docs answering the candidate's question. Run the describe tool (`knowledge-description` skill) over the scoped Knowledge folder and read the descriptions; `Grep` that folder's file contents for the candidate's `search_terms`; follow `related` links from the closest hits; check the natural destination's path. Wiki-hosted files are named `<area>-<subject>.md`, so `Glob` `{workspace_root}/Wiki/Knowledge/<area>-*.md` lists an area's files.
3. **Relationship** — per related doc: updates / extends / contradicts / none. Apply calibration surface §5's "dated accretion is not contradiction" distinction.

Retain the evidence (paths, matched queries, quoted lines). It goes into the report and, verbatim, into any queue item.

## 3. Per candidate — coherence

Four dimensions at the mode's threshold (calibration surface §§1–2). Assess pinned candidates too — a pin changes the landing of a fail (queue, not discard), never the assessment.

## 4. Per candidate — disposition

Evaluate ALL applicable conditions and collect ALL reasons — never stop at the first:

- `trust` ≠ registered
- coherence: clear fail (→ noise path) vs doubtful-at-the-bar (automated → **discard, logged with reason** per calibration surface §2 / §0.1 — NOT queue; queue only if §0.3's entry condition is met; interactive → ask)
- contradiction with existing vault content — include BOTH versions in the payload
- destination resolution (durable-knowledge only): resolved-unique / resolved-multiple / unresolved (judgment: calibration surface §5). Mechanical consequence (calibration surface §4 cell + §5): automated files on resolved-unique OR resolved-multiple's defensible best home (note the alternative home in the entry); unresolved → queue only if §0.3, else discard logged (`placement-unresolved`). Interactive: resolved-unique → file; resolved-multiple / unresolved → ask.
- update-mode guard (both modes, before any append to an existing file): Read the destination's `update` frontmatter field (`spec/knowledge-files.md`; integration-modes §3). `append` → continue. `replace` or `never` → disposition `queue`, reason `update-mode-<value>`, never an append. `update` absent → the file breaks the contract; disposition `queue`, reason `update-mode-unset`, never an append. Interactive mode may resolve a `replace` target with the operator instead: they can direct an in-place rewrite, which is a user-initiated action (Interactive override); a `never` target takes a successor file, never a body change. The destination is read here, in this skill, before the write: the calling session never sees the target.
- project-hosted opt-in gate: Read the destination project's CLAUDE.md frontmatter; is `knowledge_intake: true`? Absent or false → the destination re-resolves to the Wiki-hosted domain home (`{workspace_root}/Wiki/Knowledge/`, no opt-in required) and the content files there — calibration surface §5: a missing declaration never black-holes content — AND the declaration proposal queues separately, reason `opt-in-gate-absent` (interactive: the operator may add `knowledge_intake: true` to the project's frontmatter now; re-check, then proceed project-hosted).
- re-grade forced (step 1)
- idempotency (appends): target already contains an entry matching `content_hash` or attribution+date → disposition `discard`, reason `duplicate`
- pinned + coherence-fail → disposition `queue` (queue-kind `disposition`) with a note naming the failed dimensions — never silent discard

Then look up the matrix (calibration surface §4) with `mode × trust × kind_final`. Apply the calibration-surface §4 queue-entry gate to any automated 'queue' cell: §0.3 must hold or the disposition is discard, logged — pinned, quarantine, and within-group-contradiction items always queue. Interactive `ask` / `surface in-conversation` outcomes resolve with the operator to a terminal disposition (file / queue / discard) before the report — `ask` is never terminal.

## 5. Batch — group + within-group contradiction check

Group `file`-disposition candidates by target file. Pairwise-check each group for internal contradictions (incompatible claims about the same fact — calibration surface §5 distinction). On contradiction:

- Interactive → surface both versions to the operator; their decision yields terminal dispositions.
- Automated → remove both from the write plan; ONE `disposition` queue item carrying both candidates + evidence.

Compose one ordered append per surviving target per run (source order, oldest attribution first).

## 6. Queue landings

Every `queue` disposition → `/queue create-item`, one item per queued candidate (within-group conflicts: one item per conflict pair):

| Dominant reason(s) | queue_kind |
| --- | --- |
| `opt-in-gate-absent` (the declaration proposal only — the content itself files to the Wiki-hosted domain home separately and does not wait on the proposal) / proposing a new Data/ record / project-work deferred — INTERACTIVE promotions only; automated project-work discards (task-extraction-unbuilt) | `proposal` |
| everything else — contradiction (vault or within-group), unregistered trust, unresolved or true-tie resolved-multiple meeting §0.3, `update-mode-<value>` / `update-mode-unset`, `re-grade-forced`, pinned coherence-fail, undeclared mode, automated kind-authority deferral (data-mutation / context-shift) — queue ONLY when the calibration-surface §4 queue-entry gate holds (§0.3: critically important AND legitimately stuck); otherwise discard, logged — the source persists upstream | `disposition` |

Pass to create-item: `queue_kind`; `source` = this run's source; `reasons[]` = ALL collected reasons; `scope` from the resolved or hinted scope; evidence = the step-2 search evidence plus attribution + provenance (+ both gradings when re-graded, both versions when conflicting) — all of which lands in the item's `## Mechanics` section, not the ask.

**The payload is a human ask, not a data dump.** This playbook is the only party holding both the candidate and the reasons, so it composes the three parts create-item requires (create-item.md § The human-question test): *what this is* — the candidate's content in plain terms; *why I'm stuck* — the collected reasons translated into the specific fork only the operator can close (e.g. `resolved-multiple` becomes "this could live with your X notes or your Y notes and I can't tell which"; `unregistered trust` becomes "this came from pasted third-party material, so I won't file it as your knowledge without your say-so"); *what your answer changes* — each plausible answer mapped to the disposition it triggers, consequences first. Reason codes, kind names, trust levels, and check ids never appear in the ask. The title handed over is the plain question itself.

An item-write FAIL fails the run loudly (stop rule) — never proceed as if queued.

## 7. Execute — interactive mode

Per `kind_final`; the matrix cells govern, the owners below execute:

| kind_final | Execution |
| --- | --- |
| durable-knowledge | **New file** or **append**: see Filing below. |
| data-mutation | Explicit operator mutation intent (the capture IS a correction statement) → delegate to `/wiki-intake` (data-correction intent — the existing chain owner: Data/ → Knowledge append → Context → Personal/Work). Extraction-inferred → ask/confirm first; confirm → delegate; decline → re-grade or discard per the operator. |
| context-shift | Update the `{workspace_root}/Wiki/Contexts/` domain context page through the `context-page` skill (autonomous; the page is `update: replace`). Never a project CLAUDE.md. |
| personal-action | Append to the existing Personal/Work task section per router-spec's personal-action append format (the format owner). Section absent → queue (`disposition`) — never create the section. |
| project-work | Create the Linear issue per `linear-discipline`'s Integrity on Creation: duplicate check, falsifiable acceptance criteria, relations as Linear relations, project + priority matching the work. |
| noise | Discard, logged in the report. Borderline → ask. |

### Filing (durable-knowledge)

`<lint>` below is `python3 <skills-dir>/knowledge-description/scripts/contract_lint.py`, where `<skills-dir>` is the directory holding this skill's folder.

**New file.**

1. Place it. Project-hosted: `<project>/Knowledge/<Folder>/`, where `<Folder>` is the type folder that fits (`spec/knowledge-files.md` › Structure: `Methods/` how we do things, `Reference/` how a system is built and what is true now, `Research/` findings about the outside world, `Decisions/` choices and their reasoning, `Records/` dated frozen material) or a folder the project added. Wiki-hosted: `{workspace_root}/Wiki/Knowledge/<area>-<subject>.md`, flat, no type folders; `<area>` matches the area's context page name. Kebab-case file names.
2. Compose it: frontmatter with exactly the four fields, then the body.
   - `description` — written per the `knowledge-description` skill: true of this file, specific to it, in the words someone would search with.
   - `update` — `append` for a file that will accrete dated entries, `replace` for one that states what is true now and is rewritten to stay current, `never` for a dated record that must not change.
   - `related` — `[]`, or aliased links `"[[target|short reason]]"` to files the step-2 search found this one directly extends or depends on.
   - `updated` — today, `YYYY-MM-DD`.
   - Body: one `# Title`, the content, and a bottom `## Sources` section (Sources, SKILL.md).
   - No `tags`, `verified`, `integration`, or frontmatter `sources`: those keys are retired.
3. Write it with `Write`, then run `<lint> --cutover <path>`. PASS = exit 0. FAIL → fix each finding, re-run; cap 3; still failing → surface all findings, do not mark complete.

**Append** (only to an `update: append` target; the guard in step 4 has already held):

1. Re-run the idempotency check against a fresh `Read` of the target.
2. With `Edit`, add the entry under its parent heading, or as a new dated section at the end of the body above `## Sources`: date attribution plus `source_attribution`. Existing text stays unchanged.
3. Add the entry's Sources bullets under the existing `## Sources` heading (create the heading at the bottom if absent).
4. Set `updated` to today. Refresh `description` if the entry changes what the file is about (knowledge-description skill).
5. Read the file back to confirm the entry is present, then run `<lint> <path>` (no `--cutover`: a file written before the cutover still carries the retired keys, which only the cutover removes). PASS = exit 0.

## 8. Execute — automated mode

Load `automated-write-plan.md`. Summary of the contract: this skill emits the write plan + queue items + report. No destination write happens in this context — the skill's only direct vault writes in automated mode are `/queue create-item` files.

## 9. Report

Emit the extraction report (schema: SKILL.md › Extraction report). Reconcile before returning:

- every candidate has exactly one terminal disposition;
- `queue_items[]` matches the step-6 writes;
- interactive: also present the human-readable summary — filed (paths + validator verdicts), queued (item paths + reasons), discarded (reasons) — and any `flags[]`.
