---
name: knowledge-description
description: >-
  Write and refresh the `description` of a knowledge file whenever you create or
  change one, and orient in a folder of knowledge files with the describe tool
  instead of opening every file. Also covers checking files against the
  frontmatter contract with the contract lint tool. Triggers on creating or
  editing a knowledge file, "describe this folder", "what's in this folder",
  "write a description", or "check the frontmatter".
---

# Knowledge description

A knowledge file's `description` is the line a future session reads instead of the file. It is how someone finds the file, and how a session decides whether to open it. The contract for the frontmatter lives in `spec/knowledge-files.md` at this plugin's root (`<this-skill-dir>/../../spec/knowledge-files.md`; the same file lives in the wiki repo's `spec/`). The describe tool never judges a file: unreadable frontmatter prints a heading fallback and a stderr warning, so after writing a file run the lint below, not only describe.

## Writing a description

Do this every time you create a knowledge file, and every time you change one in a way that alters what it says. A stale description is worse than none: it sends a reader to the wrong file, or past the right one.

A good description is:

- **True of this file.** Describe what the file contains now, not what it was started to be. Re-read the file's body before you refresh the line.
- **Specific to it.** If the sentence could sit on a sibling file, it is too general. Name the system, the decision, the period, the finding.
- **One or two sentences.** The first sentence says what the file is; a second only if it adds a reason to open it.
- **In the words someone would search with.** Use the terms the operator uses, product and tool names as written, not your own paraphrase.

| Weak | Better |
| --- | --- |
| Notes about the export job. | How the nightly export job is scheduled and what it writes. |
| Research on bees. | Which flowering borders drew the most bees in a two-season trial: native mixes beat annuals. |

Also set `updated` to today's date when the content changes, and check that `update` still matches how the file is meant to change (`append`, `replace`, `never`). Under `never` the body does not change; only frontmatter may.

## Orienting in a folder

Before reading files in a knowledge folder, run the describe tool. One line per file: `file — purpose · updated <date> — description`, with the file's `related` links indented beneath it.

```bash
python3 <this-skill-dir>/scripts/describe.py <folder>
```

`<this-skill-dir>` is the directory that holds this `SKILL.md`. The tool reads only; it writes nothing. Use the lines to choose which files to open, and follow `related` links when a line points at something adjacent. When a line shows a heading instead of a real description, or `(no description)`, the file needs a description: write one.

The output format is specified in `references/describe-output-spec.md`.

## Checking the contract

```bash
python3 <this-skill-dir>/scripts/contract_lint.py <file-or-folder>...
python3 <this-skill-dir>/scripts/contract_lint.py --cutover <folder>
```

It exits non-zero and prints `file: rule: message` per violation. Without `--cutover`, the retired keys (`tags`, `verified`, `integration`, `sources`) are allowed, so a corpus can migrate in stages; `--cutover` fails on them. `Wiki/Data` and `index.md` files are skipped during folder walks unless `--include-data` / `--include-index` is passed. Rules and flags: `references/lint-rules.md`. Fix findings in the files; do not edit the tool to pass.

Tests, run from the repo root: `python3 .claude/skills/knowledge-description/tests/run_tests.py`.
