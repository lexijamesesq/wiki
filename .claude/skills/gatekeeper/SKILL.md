---
name: gatekeeper
description: >-
  Universal router + gatekeeper for everything entering the vault's knowledge
  layer. Receives typed candidates from any ingress surface (Inbox routing via
  /router, closeout query-and-file, /wiki-intake, or a session invoking it
  directly), resolves each to a
  terminal disposition — file (through a write contract), queue (Wiki/Queue/
  item), or discard (logged) — under the two-axis trust/mode authority model.
  No candidate bypasses it; no extractor writes destinations. Triggers on
  "/gatekeeper assess candidates" or "/gatekeeper assess single".
argument-hint: "assess candidates | assess single"
context: fork
allowed-tools:
  - Task
  - Skill
  - 'Bash(date:*)'
  - 'Bash(shasum:*)'
---

# gatekeeper — Router + Gatekeeper

One judgment pass per candidate: routing and vault-fit are two halves of one judgment — "does this help me help Lexi?" includes "where would it help?". Callers (`/router`, `/knowledge-layer` query-and-file, `/wiki-intake`'s knowledge branch, or a session invoking `/gatekeeper assess single` directly) hand it candidates; this skill disposes of them. Files it writes follow `spec/knowledge-files.md`. Where this skill is silent, the ingress design (`references.intake_defaults` config key) governs.

## Identity

Discipline rules applied on every invocation:

- **Resolve the vault root via the `workspace_root` config key** and project folders via `projects_root` (global CLAUDE.md > Configuration). Never hardcode a vault path.
- **Vault files are read and written with the native tools** — Read, Grep, Glob, Edit, Write — under the session's own permissions. This skill pre-approves none of them: a public plugin cannot name the vault's path, and a bare grant would reach every file on the machine. Its file reach is therefore the session's, never wider. It never moves or deletes a file.
- **The caller declares `trust` and `mode`, always.** Trust is a source property; mode is an invocation property. This skill never decides its own mode.
- **The calibration surface is the canonical judgment home.** `spec/calibration-surface.md` at this plugin's root (`../../../spec/` from this skill's folder) holds the kind definitions, the four dimensions + thresholds, the full disposition matrix, destination-resolution guidance, and worked examples. Load it on every invocation; reference its tables, never restate them.
- **The file contract is `spec/knowledge-files.md`**, beside it: four frontmatter fields (`description`, `update`, `related`, `updated`), three update modes, the type folders. Every file this skill creates or appends to is held to it.
- **One vault search feeds routing AND assessment** — never two passes.
- **Per-candidate accounting.** The gatekeeper never splits a candidate (multi-kind duplication happens at extraction only, with shared provenance); every candidate ends with exactly one terminal disposition.

## Intent

**Objective.** Noise has negative value — bad entries degrade search, dilute context windows, and make future answers less reliable; misrouted entries are buried where no future query finds them. Every ingress surface produces candidates; without one gatekeeper owning both routing and vault-fit, each surface re-invents partial judgment and automated callers accrete write authority nobody audited. This skill is the single point where candidates become vault state: file, queue, or discard — nothing else, no exceptions.

**Desired outcomes** (observable):

1. Every candidate gets exactly one terminal disposition — file / queue / discard — no silent drops, no unaccounted candidates.
2. Filed content is findable in its first session from its `description` and its folder, and passes the contract lint.
3. The automated write surface stays deliberately narrow: Knowledge-layer appends/creates + `Wiki/Queue/` items — nothing else, ever.
4. Every queued candidate is one self-contained adjudication package carrying ALL applicable reasons plus search evidence — no evidence loss to branch ordering.
5. Every run emits the machine-readable extraction report — the audit artifact and the interface callers reconcile against.

**Health metrics — must NOT degrade:**

- Zero automated-mode edits to existing substance (appends/creates only; edits are human-approved, ever — surfacing a conflict is not approval).
- Zero filings from any trust value other than `registered` (missing or unknown trust ≠ registered).
- Zero pinned candidates silently discarded.
- Zero double-appends — the idempotency check (`content_hash` / attribution+date) runs before every append.
- Zero appends to a file whose `update` is not `append`.
- Zero files created without the four contract fields and a `## Sources` section.
- Report reconciliation: `dispositions[]` covers every candidate; `queue_items[]` count matches actual queue writes.

**Strategic context.** The universal gatekeeper of the ingress design — router AND gatekeeper, one skill. Consumers: `/knowledge-layer` query-and-file (closeout synthesis), the interactive `/router` (Inbox captures), `/wiki-intake` (knowledge-intent branch), and a session that invokes `/gatekeeper assess single` directly to file something mid-session — there is no separate capture verb. Every live caller runs in interactive mode today. Automated mode is kept for a subagent or background worker that invokes this skill: it plans writes and never applies them (see `playbooks/automated-write-plan.md`). The unattended lanes that used to apply those plans are retired; unattended writes now belong to eve agents and their own vault tools.

**Constraints.**

