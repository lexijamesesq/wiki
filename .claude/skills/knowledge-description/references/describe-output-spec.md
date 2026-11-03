# Describe tool: output spec

Standalone specification of `describe`, a read-only tool that orients a reader in a
folder of knowledge files. Any implementation (the reference Python script, a
native librarian) must produce identical output for the fixture vault in
`tests/fixtures/vault/` — the expected output is `tests/fixtures/describe-expected.txt`.

The frontmatter keys it reads (`description`, `updated`, `related`) are defined by
`spec/knowledge-files.md`.

## Input

One argument: a folder path. Not a folder: write a message to stderr, exit 2,
print nothing to stdout.

## What it reads

Every file whose name ends in `.md`, at any depth under the folder. Directories
and files whose names start with `.` are skipped. `index.md` files are included.
Symlinks are not specially handled. It writes nothing anywhere.

## Ordering

Files sort by their path relative to the given folder, using `/` as the
separator, by ascending Unicode code point (so `B.md` sorts before `a.md`).
Nested files interleave by full relative path; there is no per-directory grouping.

## Output

For each file, one line, in this exact shape:

```text
<path> — <purpose> · updated <date> — <description>
```

- `<path>`: the relative path, as above.
- `<purpose>`: the name of the nearest enclosing type folder, one of `Methods`,
  `Reference`, `Research`, `Decisions`, `Records` (exact, case-sensitive).
  Candidates are the file's own folders below the given folder, plus the given
  folder's own name; folders above the given folder never count. When there is
  none, omit the purpose and its trailing separator entirely, giving `<path> — updated <date> — <description>`.
- `<date>`: the `updated` value verbatim, or `unknown` when absent or empty.
- `<description>`: the `description` value with all runs of whitespace (including
  newlines from block scalars) collapsed to single spaces and trimmed. Fallback
  order when `description` is absent, empty, or not a string: the text of the
  file's first level-one heading (`# Title`), ignoring headings inside fenced code
  blocks and trimming closing `#` marks; else the literal `(no description)`.

The separators are an em dash (U+2014) with a space on each side, and a middle dot
(U+00B7) with a space on each side.

Immediately after a file's line, one line per `related` entry, in the order
written, each indented by exactly four spaces and consisting of the entry text
verbatim (whitespace-collapsed), for example four spaces then `[[target|reason]]`. Entries
that are not non-empty strings are skipped. No `related` key, or an empty list,
produces no extra lines.

Lines end with a single newline. A folder with no `.md` files produces no output
and exits 0.

## Unreadable frontmatter

A file whose frontmatter is not valid YAML (or never closes) still gets its line:
`updated unknown`, no related lines, and the description falls back to the heading
or `(no description)`. A warning `<path>: frontmatter unreadable (<reason>)` goes to
stderr. Exit status is still 0; describe reports, it does not judge. Checking
validity is the lint tool's job.

## Exit status

`0` on success, `2` on a usage error. Nothing else.
