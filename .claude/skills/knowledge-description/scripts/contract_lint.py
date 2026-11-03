#!/usr/bin/env python3
"""contract_lint.py — check knowledge files against the frontmatter contract.

Usage: contract_lint.py [--cutover] [--include-data] [--include-index] PATH...

Each PATH is a file or a folder. Exits 0 when clean, 1 on violations, 2 on a
usage error. Read-only. The contract lives in spec/knowledge-files.md; the rule
ids printed here are listed in ../references/lint-rules.md.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_frontmatter import read_file  # noqa: E402

UPDATE_VALUES = ("append", "replace", "never")
RETIRED_KEYS = ("tags", "verified", "integration", "sources")
# target: no brackets or pipes. reason: no pipe, and no "]]" before the closing one.
RELATED_RE = re.compile(r"^\[\[([^\[\]|]+)\|((?:(?!\]\])[^|])+)\]\]$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_wiki_data(path):
    parts = path.resolve().parts
    return any(a == "Wiki" and b == "Data" for a, b in zip(parts, parts[1:]))


def collect(paths, include_data, include_index):
    files, seen = [], set()
    for arg in paths:
        p = Path(arg)
        if p.is_file():
            candidates = [p]
        else:
            candidates = []
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
                for name in sorted(filenames):
                    if name.endswith(".md") and not name.startswith("."):
                        f = Path(dirpath) / name
                        if name == "index.md" and not include_index:
                            continue
                        if is_wiki_data(f) and not include_data:
                            continue
                        candidates.append(f)
        for f in candidates:
            key = f.resolve()
            if key not in seen:
                seen.add(key)
                files.append(f)
    return files


def check_file(path, cutover):
    """Return a list of (rule, message) violations for one file."""
    fm, _, error = read_file(path)
    if error:
        return [("yaml-parse", error)]
    if fm is None:
        return [("no-frontmatter", "file has no frontmatter block")]
    out = []

    desc = fm.get("description")
    if "description" not in fm:
        out.append(("description-missing", "missing required key 'description'"))
    elif not isinstance(desc, str):
        out.append(("description-type", "'description' must be a string"))
    elif not desc.strip():
        out.append(("description-empty", "'description' is empty"))

    if "update" not in fm:
        out.append(("update-missing", "missing required key 'update'"))
    elif fm["update"] not in UPDATE_VALUES:
        out.append(
            (
                "update-invalid",
                f"'update' is {fm['update']!r}; must be one of {', '.join(UPDATE_VALUES)}",
            )
        )

    related = fm.get("related")
    if "related" not in fm:
        out.append(
            ("related-missing", "missing required key 'related' (use [] if none)")
        )
    elif not isinstance(related, list):
        out.append(("related-type", "'related' must be a list"))
    else:
        for n, entry in enumerate(related, 1):
            if isinstance(entry, list):
                out.append(
                    (
                        "related-entry",
                        f"related entry {n} parsed as a nested list; quote it as a string",
                    )
                )
            elif not isinstance(entry, str):
                out.append(("related-entry", f"related entry {n} must be a string"))
            elif not RELATED_RE.match(entry.strip()):
                out.append(
                    (
                        "related-entry",
                        f"related entry {n} {entry!r} is not an aliased wikilink [[target|reason]]",
                    )
                )

    updated = fm.get("updated")
    if "updated" not in fm:
        out.append(("updated-missing", "missing required key 'updated'"))
    elif not _valid_date(updated):
        out.append(("updated-invalid", f"'updated' is {updated!r}; must be YYYY-MM-DD"))

    if cutover:
        for key in RETIRED_KEYS:
            if key in fm:
                out.append(("retired-key", f"retired key '{key}' present (--cutover)"))
    return out


def _valid_date(value):
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def main(argv):
    ap = argparse.ArgumentParser(
        description="Check knowledge files against the contract."
    )
    ap.add_argument("paths", nargs="+", metavar="PATH")
    ap.add_argument("--cutover", action="store_true", help="also fail on retired keys")
    ap.add_argument(
        "--include-data", action="store_true", help="also check Wiki/Data records"
    )
    ap.add_argument(
        "--include-index", action="store_true", help="also check index.md files"
    )
    args = ap.parse_args(argv[1:])

    missing = [p for p in args.paths if not Path(p).exists()]
    if missing:
        print(f"contract_lint.py: no such path: {', '.join(missing)}", file=sys.stderr)
        return 2

    files = collect(args.paths, args.include_data, args.include_index)
    bad = 0
    total = 0
    for f in files:
        violations = check_file(f, args.cutover)
        for rule, message in violations:
            print(f"{f}: {rule}: {message}")
        bad += 1 if violations else 0
        total += len(violations)
    print(
        f"checked {len(files)} files: {bad} with violations ({total} total)",
        file=sys.stderr,
    )
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
