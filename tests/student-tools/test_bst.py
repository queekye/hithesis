"""Exercise optional BST output with synthetic entries using existing BibTeX."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
STYLE = ROOT / "student" / "gbt7714-numerical-quanjiao.bst"
FIXTURE = Path(__file__).with_name("conference-fixture.bib")
UPSTREAM_STYLE = ROOT / "examples" / "hitbook" / "chinese" / STYLE.name


class StudentBstTests(unittest.TestCase):
    def run_bibtex(self, style: str) -> str:
        bibtex = shutil.which("bibtex")
        if not bibtex:
            self.skipTest("BibTeX is not installed; no dependency installation is attempted")
        with tempfile.TemporaryDirectory(prefix="student-bst-") as temporary:
            directory = Path(temporary)
            (directory / STYLE.name).write_text(style, encoding="utf-8")
            shutil.copyfile(FIXTURE, directory / "fixture.bib")
            (directory / "fixture.aux").write_text(
                "\\relax\n\\citation{*}\n\\bibstyle{gbt7714-numerical-quanjiao}\n"
                "\\bibdata{fixture}\n", encoding="ascii")
            environment = os.environ.copy()
            result = subprocess.run([bibtex, "fixture"], cwd=directory, env=environment,
                                    capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", check=False)
            log = (directory / "fixture.blg").read_text(encoding="utf-8", errors="replace")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr + log)
            self.assertNotRegex(log, r"(?im)^Warning--|error message|literal stack|unknown function")
            return (directory / "fixture.bbl").read_text(encoding="utf-8")

    def test_optional_style_preserves_complete_conference_fields(self) -> None:
        output = self.run_bibtex(STYLE.read_text(encoding="utf-8"))
        for text in ("Synthetic conference contribution", "Synthetic Student Conference",
                     "Example City", "Example Press", "2025", "101", "109",
                     "example.org/student-paper", "10.0000/synthetic.2025.101", "2026-10-09",
                     "Synthetic conference alias entry", "Synthetic Alias Conference",
                     "Synthetic journal control", "Synthetic Journal"):
            self.assertIn(text, output)
        self.assertIn("［C/OL］", output)
        self.assertIn("［C］", output)
        self.assertIn("［J］", output)
        self.assertIn("2nd ed", output)

    def test_individual_display_flags_can_hide_url_doi_and_access_date(self) -> None:
        style = STYLE.read_text(encoding="utf-8")
        for name in ("show.urldate", "show.url", "show.doi"):
            style, replacements = re.subn(r"#1 '" + re.escape(name) + r" :=", "#0 '" + name + " :=", style)
            self.assertEqual(replacements, 1)
        output = self.run_bibtex(style)
        for text in ("example.org/student-paper", "10.0000/synthetic.2025.101", "2026-10-09"):
            self.assertNotIn(text, output)
        self.assertIn("Synthetic Student Conference", output)
        self.assertIn("Example Press", output)

    def test_journal_entry_matches_unmodified_upstream_style(self) -> None:
        optional = self.run_bibtex(STYLE.read_text(encoding="utf-8"))
        upstream = self.run_bibtex(UPSTREAM_STYLE.read_text(encoding="utf-8"))
        self.assertIn("EDITOR E", optional)
        self.assertEqual(optional, upstream)


if __name__ == "__main__":
    unittest.main()
