# Playbook: extract

Mid-session capture: locate → extract → enrich → classify → hand off → relay.

## 1. Locate the referent

- **Pointed ask** ("capture this", "capture that decision about X"): resolve to the specific conversation content. If "this" plausibly means two or more things → ask; never guess, never fall back to a whole-session sweep.
- **Broad ask** ("capture this discussion", "capture the session so far"): sweep the conversation for candidates passing the interactive bar (calibration surface §§1–2). Material the operator explicitly named is **pinned**; sweep extras are unpinned — list them in one line each for a quick operator keep/drop before handoff.
- **Bare `/capture`:** treat as a broad ask over the session since the last capture (or session start).

## 2. Extract and enrich

Per candidate:

- Rewrite to self-containment: resolve pronouns, name the subjects and systems, date the claims. Enrichment adds context, never new claims — the operator's substance is preserved.
- `content_hash` = SHA-256 of the enriched content (`shasum -a 256` on stdin).
- `source_attribution` = `CC session YYYY-MM-DD (<project>)` — date via `date`, project from the session's cwd.
- `provenance` per gatekeeper SKILL.md › Sources: `user-stated` for operator-stated facts; `AI research YYYY-MM-DD` for session-derived synthesis; a URL for external material.
- `trust` per the source rule (SKILL.md Identity): `registered` for operator-authored content; `unregistered` for third-party pasted/forwarded material. The pin still applies — a pinned unregistered candidate is surfaced, never filed autonomously and never silently dropped.

## 3. Classify (proposal only)

Load the calibration surface (`spec/calibration-surface.md` at this plugin's root). Per candidate: propose `kind` (§3 definitions — one kind per candidate; a source item spanning two kinds yields TWO candidates with shared provenance, split here at extraction), `scope_hint` (a project name or a Wiki area name), `search_terms` (the words a future session would search with). Set `pinned` per step 1. The gatekeeper may re-grade — the proposal just has to be honest.

## 4. Hand off

Invoke `/gatekeeper assess candidates` with the full candidate list, `mode: interactive`, and each candidate's per-source `trust` (step 2). Relay every gatekeeper ask (destination ambiguity, extraction-inferred mutation confirms, conflicts, surfaced unregistered content) to the operator faithfully — the ask resolves in this conversation, then the gatekeeper completes disposition.

## 5. Destination overrides

When the operator names a destination (before or after handoff):

- **Contract-legal** → it wins, silently. Pass it to the gatekeeper as the resolved destination.
- **Contract-violating** (e.g., a personal-action into Linear; a rollup file; project Knowledge/ in a project without `knowledge_intake: true`) → state the violated rule in one sentence + ask for explicit confirmation. Confirmed → proceed as a user-initiated action. Declined → fall back to the gatekeeper's own resolution.
- A filing-time lint gate FAIL on an operator-chosen destination → the envelope gets fixed; the destination stays.

## 6. Relay the report

Present the gatekeeper's outcome: **filed** (paths + lint gate verdicts), **queued** (item paths + reasons), **discarded** (reasons), plus any `flags[]`. Reconcile against the handed-off candidate list — a candidate missing from the report is a reconciliation gap: surface it, do not report success.
