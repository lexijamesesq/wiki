---
tags:
  - type/spec
  - project/system
  - status/active
updated: 2026-11-02
---

# Knowledge Files

The contract for knowledge files: four frontmatter fields, three update modes, five base folders. It defines the target state. `spec/knowledge-contract.md` stays in force and `lint.py` keeps reading it until the cutover (see the pull request that introduced this file for what the cutover supersedes).

## Scope

| In scope | Out of scope |
| --- | --- |
| Every `Knowledge/` folder: `{workspace_root}/Wiki/Knowledge`, `{workspace_root}/Projects/*/Knowledge`, `{workspace_root}/System/Knowledge`, `{workspace_root}/Agents/*/Knowledge` | `Wiki/Data` records (own schema; Obsidian Bases read their properties) |
| `{workspace_root}/Wiki/Contexts` pages | `Personal/`, `Work/` |

## Frontmatter

Exactly four required fields.

| Field | Value | Rule |
| --- | --- | --- |
| `description` | One or two sentences | True of this file and specific to it. Written in the words someone would search with. |
| `update` | `append` \| `replace` \| `never` | How the body may change. See Update modes. |
| `related` | List of aliased wikilinks | `"[[target-file\|Short reason]]"`. Reason at most about 45 characters; no `\|` or `]]` inside it. Empty list allowed. |
| `updated` | `YYYY-MM-DD` | Date of the last content change. File mtimes are unreliable under Obsidian Sync, so this field is the record. |

```yaml
---
description: How the nightly export job is scheduled and what it writes.
update: replace
related:
  - "[[export-failure-log|Past failures]]"
updated: 2026-11-02
---
```

- `related` links render in Obsidian and follow renames. A background librarian agent maintains the list; any writer may add to it.
- Body is content only. Citations go in a bottom `## Sources` section.
- Retired at cutover: `tags` (all families), `verified`, frontmatter `sources`, `integration`.

## Update modes

Declared per file in `update`. A folder never sets the mode. Frontmatter is editable under every mode.

| Mode | Rule |
| --- | --- |
| `append` | Existing text stays unchanged. New text is only added, anywhere (for example under its parent heading). |
| `replace` | Rewritten in place to stay current. No deprecated or superseded banners, no strikethrough. |
| `never` | No body changes. A successor is a new file. |

## Structure

**Project-scoped Knowledge** (each `Projects/<p>/`, plus `System/` and each agent) uses five base folders inside `Knowledge/`. Projects may add folders.

| Folder | Holds |
| --- | --- |
| `Methods/` | How we do things |
| `Reference/` | How a system is built; what is true now |
| `Research/` | Findings about the outside world |
| `Decisions/` | Choices and the reasoning behind them |
| `Records/` | Dated, frozen material: snapshots, transcripts, incident logs, historical records |

**Wiki** has no type folders. `Wiki/` keeps `Attachments/`, `Contexts/`, `Data/`, `Knowledge/`.

## Wiki context pages

`{workspace_root}/Wiki/Contexts/*-context.md` are area orientation pages. Hand-written sections: User Context, Approach, Working Understanding. What used to be a Cross-Domain section is now `related` frontmatter.

## Enforcement

| Writer | Held to the spec by |
| --- | --- |
| Unattended (only eve agents on calcifer) | Their vault tools reject writes that break the spec |
| Interactive sessions | Following it as a way of working; the `update` field is the instruction. A lint tool runs on demand. |

Unattended writes are logged with a 30-day TTL (Obsidian Sync Standard keeps one month of history), so any such write can be recovered or reverted inside that window.
