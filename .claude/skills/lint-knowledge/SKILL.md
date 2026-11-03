---
name: lint-knowledge
description: >-
  Check a project's, the Wiki's, or the whole vault's knowledge files against
  the knowledge-file contract in one pass, and report the violations file by
  file without fixing anything. Runs the contract lint tool from the
  knowledge-description skill. Triggers on "/lint-knowledge", "lint
  knowledge", "check knowledge health", or "scan knowledge for issues".
---

# Lint Knowledge

The operator's verb for a whole-scope health check of knowledge files. It resolves a scope to folders, runs the contract lint tool over them, and reports. It fixes nothing.

The rules live in `spec/knowledge-files.md` (four frontmatter fields, three update modes). The tool that checks them is `contract_lint.py` in the sibling `knowledge-description` skill; its rule ids are listed in that skill's `references/lint-rules.md`. This skill adds scope resolution and a readable report, nothing else.

## Scope

Resolve the vault root from the `workspace_root` config key (global CLAUDE.md > Configuration) and project folders from `projects_root`.

| Invocation | Folders linted |
| --- | --- |
| `/lint-knowledge` from inside a project folder | that project's `Knowledge/` |
| `/lint-knowledge --scope wiki` | `{workspace_root}/Wiki/Knowledge/` and `{workspace_root}/Wiki/Contexts/` |
| `/lint-knowledge --scope vault` | the wiki scope, plus `{workspace_root}/System/Knowledge/`, every `{projects_root}/*/Knowledge/`, and every `{projects_root}/Agents/*/Knowledge/` |
| `/lint-knowledge --scope <path>` | that vault-relative file or folder |

With no flag and no project folder in the working directory, ask which scope; do not guess.

## Run

```bash
python3 <skills-dir>/knowledge-description/scripts/contract_lint.py [--cutover] <folder>...
```

`<skills-dir>` is the directory that holds this skill's folder. The tool skips `index.md` files and the Wiki's `Data/` folder during a folder walk.

Pass `--cutover` only when the operator asks whether the corpus is clear of the retired keys (`tags`, `verified`, `integration`, frontmatter `sources`), or after the cutover has removed them. Before the cutover those keys are still present on every file, and `--cutover` fails on all of them.

## Report

Group the tool's `file: rule: message` lines by rule, with a count per rule and the files under each. End with the summary line the tool prints. Exit `0` is a clean scope; say so in one line.

## Stop rules

- The tool is missing or exits `2` (usage error): report the error and stop. Do not lint by reading files yourself.
- The scope resolves to no folders: report the resolved paths and stop.

## What this skill does NOT do

- Does NOT fix findings. Fixes happen in the files, by the session that owns them; `knowledge-description` says how to write a description.
- Does NOT check links, freshness, or contradictions between files. Those duties move to the librarian agent; until it is live they are not checked automatically.
- Does NOT keep state between runs.
