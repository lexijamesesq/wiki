#!/usr/bin/env bash
# Track-list guard — fails the commit if any staged path's top-level component
# is not on the explicit allow-list below.
#
# Why this exists alongside .gitignore: the ignore-list is a wall around known
# content dirs, but it drifts silently — a new top-level dir (or a forgotten
# entry) simply isn't blocked until someone remembers to add it. This hook is
# the opposite shape: nothing new lands unless someone deliberately allow-lists
# it here. See {workspace_root}/System/Context/wiki-publication-boundary-map.md > Decisions #1
# (the ignore-list itself was stale the day it was written).
#
# To add a new top-level path to the public Wiki repo: confirm it belongs
# (machinery, not operator content), then add its name to ALLOW below.
#
# Kept, not retired, when this repo moved out of the vault (notes no longer
# live beside this checkout at all): the guard's actual purpose was never
# specifically "keep vault notes out" — it's general defense against ANY
# undeclared top-level path landing here (a stray secrets file, a debug
# script, an accidental tool-config directory), a purpose this repo needs
# exactly as much post-move as before.
set -euo pipefail

ALLOW=(
  ".claude"
  ".claude-plugin"
  ".house-qa.json"
  "spec"
  ".gitignore"
  "README.md"
  "LICENSE"
  "CLAUDE.md"
  ".pre-commit-config.yaml"
  ".gitleaks.toml"
  ".gitleaks.ci.toml"
  ".track-list-guard.sh"
  ".github"
)

is_allowed() {
  local top="$1"
  for a in "${ALLOW[@]}"; do
    [[ "$top" == "$a" ]] && return 0
  done
  return 1
}

violations=()
while IFS= read -r path; do
  [[ -z "$path" ]] && continue
  top="${path%%/*}"
  if ! is_allowed "$top"; then
    violations+=("$path")
  fi
done < <(git diff --cached --name-only --diff-filter=ACMR)

if [[ ${#violations[@]} -gt 0 ]]; then
  echo "Track-list guard: staged path(s) not on the allow-list:"
  printf '  %s\n' "${violations[@]}"
  echo ""
  echo "Allow-list: ${ALLOW[*]}"
  echo "If this path genuinely belongs in the public Wiki repo, add its top-level"
  echo "name deliberately to .track-list-guard.sh. Otherwise it's operator content —"
  echo "add it to .gitignore instead."
  exit 1
fi

exit 0
