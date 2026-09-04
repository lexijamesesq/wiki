# CI workflow shape

Follows dotty's CI shape (`.github/CI.md` there) for the general conventions
— least-privilege `permissions:`, `concurrency:`, `timeout-minutes`,
SHA-pinned actions, the shared gitleaks composite. This repo records only
what's specific to it.

## Decisions specific to this repo

**`gate` (`ci.yml`, `pull_request`) is the pre-existing conformance check**
— `claude plugin validate --strict`, lint-knowledge tests, diff-scoped
house-qa, a base-rules gitleaks scan. Unchanged by the release job below.

**Release job — see work-lifecycle's `CI.md` for the full design** (this
repo publishes one plugin, `wiki`, from its own root; work-lifecycle
publishes two from its `plugins/` tree — the mechanism is identical). Two
pieces, split across files on purpose:

- `release-check` joins `ci.yml` as a second job on the same
  `pull_request` trigger `gate` already uses — required by this repo's
  branch-protection ruleset (appended to its existing `gate` requirement,
  strict). Compares the plugin's tree against its highest existing tag;
  fails loud if content changed with no version bump.
- `release.yml` is a **separate file**, `push`-triggered only. Adding a
  push trigger to `ci.yml` itself would make `gate`'s `BASE_SHA` scoping
  (computed from the PR event) vacuous on a push event — this repo's own
  version of the gotcha work-lifecycle's `CI.md` names for dotty-private.
  Cuts the tag + GitHub Release once a version lands untagged.

Both jobs invoke `work-lifecycle`'s `check-plugin-version.sh` /
`tag-plugin-release.sh` from a pinned checkout — same convention this
repo already uses for `qa.py` (see `ci.yml`) — rather than duplicating
the scripts here.

**First-release baseline:** `wiki--v0.1.0` — already reflects real,
intentionally-set state; no bump needed to produce a clean first tag.
