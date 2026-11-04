---
name: context-page
description: >-
  Keep a Wiki area's context page current when
  a session learns something durable about the operator or the area. Hand-writes
  three sections: User Context, Approach, Working Understanding. Triggers on
  learning a lasting preference or constraint, a change in how to help in an area,
  or a shift in the picture of an area; also "update the context page",
  "refresh the <area> context".
---

# Context page

A context page orients a session in one area before it starts work: who the operator is in that area, how to help, and what is currently understood. It lives at `{workspace_root}/Wiki/Contexts/<area>-context.md`, and is one of the files `spec/knowledge-files.md` governs.

## When to update

Update when the session learned something **durable**: it will still be true and useful next month, and a future session in this area would act differently for knowing it. Typical triggers:

- The operator states a preference or constraint that is not tied to this task.
- You find a way of helping in this area that works, or one that does not.
- The picture of the area shifts: a decision settles, a system changes, an assumption proves wrong.

Do not record: what happened in this session, task status, anything already in a Knowledge file (link it instead), or a guess. If unsure whether it is durable, leave it out.

## Shape of the page

Frontmatter carries the four required fields (`description`, `update: replace`, `related`, `updated`). The `description` says what area the page covers and what a session gets from it. The page has three hand-written sections (listed here in the order a new page uses; an existing page may carry them in another order, and a fact update does not reorder or reformat them):

| Section | Holds |
| --- | --- |
| `## User Context` | The operator's preferences and constraints in this area, stated as facts about her. |
| `## Approach` | How to help in this area: what to do, what to avoid, and what depth she wants. |
| `## Working Understanding` | A synthesized picture of the area as it stands: how the parts fit and what is settled versus open. A synthesis you keep coherent, not a log, in whatever form the page already uses (prose or bullets). |

There is no Cross-Domain section. Links to other areas, and to the Knowledge files that back a claim, go in `related` frontmatter as aliased wikilinks, `"[[target|short reason]]"`.

## How to update

1. Read the page with the Read tool, and run the describe tool over the area's Knowledge folder (`python3 ${CLAUDE_PLUGIN_ROOT}/.claude/skills/knowledge-description/scripts/describe.py <folder>`) to see what already carries the detail.
2. Revise in place. The page is `update: replace`: rewrite the sentence that is now wrong rather than appending a correction, and leave no "previously" or "superseded" notes. Merge a new fact into the section where it belongs; if it contradicts an existing line, resolve the contradiction.
3. Keep Working Understanding a synthesis. When it starts reading as a list of findings, those findings belong in a Knowledge file with a `related` link from here.
4. Add `related` links for areas or files the new understanding connects to. Refresh `description` if the page's scope changed. Set `updated` to today's date.
5. Check the result against the contract: `python3 ${CLAUDE_PLUGIN_ROOT}/.claude/skills/knowledge-description/scripts/contract_lint.py <page>`.

Edit the page in place with the Edit tool (Write only when the page does not exist yet). The vault is live files under `{workspace_root}`, never a checkout of this repo, and no MCP server mediates vault writes. Say in your reply what you changed on the page and why, in one or two lines.
