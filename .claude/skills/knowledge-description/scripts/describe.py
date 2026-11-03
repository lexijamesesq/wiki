#!/usr/bin/env python3
"""describe.py — one line per knowledge file: what it is, when it changed, why read it.

Usage: describe.py <folder>

Read-only. Output format, ordering and fallbacks are specified in
../references/describe-output-spec.md; that spec is the contract.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_frontmatter import first_heading, read_file  # noqa: E402

PURPOSE_FOLDERS = ("Methods", "Reference", "Research", "Decisions", "Records")
NO_DESCRIPTION = "(no description)"
UNKNOWN_DATE = "unknown"


def collect(root):
    """All .md files under root, hidden directories skipped, sorted by path."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if name.endswith(".md") and not name.startswith("."):
                found.append(Path(dirpath) / name)
    return sorted(found, key=lambda p: p.relative_to(root).as_posix())


def purpose_of(root, path):
    """Nearest enclosing type folder, looking from the scanned folder's own name down."""
    parts = (root.name,) + path.relative_to(root).parts[:-1]
    for part in reversed(parts):
        if part in PURPOSE_FOLDERS:
            return part
    return None


def one_line(value):
    return " ".join(str(value).split())


def describe_file(root, path):
    """Return (lines, warning | None) for one file."""
    fm, body, error = read_file(path)
    fm = fm or {}
    desc = fm.get("description")
    text = one_line(desc) if isinstance(desc, str) and desc.strip() else ""
    if not text:
        text = first_heading(body) or NO_DESCRIPTION
    updated = fm.get("updated")
    updated = one_line(updated) if updated not in (None, "") else UNKNOWN_DATE
    purpose = purpose_of(root, path)
    rel = path.relative_to(root).as_posix()
    head = f"{rel} — "
    if purpose:
        head += f"{purpose} · "
    lines = [f"{head}updated {updated} — {text}"]
    related = fm.get("related")
    if isinstance(related, list):
        lines += [
            f"    {one_line(r)}" for r in related if isinstance(r, str) and r.strip()
        ]
    warning = f"{rel}: frontmatter unreadable ({error})" if error else None
    return lines, warning


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print("usage: describe.py <folder>", file=sys.stderr)
        return 2
    root = Path(argv[1])
    if not root.is_dir():
        print(f"describe.py: not a folder: {argv[1]}", file=sys.stderr)
        return 2
    root = root.resolve()
    for path in collect(root):
        lines, warning = describe_file(root, path)
        print("\n".join(lines))
        if warning:
            print(warning, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
