# CI workflow shape

Follows dotty's CI shape (`.github/CI.md` there) for the general conventions
— least-privilege `permissions:`, `concurrency:`, `timeout-minutes`,
SHA-pinned actions, the shared gitleaks composite. This repo records only
what's specific to it.

## Decisions specific to this repo

**`gate` (`ci.yml`, `pull_request`) is the pre-existing conformance check**
— `claude plugin validate --strict` and the lint-knowledge tests —
alongside `floor` (this repo's caller into the estate's shared
`estate-ci.yml`, the standard pre-commit chain). PR-time secret scanning is
the trusted lane's `trusted-scan` (`gate.yml`), not a job here.

**Release job — see core-skills' `CI.md` for the full design** (this
repo publishes one plugin, `wiki`, from its own root; core-skills
publishes two from its `plugins/` tree — the mechanism is identical).
Both pieces are calling jobs in `ci.yml`, invoking dotty's shared
`estate-plugin-release.yml@v1` — this repo carries neither script nor
a pinned checkout of core-skills:

- `release-check` (`pull_request`) — required by this repo's
  branch-protection ruleset (appended to its existing `gate` requirement,
  strict). Compares the plugin's tree against its highest existing tag;
  fails loud if content changed with no version bump.
- `release-tag` (`push` to `main`) cuts the tag + GitHub Release once a
  version lands untagged. No longer a separate `release.yml` file — both
  jobs now live in `ci.yml`, each gated on its own event (`gate`'s own
  PR-only scoping is unaffected; it never reads from a push event).

**First-release baseline:** `wiki--v0.1.0` — already reflects real,
intentionally-set state; no bump needed to produce a clean first tag.