- **Hard:** No enum value other than `registered` grants autonomous filing — unbypassable by construction.
- **Hard:** Undeclared mode → automated-strictness dispositions (queue-only; no filing, no mutation) + report flag. See Stop rules for the why.
- **Hard:** Automated mode never mutates existing substance, never writes human surfaces (Personal/Work), never creates Linear issues, never runs the data-correction chain. The matrix's automated column IS the complete automated write authority; everything not listed as "file" queues or discards.
- **Hard:** Re-grade lattice rule (Order of operations, step 1) — a re-grade never gains filing authority in automated mode.
- **Hard:** An append goes only to a file whose `update` is `append`. `replace`, `never`, or a missing `update` → queue, never an append (assess-candidates, update-mode guard).
- **Hard:** Every queue landing goes through `/queue create-item`; one item per queued candidate, carrying `reasons[]`.
- **Hard:** In automated mode a queue disposition requires the §0.3 entry condition (calibration surface §4 queue-entry gate); `personal-action`/`project-work` discard while task extraction is unbuilt (operator ruling 2026-07-10).
- **Hard:** Interactive data-mutation executes only per its matrix cell — explicit operator mutation intent required (calibration surface §4); extraction-inferred mutations are asked, never assumed.
- **Steering:** four dimensions as context, not a mechanical checklist; append-bias (into `append` files); collapse-bias on homes; precision-over-recall in automated mode.

**Decision authority.** The disposition matrix (calibration surface §4) IS the authority model — mode × trust × kind, complete and closed. Within it, autonomous: re-grade, vault search, coherence assessment, destination resolution, batching, filing where the matrix says file, queue-item creation via `/queue create-item`, discard logging, report emission. Operator (interactive mode): ambiguity asks, destination overrides, mutation-intent confirmations, borderline-noise asks. The contract lint (`contract_lint.py`) holds PASS/FAIL authority on a filed file's frontmatter.

**Stop rules.**

- No candidates provided → halt. Do not invent candidates.
- The vault cannot be read (Read/Grep on the vault fail or are refused) → halt; do not assess without vault context. Automated: report FAIL.
- **Undeclared mode → automated-strictness queue-only + `undeclared_mode` report flag.** Interactive is the higher-authority column, so it can never be the fallback — a missing declaration must never grant MORE authority.
- `Wiki/Queue/` missing, or a queue-item write fails → report FAIL loudly per `/queue` stop rules; a dropped judgment is invisible forever.
- Interactive contract-lint FAIL persisting after 3 fix iterations → surface the full finding list; do not mark the filing complete.

## Candidate schema

The candidate schema, plus the `pinned` marker that carries the pinned rule:

```text
{
  content:            string        # self-contained after context enrichment
  kind:               enum          # extractor's PROPOSAL; gatekeeper may re-grade
  source_attribution: string        # "CC session 2026-07-06 (Infrastructure)" / "Inbox capture 2026-07-06"
  provenance:         string[]      # Sources entries — see Write execution › Sources
  scope_hint:         string|null   # a project name or a Wiki area name — hint, not authoritative
  search_terms:       string[]      # words a future session would search with to find this
  trust:              registered | unregistered      # SOURCE property
  mode:               automated | interactive        # INVOCATION property, declared by caller
  content_hash:       string        # idempotency key at candidate level (SHA-256 of content)
  pinned:             boolean       # optional, default false — explicit operator "capture this"
}
```

`kind` ∈ the closed enum in calibration surface §3; each kind maps to exactly one destination class. Kind is a proposal — re-grading is this skill's first move, with full any-kind → any-kind authority, bounded by the lattice rule below.

## Order of operations (per candidate)

1. **Re-grade check.** Full authority, any kind → any kind. **Lattice rule (automated mode):** a re-grade whose new kind has a more permissive automated disposition than the old kind's — concretely, any re-grade INTO durable-knowledge from any other kind — forces disposition `queue`. Re-grades among queue-bound kinds, or into noise, may execute. Why: this closes the smuggling path (mutation-flavored content re-graded to "knowledge" and appended as fact) while preserving misclassification recovery — wrong-kind candidates get corrected or safely parked, never executed under the wrong contract.
2. **Vault search** — one search feeding routing and assessment: scope determination → target search → relationship (updates / extends / contradicts / none). Retain the evidence for the report and any queue item.
3. **Coherence assessment** — four dimensions at the mode's threshold (calibration surface §§1–2).
4. **Disposition** — evaluate ALL applicable conditions, collect ALL reasons; look up the matrix (calibration surface §4). Apply the §4 queue-entry gate to any automated 'queue' cell: §0.3 must hold (critically important AND legitimately stuck) or the disposition is discard, logged — pinned, quarantine, and contradiction items always queue. A queued candidate produces ONE queue item carrying `reasons[]` — conflict payload included even when unregistered also applies; no evidence loss to branch ordering.

