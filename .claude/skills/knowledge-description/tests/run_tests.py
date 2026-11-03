#!/usr/bin/env python3
"""Tests for describe.py and contract_lint.py against the synthetic fixture vault.

Usage:
    python3 tests/run_tests.py
    python3 tests/run_tests.py -v
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).parent.resolve()
FIXTURES = TESTS_DIR / "fixtures"
SCRIPTS = TESTS_DIR.parent / "scripts"
DESCRIBE = SCRIPTS / "describe.py"
LINT = SCRIPTS / "contract_lint.py"

sys.path.insert(0, str(SCRIPTS))
import knowledge_frontmatter as kf  # noqa: E402


def run(script, *args):
    return subprocess.run(
        [sys.executable, "-B", str(script), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def broken_yaml_dir(tmp):
    """Materialise the *.md.txt fixtures as .md files (broken YAML can't live as .md in-repo)."""
    out = Path(tmp) / "broken"
    out.mkdir()
    for src in (FIXTURES / "violations").glob("*.md.txt"):
        (out / src.name[: -len(".txt")]).write_text(src.read_text())
    return out


def tree_digest(root):
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        h.update(str(p.relative_to(root)).encode())
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()


def lint_findings(proc):
    """Parse stdout into {filename: [rule, ...]} (filename without folders)."""
    found = {}
    for line in proc.stdout.splitlines():
        path, rule, _ = line.split(": ", 2)
        found.setdefault(Path(path).name, []).append(rule)
    return found


class DescribeTests(unittest.TestCase):
    def test_matches_expected_output(self):
        proc = run(DESCRIBE, FIXTURES / "vault" / "Wiki")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, (FIXTURES / "describe-expected.txt").read_text())
        self.assertEqual(proc.stderr, "")

    def test_one_line_per_file_with_related_indented(self):
        out = run(DESCRIBE, FIXTURES / "vault" / "Wiki").stdout.splitlines()
        file_lines = [ln for ln in out if not ln.startswith("    ")]
        md = [p for p in (FIXTURES / "vault" / "Wiki").rglob("*.md")]
        listed = [p for p in md if not p.name.startswith(".")]
        self.assertEqual(len(file_lines), len(listed))
        self.assertIn("    [[Reference/soil-ph|why compost acidity matters]]", out)

    def test_purpose_present_and_omitted(self):
        out = run(DESCRIBE, FIXTURES / "vault" / "Wiki").stdout
        self.assertIn("Methods/composting.md — Methods · updated 2026-03-14 — ", out)
        self.assertIn("Notes/loose-thoughts.md — updated 2026-07-04 — ", out)

    def test_purpose_from_nested_ancestor_and_scanned_folder_name(self):
        out = run(DESCRIBE, FIXTURES / "vault" / "Wiki").stdout
        self.assertIn("Methods/nested/deep-watering.md — Methods · ", out)
        out = run(DESCRIBE, FIXTURES / "vault" / "Wiki" / "Methods").stdout
        self.assertIn("composting.md — Methods · ", out)

    def test_folders_above_scanned_folder_do_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Research" / "box"
            root.mkdir(parents=True)
            (root / "a.md").write_text("---\ndescription: x\n---\n")
            out = run(DESCRIBE, root).stdout
            self.assertEqual(out, "a.md — updated unknown — x\n")

    def test_heading_fallback_ignores_fenced_code(self):
        out = run(DESCRIBE, FIXTURES / "vault" / "Wiki").stdout
        self.assertIn(
            "Reference/no-description.md — Reference · updated 2026-01-20 — Frost dates\n",
            out,
        )

    def test_no_description_literal_when_no_heading(self):
        out = run(DESCRIBE, FIXTURES / "vault" / "Wiki").stdout
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "bare.md").write_text("no heading here\n")
            self.assertEqual(
                run(DESCRIBE, tmp).stdout,
                "bare.md — updated unknown — (no description)\n",
            )
        self.assertIn("Data/seed-order.md — updated unknown — Seed order\n", out)

    def test_block_scalar_description_collapsed_to_one_line(self):
        out = run(DESCRIBE, FIXTURES / "vault" / "Wiki").stdout
        self.assertIn("test a bed. Second paragraph on amendments.\n", out)

    def test_hidden_files_skipped_and_ordering_is_codepoint(self):
        lines = [
            ln.split(" — ")[0]
            for ln in run(DESCRIBE, FIXTURES / "vault" / "Wiki").stdout.splitlines()
            if not ln.startswith("    ")
        ]
        self.assertNotIn(".hidden-note.md", lines)
        self.assertEqual(lines, sorted(lines))
        self.assertEqual(lines[-1], "index.md")

    def test_writes_nothing(self):
        before = tree_digest(FIXTURES)
        run(DESCRIBE, FIXTURES / "vault" / "Wiki")
        run(DESCRIBE, FIXTURES / "violations")
        self.assertEqual(tree_digest(FIXTURES), before)

    def test_unreadable_frontmatter_still_listed_with_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run(DESCRIBE, broken_yaml_dir(tmp))
        self.assertEqual(proc.returncode, 0)
        self.assertIn(
            "yaml-colon.md — updated unknown — (no description)\n", proc.stdout
        )
        self.assertIn("yaml-colon.md: frontmatter unreadable (", proc.stderr)

    def test_not_a_folder_exits_2_with_empty_stdout(self):
        proc = run(DESCRIBE, FIXTURES / "nope")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, "")

    def test_empty_folder_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run(DESCRIBE, tmp)
            self.assertEqual((proc.returncode, proc.stdout), (0, ""))


