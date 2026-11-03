# Playbook: scope-lint

Run the contract lint over the knowledge files this session touched, at closeout. No model in the lint pass. Frontmatter findings on files the session created or edited get fixed inline; everything else is listed for the closeout summary.

## Input

- `scope_paths` — the vault paths this session touched (files or directories)
- `created_paths` — the subset of `scope_paths` this session CREATED
- `vault_root` — resolved via the `workspace_root` config key

## Protocol

1. **Keep only knowledge files.** From `scope_paths`, keep paths under a `Knowledge/` folder or `{workspace_root}/Wiki/Contexts/`. Drop everything else (CLAUDE.md, `overview.md`, `Wiki/Data`, `Wiki/Queue`, Personal/Work). Nothing left → report `scope-lint: no knowledge files touched` and stop.

2. **Run the lint** — `contract_lint.py` lives in the sibling `knowledge-description` skill (same skills directory as this skill):

   ```bash
   python3 <skills-dir>/knowledge-description/scripts/contract_lint.py --cutover <created knowledge paths...>
   python3 <skills-dir>/knowledge-description/scripts/contract_lint.py <other touched knowledge paths...>
   ```

   New files must already be free of the retired keys (`tags`, `verified`, `integration`, frontmatter `sources`), so they get `--cutover`. Files that existed before the session may still carry those keys until the one-time cutover removes them; lint them without the flag. Exit `0` on both → report `scope-lint: clean, N files` and stop.

3. **Partition and act** on the `file: rule: message` lines:
   - **Files this session created or edited** → fix the frontmatter now (`Edit`): a missing or stale `description` (write it per the `knowledge-description` skill), a missing or invalid `update`, a malformed `related` entry, a bad `updated` date. Frontmatter is editable under every update mode. Re-run step 2 on the fixed files to confirm.
   - **Files the session only read** → do not modify. List them with their findings for the closeout summary.

4. **Report** to the orchestrator: files linted, fixes applied (confirmed clean on re-run), and the remaining findings by file.

## Discipline

- **Inline-fix authority is frontmatter on files this session created or edited.** Body changes are hygiene's, under the file's update mode.
- **No model in the lint pass.** Judgment enters only at the partition step and the fix composition.

## What this playbook does NOT do

- Does NOT run whole-corpus scans — that's `/lint-knowledge`.
- Does NOT create queue items; remaining findings go in the closeout summary for the operator.
- Does NOT gate filing — the gatekeeper's lint already ran on files it filed; scope-lint is the closeout backstop across everything the session touched.
