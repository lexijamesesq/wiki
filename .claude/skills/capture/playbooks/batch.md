# Playbook: batch

Boundary entry — the same machinery as `extract.md`, minus conversation sweeping. The caller has already identified WHAT to capture; this playbook normalizes, hands off, and relays. Callers: `/knowledge-layer` query-and-file (closeout Step 9 — the durable-synthesis gate is the CALLER's judgment, upstream of here) and the closeout preflight capture scan.

**Invocation: `/capture batch <items>`**

## Input

```yaml
entry: closeout | ad-hoc
items:
  - content: <markdown — the synthesis/claim body>
    title: <string>                    # optional; informs new-file naming
    kind_proposal: <kind enum>         # optional; default durable-knowledge
    scope_hint: <project name | Wiki area name>   # optional
    search_terms: [<word>, ...]        # words a future session would search with
    sources: [<provenance string>, ...]  # gatekeeper SKILL.md › Sources
    pinned: <bool>                     # operator-confirmed at closeout → true
    source_attribution: <string>       # default "CC session YYYY-MM-DD (<project>)"
    trust: registered | unregistered   # optional, default registered (closeout synthesis is operator-authored); third-party material MUST be marked unregistered
```

**Caller mapping — query-and-file input → items:** `draft_content` → `content`; `title` → `title` (`suggested_filename` → `title` when `title` is absent); `destination_class` + `scope` → `scope_hint` (the project name for project-hosted, the Wiki area name for Wiki-hosted); `host_project_root` → informs the project-hosted `scope_hint` (the gatekeeper resolves final placement, including the type folder, from the resolved scope); `search_terms` → `search_terms`; `sources` → `provenance`. Operator-approved synthesis is `pinned: true`.

## Protocol

1. **Normalize** each item to the gatekeeper's candidate schema (gatekeeper SKILL.md › Candidate schema): enrich to self-containment only where needed (closeout drafts usually already are); compute `content_hash` (`shasum -a 256`); fill `source_attribution` and provenance defaults.
2. **Hand off** ALL candidates: `/gatekeeper assess candidates`, `mode: interactive`, trust per item (default `registered`; unregistered items surface in-conversation per the matrix). A caller with no human in the loop must say so — then declare `mode: automated` and expect queue-only dispositions (subagents/background workers MUST declare automated).
3. **Relay asks** to the operator (closeout is operator-present); apply the SKILL.md override rules if the operator redirects a destination.
4. **Return** the structured report to the caller:

```yaml
filed:     [{path, destination_class, validator_verdict}]
queued:    [{item_path, reasons}]
discarded: [{summary, reason}]
flags:     [...]
```

## What this playbook does NOT do

- Does NOT apply the durable-synthesis gate — the caller decides WHAT to hand in; this files what it is handed *through the gatekeeper*.
- Does NOT sweep the conversation — that's `extract.md`.
- Does NOT write destinations or queue items itself — gatekeeper machinery, as everywhere in this skill.
