# Playbook: automated-write-plan

Pre-commit write planning for `mode: automated`. Loaded from assess-candidates step 8 — never a direct entry. In this mode the skill's ONLY direct vault writes are `/queue create-item` files; destination writes are *planned* here and never applied by this skill.

**No apply stage runs today.** The unattended lanes that validated and applied these plans are retired, and unattended writes now belong to eve agents and their own vault tools. A plan produced here is returned in the extraction report for the caller to review; nothing writes it to the vault. The shape below is kept exact so that a plan stays checkable, and so an apply step can be rebuilt against it without changing this skill.

## What files in automated mode

Only the matrix cells that say `file`: durable-knowledge (registered; resolved-unique OR resolved-multiple's defensible best home per calibration surface §5; an `update: append` target for an append — any other target was queued upstream by the update-mode guard). Everything else was queued or discarded upstream in assess-candidates.

## Plan shape (verbatim contract)

Per target:

- **NEW files:** the full composed content (the four frontmatter fields and a `## Sources` section, per assess-candidates step 7 › Filing) + **enumerated content sources** — which candidates/source items produced this file. An absent or empty enumeration is itself a plan defect (no-rollup: no new file whose substance derives from ≥2 already-filed vault files; the enumeration's *presence* is mechanical, the derivation claim stays named judgment).
- **EXISTING targets:** `{target, pre_state_hash, append_suffix}` **ONLY**. The plan never carries a rendered full state for an existing file — that makes mutation discipline mechanically checkable from the plan itself (a full-state entry for an existing target = automatic defect) and makes a whole-file overwrite structurally impossible.

`pre_state_hash` = SHA-256 of the target file's bytes on disk: `shasum -a 256 "<absolute path>"`, first field of the output. Hash the file by its path. Never hash text returned by `Read`: that copy carries line numbers and may be truncated, so its hash never matches the file, and any check against the file at write time would fail.

`append_suffix` carries: date attribution, provenance `routine/<action> <run-id>`, **plus** the human-readable source attribution, and the Sources bullets that go under the target's `## Sources` heading.

## Idempotency recheck

Immediately before planning each append, recheck the target for a `content_hash` / attribution+date match — vault sync may have delivered writes since step 2's search. Match → drop the candidate to `discard: duplicate`.

## Downstream contract (for any future apply step)

```text
plan (model — this playbook)
  → validate (separate context, never this one)
      FAIL → nothing commits; plan + reasons → quarantine queue item
  → apply (deterministic script — NOT a model)
      per append: recompute shasum -a 256 on the target at apply time and compare
      to pre_state_hash; mismatch (e.g. a sync-delivered operator edit) → abort that
      write + queue item + continue others; new files created verbatim
  → verify (post-apply)
      contract_lint.py --cutover on new files; suffix-presence check on appends;
      FAIL → quarantine queue item naming the file + expected-vs-found;
      no further writes this run — never silent, no auto-revert
```

## Output

Return to assess-candidates step 9: `write_plan` (shape above) + updated dispositions. `applied[]` stays empty.
