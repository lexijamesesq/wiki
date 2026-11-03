---
name: knowledge-layer
description: >-
  Knowledge layer expert for session closeout — hygiene anti-pattern scan that
  respects each file's update mode, query-and-file handoff of durable session
  synthesis to the gatekeeper, and a contract lint of the session's touched
  knowledge files. Invoked by /session-closeout. Triggers on
  "/knowledge-layer <operation>" or programmatic invocation.
---

# /knowledge-layer

Domain expert for the Knowledge layer at session closeout — project-local `Knowledge/` folders, `{workspace_root}/System/Knowledge/`, and `{workspace_root}/Wiki/Knowledge/`. The file contract is `spec/knowledge-files.md` at this plugin's root (`../../../spec/` from this skill's folder): four frontmatter fields (`description`, `update`, `related`, `updated`), three update modes, five type folders for project-scoped Knowledge.

## Identity

The Knowledge layer is the vault's reusable-synthesis surface — methodology docs, implementation specs, reference content, research, decisions, records. This skill owns three per-session operations on it: scanning touched docs for anti-patterns, handing new synthesis to the filing path, and checking touched files against the contract.

Discipline rules applied on every invocation:

- **The `update` field decides what may change.** `append`: existing text stays unchanged, new text is only added. `replace`: rewritten in place to stay current, with no deprecated banners or strikethrough. `never`: no body change; a successor is a new file. Frontmatter is editable under every mode. Read a file's `update` before changing its body.
- **One filing path.** New synthesis files through `/gatekeeper assess candidates`, which composes the file, places it, and runs the contract lint. This skill never writes a new knowledge file itself.
- **Vault files are read and edited with native tools** (Read, Grep, Glob, Edit) under the session's own permissions.
- **A changed file gets a true description.** Any body fix this skill makes ends with the file's `description` re-read against the new body and refreshed if it no longer holds (`knowledge-description` skill), and `updated` set to today.

## Intent

**Objective.** Without this skill, knowledge-doc hygiene and closeout filing would either live inline in session-closeout or get reimplemented across consumers. The anti-patterns would drift, the update modes would be ignored at the moment a session is most tempted to "clean up" a file, and new synthesis would bypass the gatekeeper.

**Desired outcomes** (observable):

1. Every doc touched this session is scanned against the seven anti-patterns, read through its own update mode.
2. Ambiguous hygiene cases get fresh-context review via subagent; never self-evaluated in the scan path.
3. Durable session synthesis reaches the gatekeeper, and the caller gets back filed paths with lint verdicts.
4. Every knowledge file the session touched passes the contract lint before closeout ends, or its findings are in the closeout summary.

**Health metrics — must NOT degrade.**

- Zero body edits to `never` files; zero rewrites of existing text in `append` files.
- Load-boundary-as-guard for the hygiene write/review split: the scan path NEVER loads the review playbook.
- Zero new knowledge files written outside the gatekeeper.

**Strategic context.** One of three domain skills session-closeout composes (with `/project-state` and `/linear`). Periodic whole-corpus checks are `/lint-knowledge`'s (on demand) and, once live, the librarian agent's: freshness, links, and drift between context pages and Knowledge files move there.

**Constraints.**

- **Hard:** update modes (Identity). Hygiene-review subagent invoked with fresh context (scan path never loads the review playbook).
- **Steering:** hygiene classification (current-context-fix vs. defer) by current-context-availability, NOT line count. Anti-pattern detection uses inclusive matching (flag possible hits as ambiguous; let the subagent rigor-check).

**Decision authority.**

- **Autonomous:** hygiene fixes on `replace` files within current-context scope; frontmatter fixes on files this session created or edited; the gatekeeper hand-off of operator-approved synthesis.
- **Escalate via subagent:** ambiguous hygiene patterns → spawn `hygiene-review` with fresh context.
- **Escalate via Linear issue:** out-of-scope hygiene refactors → file via `/linear` issue creation.
- **Escalate to operator:** out-of-session-scope docs needing modification → flag, don't modify; hygiene hits on `append` or `never` files (the fix would break the mode — the operator decides whether the file's mode or a successor file is the answer).

**Stop rules.**

- `contract_lint.py` unavailable (script missing or exits `2`) → surface to caller; do not report the scope as clean.
- Out-of-session-scope project doc modification attempted → halt; flag to operator.
- Hygiene-review subagent FAIL after 3 iterations per doc → surface with full finding list; do not silently fix.

## Navigation

Per invocation, identify the operation and load the matching playbook:

| Operation | Input | Output | Playbook |
| --- | --- | --- | --- |
| **hygiene** scan | List of touched doc paths | Fixes applied (`replace` files, current-context) + items flagged (defer, or mode-blocked) + ambiguous items for review | `playbooks/hygiene.md` |
| **hygiene-review** (subagent-only) | Doc path + its update mode + anti-pattern definitions | Per-doc verdict (PASS/FAIL/REVISE) | `playbooks/hygiene-review.md` |
| **query-and-file** | Synthesis draft + destination class (project-hosted / Wiki-hosted) | Gatekeeper report: filed paths with lint verdicts, queued, discarded | `playbooks/query-and-file.md` |
| **scope-lint** | Session-touched vault paths + session-created subset | Frontmatter fixes on session-touched files; remaining findings listed for the closeout summary | `playbooks/scope-lint.md` |

## Load-boundary-as-guard

`playbooks/hygiene.md` is the SCAN+FIX path. `playbooks/hygiene-review.md` is the REVIEW path for ambiguous pattern-matching cases. The hygiene scan path NEVER loads the review file. Review is reachable only as a fresh subagent invocation per ambiguous doc, given the doc, its update mode, and the anti-pattern definitions, with no context about other docs scanned or the closeout's session-level reasoning.

Same pattern as `/linear`'s project-updates write/review split. Same structural guard.

## What this skill does NOT do

- Does NOT read or write CLAUDE.md (that's `/project-state`).
- Does NOT touch Linear beyond filing hygiene deferrals (that's `/linear`).
- Does NOT write new knowledge files — the gatekeeper does.
- Does NOT scan for staleness, orphans, or broken links across a whole folder, and keeps no index: there are no `index.md` files; a file's `description` plus the describe tool (`knowledge-description` skill) replace them. Folder-wide freshness and links are the librarian's.
- Does NOT decide whether a session produced synthesis worth filing — the caller (session-closeout's "Did this session produce durable synthesis?" check) makes that call.

## References

- `spec/knowledge-files.md` (this plugin) — the file contract.
- `knowledge-description` skill (sibling) — writing a description, the describe tool, `contract_lint.py`.
- The gatekeeper (`/gatekeeper assess candidates`) — the filing path query-and-file hands to.
