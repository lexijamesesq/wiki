---
tags:
  - type/spec
  - project/system
  - status/active
updated: '2026-11-03'
---

# Integration Modes — Destination Write Discipline (superseded)

**Superseded 2026-11-04.** No skill reads this document any more. Its write discipline lives in `spec/knowledge-files.md`, and the automated-write machinery it described was retired with the gatekeeper, router, wiki-intake and queue skills, which were built for captures arriving with no known destination and were never used that way. Kept as the design record; amend nothing here.

| Part | Fate |
| --- | --- |
| §1 The property (evolution vs current truth) | Replaced by the per-file `update` mode (`append` / `replace` / `never`) in `spec/knowledge-files.md` › Update modes |
| §2 Class defaults | Retired: a folder never sets the mode; each file declares its own |
| §3 Frontmatter override | Replaced by the required `update` field; `integration:` retired at cutover |
| §4 Write shape × authority | Retired with the gatekeeper; interactive sessions follow the `update` field, unattended writers are held by their own tools (`spec/knowledge-files.md` › Enforcement) |
| §5 The validated-mutation path | Retired, never activated; unattended-write enforcement belongs to the eve agents' vault tools (the librarian work) |

---

## Historical record (as of 2026-11-03, unmaintained)

Everything below is the document as it stood before supersession. Its instructions, including "amend here", no longer apply.

The canonical home of the **integration-mode property**: whether a write destination
serves *evolution* or *current truth*, the write shape and authority that follow, and
the validated-mutation path that earns automated writes on current-truth surfaces.
Owns the mutation-discipline layer the knowledge contract deliberately leaves outside
its envelope (now the per-file `update` mode in `spec/knowledge-files.md`; the earlier rule was knowledge-contract Part II › Body & Content Architecture, superseded). Consumers —
calibration-surface §§3–5, the gatekeeper (write plans), `/wiki-intake`
(data-correction chain), stewardship and closeout surfaces — reference this file.
Nothing here is restated elsewhere; amend here, nowhere else.

## §1 The property

Before any write to an existing surface, ask: **does this destination serve evolution
or current truth?**

- **evolution** — the file accretes dated, attributed entries; history is part of the
  value; newer entries supersede older ones explicitly, in place (dated accretion is
  not contradiction). Write shape: **append**.
- **current-truth** — the surface states what is true NOW; superseded content is
  replaced, never annotated (single source of truth — no banners, no strikethrough
  fragments; the annotation is the confusion). Write shape: **update/replace**, under
  the surface's own discipline.

The mode is a property of the destination, not of the candidate. A state-change fact
written toward an evolution surface files as a dated superseding entry; the same fact
applied to a current-truth surface replaces the stale value.

## §2 Class defaults

Derived from the architecture, not new policy:

| Destination class | Serves | Encoded where |
| --- | --- | --- |
| {workspace_root}/Wiki/Knowledge + project Knowledge/ | evolution | append-bias mutation discipline; consolidation human-approved |
| {workspace_root}/Wiki/Contexts | current-truth | update-on-shift; authority hierarchy (context page wins conflicts) |
| Wiki/Data | current-truth | typed records of tracked state; correction chain |
| Personal/Work pages | current-truth | stewardship patches facts in place; structure human-owned |

## §3 Frontmatter override

Every knowledge file declares its own mode in the `update` frontmatter field
(`append` | `replace` | `never`, defined in `spec/knowledge-files.md`). That field is
what a writer reads at write-plan time. A knowledge file without it breaks the contract, and a
writer treats it as not appendable. For knowledge files and context pages the field governs;
the §2 class defaults still govern destinations that carry no `update` field (`Wiki/Data`,
Personal/Work pages). The older `integration:` field is no
longer read; the cutover removes it.

What reads the field today, and what does not:

- Interactive sessions: the field is the instruction. The contract lint
  (`contract_lint.py` in the `knowledge-description` skill, shipped with the Studio kit in wiki#206)
  checks that `update` is present and one of the three values; nothing today checks that an
  edit respected the mode. That is the writer's own discipline until the check below exists.
- Unattended writers (eve agents): the vault tools will refuse a write that breaks the mode.
  That check is the eve vault-tool change and is not yet built.
- The filer in this repo (`gatekeeper`) reads `update` before any append to an existing file,
  in both modes (`assess-candidates`, update-mode guard): `replace`, `never` and missing
  `update` take a queue item, never an append. The check sits in the gatekeeper because the
  gatekeeper is what writes; the session that handed it the candidate never sees
  the destination. Automated mode (`automated-write-plan`) plans writes and applies none: the
  capture and maintenance lanes that applied its plans are retired.

## §4 Write shape × authority

| Destination mode | Interactive | Automated |
| --- | --- | --- |
| evolution | append, per the calibration matrix | append, per the calibration matrix (Knowledge-layer write plan `{target, pre_state_hash, append_suffix}` — overwrite structurally impossible) |
| current-truth | the surface's own discipline (update-on-shift; correction chain on explicit intent; stewardship patch) | **validated-mutation path (§5)** once active; queue until then. Registered trust only — `automated + unregistered` queues always; the unregistered-trust line is untouched by activation |

Personal/Work pages carry no automated write authority in either mode — human-owned
structure, not on the capture mission path.

## §5 The validated-mutation path (designed; activation-gated)

Queue-by-default on automated current-truth candidates is prevention applied to a
recoverable effect. With pre-state preserved, a mutation is one-step revertible — the
safety doctrine (reversible → recover, not prevent) licenses automated mutation
**behind machinery validation**, not deferral. The machinery is the fourth member of
an existing family: the capture critic (rubric v2) gates the pre-commit write plan
(appends and creates), the filing-time lint gate verifies new files post-apply, the
maintenance lane's fix-rubric critic gates envelope patches (plan → context-free
critic → model-free scripted apply with hash recheck — unified-ingress §9), and the
**authenticity validator** gates mutations. This is no context-not-machinery
violation: that diagnostic targets recurring *judgment* failures; mutation
authenticity is a *verification* gate — models declare, scripts enforce, validators
refute.

