# Playbook: query-and-file

Hand durable session synthesis to the filing path. The gatekeeper composes the file (four frontmatter fields, `## Sources`, type folder), decides append versus new file, and runs the contract lint; this playbook validates the caller's input, maps it to `/capture batch` items, and returns the report.

## Input

```yaml
draft_content: <markdown>           # the synthesis body (without H1 or frontmatter)
title: <string>                     # informs the H1 and file name
destination_class: project-hosted | Wiki-hosted
scope: <project name OR Wiki area name>
host_project_root: <abs-path>       # required for project-hosted
sources: [<provenance string>, ...] # required; gatekeeper SKILL.md › Sources
search_terms: [<word>, ...]         # words a future session would search with
suggested_filename: <slug>          # optional
```

## Protocol

1. **Validate inputs:**
   - `destination_class` ∈ {`project-hosted`, `Wiki-hosted`}.
   - `sources` non-empty: every filed entry says where it came from.
   - If `project-hosted`: `host_project_root` exists and has a `Knowledge/` folder.
   - `draft_content` presents current understanding in one coherent pass, with no "this session" framing (hygiene anti-pattern 4).

2. **Hand off:** `/capture batch` with one item per synthesis, `entry: closeout`, `pinned: true` (the operator approved filing at closeout), and the field mapping in `capture/playbooks/batch.md` › Caller mapping.

3. **Relay** any gatekeeper ask to the operator (closeout is operator-present), then **return** the batch report unchanged.

## Output

The `/capture batch` report:

```yaml
filed:     [{path, destination_class, validator_verdict}]
queued:    [{item_path, reasons}]
discarded: [{summary, reason}]
flags:     [...]
```

A `filed` entry with `validator_verdict: FAIL` is on disk but not counted complete; surface its findings to the caller.

## What this playbook does NOT do

- Does NOT compose frontmatter, choose the folder, or write the file — the gatekeeper does.
- Does NOT compose the draft content — the caller does.
- Does NOT decide whether the synthesis is worth filing — the caller does.
- Does NOT edit existing pages in place. A revision of a `replace` file is a direct edit by the session that owns the context, with `updated` and `description` refreshed; the gatekeeper queues rather than appends to it.