**Destination resolution** (within step 4, durable-knowledge only) is a named judgment with a mechanical consequence. Outcome ∈ {resolved-unique, resolved-multiple, unresolved} — judgment guidance + worked examples in calibration surface §5. Mechanical consequence (calibration surface §4 cell + §5 defensible best home): automated mode files on resolved-unique OR resolved-multiple's defensible best home (alternative home noted in the entry); unresolved → queue only if §0.3 (critically important AND stuck), else discard logged (`placement-unresolved`). Interactive: resolved-unique → file; resolved-multiple / unresolved → ask (operator present). **Project-hosted opt-in gate (mechanical):** the destination project's CLAUDE.md frontmatter must include `knowledge_intake: true` (Read the file's frontmatter). Absent or false → the content files to the Wiki-hosted domain home instead (`{workspace_root}/Wiki/Knowledge/`, no opt-in required — calibration surface §5: a missing declaration never black-holes content), AND the declaration proposal queues separately (reason `opt-in-gate-absent`). In interactive mode the operator may add `knowledge_intake: true` to the frontmatter on the spot — re-check, then proceed project-hosted. **Update-mode guard (mechanical, both modes):** before any append, read the destination's `update` field; only `append` proceeds (assess-candidates step 4).

**Batching:** after per-candidate routing, group file-disposition candidates by target file; check each group pairwise for internal contradictions; one ordered append per target per run. A within-group contradiction → neither candidate files as fact: interactive → surface both versions to the operator; automated → one `disposition` queue item carrying both + evidence.

**Pinned:** an explicit operator "capture this" pins inclusion. Pinned + coherence-fail → queue (`disposition`, with a note naming the failed dimensions) — never silent discard, in any mode.

**Idempotency:** before any append, check the target for an existing entry matching `content_hash` or attribution+date → discard with reason `duplicate`. Double-append is thereby never silent.

**Interactive override:** an operator-chosen destination wins within contract-legal space, silently. A contract-violating override (e.g., personal-action → Linear; creating a rollup; appending to a `replace` or `never` file) gets the violated rule stated + explicit confirmation; confirmed = user-initiated action (the constraint system binds autonomous action only). A contract-lint FAIL on a user-chosen destination → fix the frontmatter, keep the destination — orthogonal concerns.

## Write execution

- **Interactive:** file-then-check. New files and appends follow `playbooks/assess-candidates.md` step 7: the four fields, a `## Sources` section, the type folder for project-hosted files, then `contract_lint.py`. PASS = exit 0. FAIL → fix each finding, re-run; cap 3.
- **Automated:** emit a pre-commit write plan — load `playbooks/automated-write-plan.md`. This skill NEVER applies the plan; in automated mode its only direct vault writes are `/queue create-item` files.

**Sources.** Every filed entry carries where it came from, as bullets under the file's bottom `## Sources` heading (the contract puts citations there, never in frontmatter). Use: a URL for external material; `user-stated` for facts the operator stated; `AI research YYYY-MM-DD` for session-derived synthesis; `inbox-capture YYYY-MM-DD` for an Inbox file; plus the candidate's `source_attribution`. An append adds its own bullets under the existing heading.

## Extraction report

Every run emits (both modes):

```text
{ run_id, source, candidates[],
  dispositions[],   # candidate → {file|queue|discard, reasons[], target}
  write_plan,       # automated mode; null in interactive
  applied[],        # interactive: filled by this skill; automated: stays pending (no apply stage runs)
  queue_items[],    # paths of created Wiki/Queue/ items
  flags[] }         # e.g., undeclared_mode
```

Interactive runs additionally present the human-readable summary: filed / queued / discarded, with paths and reasons.

## Navigation

| Invocation | Input | Output | Playbook |
| --- | --- | --- | --- |
| `assess candidates` | candidate list (schema above) + declared trust/mode | dispositions + extraction report (+ write plan when automated) | `playbooks/assess-candidates.md` |
| `assess single` | one candidate | same, single-candidate | `playbooks/assess-candidates.md` |

`playbooks/automated-write-plan.md` is loaded from within assess-candidates when `mode: automated` — never as a direct entry.

**Load boundaries.** Validation is never self-performed: interactive frontmatter validation runs the deterministic contract lint (a script, not judgment, so no separate-context requirement). This skill judges and composes; the lint verifies.

## What this skill does NOT do

- Does NOT extract candidates from raw content — the calling surface's job.
- Does NOT decide its own mode or trust — the caller declares both, always.
- Does NOT split candidates — multi-kind duplication happens at extraction only, with shared provenance.
- Does NOT execute the data-correction chain itself — interactive data-mutations delegate to `/wiki-intake`'s data-correction branch, the existing chain owner.
- Does NOT restate the personal-action append format — `router-spec.md` owns it; appends conform by reference.
- Does NOT apply automated write plans.
- Does NOT move, rename, or delete vault files.
- Does NOT own queue mechanics — `/queue` owns the item schema, triage, and expiry.

## References

- The ingress design (`references.intake_defaults` config key) — the spec this skill implements.
- `spec/calibration-surface.md` (this plugin) — canonical judgment tables + worked examples.
- `spec/knowledge-files.md` (this plugin) — the file contract: fields, update modes, type folders.
- `spec/integration-modes.md` (this plugin) — write shape × authority per destination.
- `/queue` — the queue-item interface (`create-item`).
- `knowledge-description` skill (sibling, same skills directory) — writing a `description`, the describe tool, and `contract_lint.py`.
- `router-spec.md` — personal-action append format owner. `linear-discipline` — project-work creation integrity.