class LintTests(unittest.TestCase):
    def test_clean_vault_files_pass(self):
        proc = run(
            LINT,
            FIXTURES / "legacy" / "clean.md",
            FIXTURES / "vault" / "Wiki" / "Methods",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(proc.stdout, "")

    def test_vault_only_real_violations_reported(self):
        proc = run(LINT, FIXTURES / "vault")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(
            lint_findings(proc),
            {
                "no-date.md": ["updated-missing"],
                "no-description.md": ["description-missing"],
            },
        )

    def test_data_and_index_skipped_by_default_and_included_on_flag(self):
        base = lint_findings(run(LINT, FIXTURES / "vault"))
        self.assertNotIn("seed-order.md", base)
        self.assertNotIn("index.md", base)
        self.assertNotIn(".hidden-note.md", base)
        flagged = lint_findings(
            run(LINT, "--include-data", "--include-index", FIXTURES / "vault")
        )
        self.assertEqual(flagged["seed-order.md"], ["no-frontmatter"])
        self.assertEqual(flagged["index.md"], ["no-frontmatter"])

    def test_explicit_file_is_checked_even_if_data_or_index(self):
        proc = run(LINT, FIXTURES / "vault" / "Wiki" / "Data" / "seed-order.md")
        self.assertEqual(proc.returncode, 1)

    def test_each_violation_fixture_reports_its_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = lint_findings(
                run(LINT, FIXTURES / "violations", broken_yaml_dir(tmp))
            )
        expect = {
            "no-frontmatter.md": ["no-frontmatter"],
            "yaml-unclosed.md": ["yaml-parse"],
            "yaml-colon.md": ["yaml-parse"],
            "yaml-quote.md": ["yaml-parse"],
            "missing-all.md": [
                "description-missing",
                "update-missing",
                "related-missing",
                "updated-missing",
            ],
            "description-empty.md": ["description-empty"],
            "description-type.md": ["description-type"],
            "update-invalid.md": ["update-invalid"],
            "related-type.md": ["related-type"],
            "related-entries.md": ["related-entry"] * 4,
            "updated-bad-date.md": ["updated-invalid"],
            "updated-bad-format.md": ["updated-invalid"],
        }
        self.assertEqual(found, expect)

    def test_messages_name_the_file_rule_and_problem(self):
        proc = run(LINT, FIXTURES / "violations" / "update-invalid.md")
        self.assertIn(
            "update-invalid.md: update-invalid: 'update' is 'overwrite'", proc.stdout
        )

    def test_retired_keys_allowed_without_cutover(self):
        proc = run(LINT, FIXTURES / "legacy")
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_retired_keys_fail_with_cutover(self):
        proc = run(LINT, "--cutover", FIXTURES / "legacy")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(
            lint_findings(proc),
            {"retired-keys.md": ["retired-key"] * 4},
        )

    def test_missing_path_exits_2(self):
        self.assertEqual(run(LINT, FIXTURES / "nope").returncode, 2)

    def test_writes_nothing(self):
        before = tree_digest(FIXTURES)
        run(LINT, "--cutover", "--include-data", "--include-index", FIXTURES)
        self.assertEqual(tree_digest(FIXTURES), before)


class ParserTests(unittest.TestCase):
    def parse(self, text):
        return kf.parse_frontmatter(text)

    def test_scalars_and_lists(self):
        fm = self.parse(
            "a: 1\nb: true\nc: ~\nd: [x, \"y z\"]\ne:\n  - one\n  - \"two\"\nf: 'it''s'"
        )
        self.assertEqual(fm["a"], 1)
        self.assertIs(fm["b"], True)
        self.assertIsNone(fm["c"])
        self.assertEqual(fm["d"], ["x", "y z"])
        self.assertEqual(fm["e"], ["one", "two"])
        self.assertEqual(fm["f"], "it's")

    def test_list_at_key_indent(self):
        self.assertEqual(
            self.parse('related:\n- "[[a|b]]"\nupdated: 2026-01-01')["related"],
            ["[[a|b]]"],
        )

    def test_comments_and_quoted_hash(self):
        fm = self.parse('a: plain # trailing\nb: "has # inside"\n# whole line')
        self.assertEqual(fm["a"], "plain")
        self.assertEqual(fm["b"], "has # inside")

    def test_multiline_quoted_and_plain(self):
        fm = self.parse('a: "first\n  second"\nb: first\n  second')
        self.assertEqual(fm["a"], "first second")
        self.assertEqual(fm["b"], "first second")

    def test_crlf_and_bom(self):
        fm_text, body = kf.split_frontmatter(
            "﻿---\r\nupdated: 2026-01-01\r\n---\r\n# T\r\n"
        )
        self.assertEqual(self.parse(fm_text)["updated"], "2026-01-01")
        self.assertEqual(kf.first_heading(body), "T")

    def test_mapping_items_and_nested_structures_are_accepted(self):
        fm = self.parse(
            "sources:\n  - title: x\n    url: y\n  - title: z\n    url: w\n"
            "foo:\n  bar:\n    - x\n    - y\n  baz: 1\n"
            "tags:\n- topic/a\n- topic/b\nupdated: 2026-01-01"
        )
        self.assertEqual(len(fm["sources"]), 2)
        self.assertIsInstance(fm["foo"], dict)
        self.assertEqual(fm["tags"], ["topic/a", "topic/b"])
        self.assertEqual(fm["updated"], "2026-01-01")

    def test_quoted_list_entry_wrapping_lines(self):
        fm = self.parse(
            'sources:\n  - "first line\n    second line"\n  - plain\nupdated: 2026-01-01'
        )
        self.assertEqual(fm["sources"], ["first line second line", "plain"])

    def test_errors(self):
        for bad in (
            "a: b: c",
            "a: @x",
            "a: *x",
            "a: [1, 2",
            "a: 1\na: 2",
            "\tx: 1",
            "  x: 1",
            "just text",
            "a: 'open",
        ):
            with self.assertRaises(kf.FrontmatterError, msg=bad):
                self.parse(bad)

    def test_first_heading_skips_fenced_code(self):
        body = "intro\n\n```text\n# fake\n```\n\n# Real ##\n"
        self.assertEqual(kf.first_heading(body), "Real")
        self.assertIsNone(kf.first_heading("## only h2\n"))

    def test_no_frontmatter_and_unclosed(self):
        self.assertEqual(kf.split_frontmatter("# T\n")[0], None)
        with self.assertRaises(kf.FrontmatterError):
            kf.split_frontmatter("---\na: 1\n")


if __name__ == "__main__":
    unittest.main()