**Mutation plan (builder emits — the gatekeeper):**
`{target, locator (field/section), pre_state (verbatim), post_state, source_evidence
(quoted), attribution (routine/<action> <run-id>)}`. Per-run cap: ≤N mutations per
run (start at the Pass-3 precedent's bound of 20).

**Authenticity validator (fresh context, refute mandate, per validation-discipline):**

1. **Source-says-it** — the source payload actually asserts this change, in its own
   words; quoted evidence; no synthesis, no inference past the source.
2. **Target-state** — the live target still matches `pre_state`; a stale or
   conflicting mutation FAILs.
3. **Right record** — the locator names the record/section the source is about;
   type-consistent with its schema.
4. **No newer claim** — no conflicting later-dated claim within the run's source
   payload(s) or the target file itself.

Any leg FAILs → quarantine queue item carrying the plan + reasons (the unified-ingress
§5 quarantine pattern; a FAILed plan always surfaces — no importance test applies).

**Deterministic apply (script, not model):** re-hash the target; apply `post_state`
only on `pre_state` match; mismatch → abort that mutation (no write), queue item
carrying the plan + reason `stale-pre-state`, continue other writes — the
append-lane pattern (unified-ingress §5). Write attribution; store `pre_state` in
the run report → one-step revert. The revert script hash-checks the target against
`post_state` before restoring `pre_state`; a target edited since the mutation
quarantines instead of reverting. Post-apply verify: re-read the target; confirm
`post_state` present at the locator and `pre_state` absent. FAIL → quarantine queue
item naming expected-vs-found, heartbeat suppressed, no further writes this run, no
auto-revert (revert is the operator's one command, from the stored `pre_state`).
Detection: run report + write-volume alarm + heartbeat.

**What this path removes (ratchet):** queue-by-default as the *terminal design* for
automated current-truth candidates — a standing operator-attention tax; under the
operator's baseline an untriaged queue is where content goes to die (the queue remains
the validator-FAIL and genuinely-stuck surface). Also removed: the unmechanized
earn-path via operator queue rulings — rulings become calibration data for the
validator's rubric, not the mechanism itself — and the calibration matrix's two
per-kind exception explanations, collapsed into one named property.

**Staging:** activate on `data-mutation` first — typed records make all four legs
strongest and mechanical-adjacent. `context-shift` follows only after the lane holds
on Data/: prose working-understanding makes source-says-it judgment-heavier, and
context corruption is the costliest failure in the vault (the authority hierarchy
makes context pages win conflicts).

**Provenance narrowing (initial activation):** the validated-mutation path activates
only for candidates whose source payload is operator-authored end-to-end (registered
trust AND operator-authored source class — e.g., Inbox captures; multi-speaker meeting
transcripts are excluded even when registered, because registered trust attests the
operator configured the source, not that she authored every claim in it). Extending
mutation authority to transcript-sourced claims requires its own amendment adding a
fifth validator leg — **operator-voiced**: the quoted `source_evidence` is
speaker-attributed to the operator — plus a diarization-reliability proof on the pilot
meeting.

**Activation gate:** the calibration matrix's `data-mutation` / `context-shift`
**automated + registered** cells flip from `queue` only by calibration-surface
amendment, after the lane passes: fixture eval green + live proof on a real capture +
a reproducible acceptance command run by a non-author session. The
`automated + unregistered` cells never flip — the unregistered-trust line survives
activation unconditionally. The activation amendment must re-derive the §3 re-grade
lattice: any kind whose automated disposition becomes more permissive joins the
forced-queue INTO set (`data-mutation` at this rung). The activation amendment's sweep
list: unified-ingress §2 Consequences + §6 R6, calibration §4 Consequences,
Wiki/CLAUDE.md Decision Authority (automated lanes), and the §3 lattice re-derivation
(above).

## Amendment discipline

This file changes only by operator-approved edit. Consumers reference sections by
number (§1–§5); renumbering requires sweeping consumer references (calibration
surface, gatekeeper, `/wiki-intake`, stewardship surfaces).
