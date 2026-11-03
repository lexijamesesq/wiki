# Contract lint: rules and flags

`contract_lint.py` checks knowledge files against the frontmatter contract in
`spec/knowledge-files.md`. Output is one line per violation on stdout,
`<file>: <rule>: <message>`, and a summary on stderr. Exit `0` clean, `1` violations,
`2` usage error.

## Required frontmatter

| Rule id | Fails when |
| --- | --- |
| `no-frontmatter` | the file has no `---` block |
| `yaml-parse` | the block is not valid YAML, or never closes |
| `description-missing` / `description-type` / `description-empty` | `description` is absent, not a string, or blank |
| `update-missing` / `update-invalid` | `update` is absent or not one of `append`, `replace`, `never` |
| `related-missing` / `related-type` | `related` is absent or not a list (`[]` is fine) |
| `related-entry` | an entry is not a string of the form `[[target\|reason]]`. An unquoted `[[a\|b]]` parses as a nested list and fails here; quote it |
| `updated-missing` / `updated-invalid` | `updated` is absent or not a real `YYYY-MM-DD` date |

The reason may be any text without `|` or `]]`; its length is not checked. Unknown keys are allowed.

## Retired keys

`retired-key` fires only with `--cutover`, for `tags`, `verified`, `integration`,
and `sources`. Without the flag they pass, so a corpus can be migrated in stages.

## What gets scanned

Folders are walked recursively for `.md` files; hidden directories are skipped.
During a walk, `index.md` files and anything under a `Wiki/Data` directory are
skipped unless `--include-index` / `--include-data` is given. A file named
explicitly on the command line is always checked.
