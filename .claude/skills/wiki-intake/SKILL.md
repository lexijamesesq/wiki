---
name: wiki-intake
description: >-
  Entry point for Wiki-axis content the operator hands over directly, and the
  owner of the data-correction chain the gatekeeper delegates to. Classifies
  intent and routes:
  knowledge-intent captures are packaged as typed candidates for the
  gatekeeper (which owns coherence, destination, filing,
  and validation), explore/triage captures become Wiki/Queue/ items, and data
  corrections run the mutation chain. Triggers on "/wiki-intake", "file this to
  wiki", "wiki intake", or a gatekeeper data-correction hand-off.
---

# Wiki Intake

Entry point for Wiki-axis content the operator hands over directly: classifies intent and routes. Also the owner of the data-correction chain, which the gatekeeper delegates to when a capture is a fact change. Composes with `/gatekeeper` (the gatekeeper — owns the coherence decision and filing) and `/queue` (the Wiki/Queue/ item interface). See `{workspace_root}/System/Knowledge/Reference/unified-ingress-design.md §§13–15` for the architectural pattern.

## Identity

- **This skill classifies and routes; it does not judge coherence or file knowledge.** Speculative filing creates orphaned content that's harder to find than unfiled content — an honest "I don't know where this goes" beats a confident misfile.
- **Knowledge-intent content never files directly** — candidates go to the gatekeeper, always.
- **Intake adds, never removes.** No deletion as part of any branch.
- **Append-bias on data-corrections** — appending to Knowledge/ is autonomous; editing existing substance is not.

## Intent

**Objective.** Captures die in two ways: they never get filed (lost in queue purgatory) or they get filed wrong (orphaned in the wrong location, misdescribed, lacking provenance). Wiki intake ensures every capture that reaches the Wiki axis gets a deliberate routing decision — packaged as candidates for the gatekeeper when it's knowledge, staged as a Wiki/Queue/ item when it isn't, or run through the mutation chain when it's a correction. The cost of a wrong placement is higher than the cost of a queue item.

**Desired outcomes** (observable):

1. Every capture receives a classification decision — no silent drops, no ambiguous deferrals.
2. Candidates handed to the gatekeeper are self-contained and fully specified per the candidate schema.
3. Queue items carry enough context that a future triage or stewardship session can act on them without re-deriving intent.
4. Data corrections propagate through all affected layers in a single pass — no partial updates leaving inconsistency between Data/, Knowledge/, Context, and Personal/Work.

**Health metrics — must NOT degrade.**

- Zero captures lost during intake — every input produces a gatekeeper disposition, a Wiki/Queue/ item, a staged Inbox/ file, or an explicit halt-and-ask.
- Zero underspecified candidates — every candidate handed to the gatekeeper carries provenance, trust, and mode.
- Data-correction chain touches all affected layers — no partial propagation.
- Queue items are actionable without the original conversation.

**Strategic context.** A Wiki-axis entry point of the ingress design, alongside `/capture` (mid-session) and `/router` (Inbox). All of them hand typed candidates to the same gatekeeper; the router and `/capture` now deliver there directly, so this skill's own entry is an operator invoking `/wiki-intake`. Its lasting duty is the data-correction chain.

**Constraints.**

- **Hard:** never file knowledge-intent content directly (candidates only); never delete content; data-correction execution requires explicit operator mutation intent (inferred intent asks first); a data-correction that would edit existing Knowledge/ substance halts for approval.
- **Steering:** classification bias is honesty over confidence — ambiguous intent halts and asks rather than guessing a placement.

**Decision authority.**

- **Autonomous:** classifying capture intent; packaging knowledge-intent captures as candidates and invoking the gatekeeper (coherence, destination, filing, and validation are gatekeeper-owned — this skill relays its report); creating `Wiki/Queue/` items for explore/triage; staging out-of-vault captures to `Inbox/`; executing the data-correction chain on an explicit operator mutation statement.
- **Escalate:** mutation intent inferred rather than stated → ask/confirm before executing the chain; classification ambiguous → halt and ask; editing existing Knowledge/ substance (vs. appending) → halt and flag; a Knowledge/ file would exceed 150 lines after a data-correction append → advisory flag as a consolidation candidate, do not halt; promoting a queue item to Knowledge/ → human-initiated, not this skill's call.

**Stop rules.**

- Out-of-vault cwd → stage to `Inbox/` with a provenance note and report; never process directly.
- Capture can't be classified cleanly → halt and ask; don't guess.
- A data-correction would edit existing Knowledge/ substance (vs. appending) → halt.
- Never file knowledge-intent content directly — candidates go through the gatekeeper, always.
- Never delete content as part of intake.

## Navigation

Per invocation, work through the stages in order and load the matching playbook:

| Stage | Input | Output | Playbook |
| --- | --- | --- | --- |
| Classify intent (Step 1) | capture content | intent: `knowledge` \| `data-correction` \| `explore` \| `triage` | `playbooks/classify.md` |
| Route: knowledge | classified capture | candidates handed to the gatekeeper; disposition report relayed | `playbooks/knowledge-intent.md` |
| Route: data-correction | classified capture | mutation chain executed across affected layers | `playbooks/data-correction.md` |
| Route: explore / triage | classified capture | `Wiki/Queue/` item created | `playbooks/explore-triage.md` |

## Cross-cutting

### Preflight: out-of-vault guard

wiki-intake's delegates (the gatekeeper, `/queue`) are vault-resident; filing requires vault access. Determine the vault root: `VAULT_ROOT` env var if set, else `workspace_root` (global CLAUDE.md > Configuration). If the session cwd is NOT inside the vault root:

1. Do not classify or process — the delegates this skill routes to are unavailable.
2. Stage the raw capture to `{vault_root}/Inbox/` verbatim, plus a provenance note (capture source, date, invoking context, reason staged: wiki-intake invoked outside the vault).
3. Report the staged path — the session-start debt line covers Inbox/, so the capture surfaces at the next vault-rooted session.

If the cwd is vault-rooted, proceed to Step 1 (classify).

### Input sources

| Source | Format |
| --- | --- |
| `/wiki-intake {text}` | Inline text in the invocation |
| `/wiki-intake` (no args) | Prompts user for content |
| Gatekeeper hand-off | A data-mutation candidate with explicit operator mutation intent (data-correction branch only) |
| Chat interface delivery | Data update or query from messaging integration (future) |

### Provenance

Every candidate carries `provenance` (gatekeeper SKILL.md › Sources); every data-correction append carries date attribution. User-stated facts use `user-stated`; captures use the original URL or `inbox-capture`. The queue is not a graveyard — items surface via the statusline queue signal and drain via operator-invoked `/queue triage`; keep descriptions actionable. Data-corrections are the eventual bridge to the chat interface: the mutation chain defined here is the same chain that channel will use.

## What this skill does NOT do

- Does NOT judge coherence, resolve destinations, or file knowledge-intent content — that's the gatekeeper's job; this skill packages and relays.
- Does NOT own queue mechanics — `/queue` owns the item schema and drain.
- Does NOT append to `Wiki/backlog.json` — frozen; superseded by `Wiki/Queue/`.
- Does NOT promote queue items to Knowledge/ — human-initiated.
- Does NOT delete content, ever.

## References

Paths use the `{workspace_root}` placeholder — resolve via global CLAUDE.md > Configuration > `workspace_root`.

- The vault's ingress-design doc (not shipped in this repo — a System-project reference) — the routing model this skill implements: candidate schema, trust/mode disposition matrix, gatekeeper wiring, out-of-vault guard.
- `../gatekeeper/` — the gatekeeper (bundled sibling skill); the coherence judgment (dimensions, thresholds, worked examples) lives at `spec/calibration-surface.md` at this plugin's root — cited by the knowledge-intent playbook, never restated here.
- `{workspace_root}/Wiki/CLAUDE.md` — Wiki stewardship rules, decision authority, stop rules.
- `{workspace_root}/System/target-architecture-v2.md` — space structure, Data/ threshold.
- `{workspace_root}/System/Knowledge/Reference/unified-ingress-design.md §§13–15` — routing patterns and accountability boundaries.
- `spec/knowledge-files.md` (this plugin) — the file contract: frontmatter fields, update modes.
