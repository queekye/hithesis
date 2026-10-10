#!/usr/bin/env python3
"""Build a deterministic, allowlisted ready-to-use student distribution.

Only synthetic starter files, extension source, official runtime/source,
scripts and public documentation are included. No recursive content discovery.
"""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "hithesis.dtx", "hithesis.ins", "README.md", "UPSTREAM-README.md", "OPTIONS.md",
    "FORK-NOTES.md", "CHANGES.md", "LICENSE", "VALIDATION.md", "REVIEW.md",
    "VALIDATION-RESULTS.json", "REVIEW-MANIFEST.json",
    "LICENSES/LPPL-1.3a.txt", "LICENSES/LPPL-1.3c.txt", "LICENSES/CC-BY-NC-4.0.txt",
    "scripts/prepare-student-windows.cmd", "scripts/prepare-student-windows.ps1",
    "scripts/prepare-student.sh", "scripts/build-student-windows.cmd",
    "scripts/build-student-windows.ps1", "scripts/remove_pdf_page_links.py",
    "scripts/requirements-pdf.txt",
    "student/hithesisbook.cls", "student/hithesisbook.cfg", "student/hithesis.sty",
    "student/hithesis.bst", "student/hithesis.ist",
    "student/hitthesis-student.cls", "student/hitstudent-core.sty",
    "student/hitlayoutc.sty", "student/hitstudent-backmatter.sty",
    "student/hitwordbackmatter.sty", "student/gbt7714-numerical-quanjiao.bst",
    "student/thesis.tex", "student/front/cover.tex", "student/body/chapter01.tex",
    "student/reference.bib", "student/back/publications.tex",
    "student/back/acknowledgements.tex", "student/back/resolution-guide.tex",
    "student/back/resolution-word.tex", "student/back/authorization-guide.tex",
    "student/back/authorization-word.tex", "student/back/ai-tools.tex",
]
PREFIX = "hitthesis-student/"
FIXED_TIME = (2026, 10, 9, 0, 0, 0)


def main():
    sources = []
    for name in sorted(FILES):
        source = ROOT / name
        if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(ROOT):
            raise SystemExit(f"Missing or unsafe release file: {name}; prepare runtime and review first")
        sources.append((name, source.read_bytes()))
    manifest = "".join(f"{hashlib.sha256(data).hexdigest()}  {name}\n" for name, data in sources)
    sources.append(("SHA256SUMS", manifest.encode("utf-8")))
    output = ROOT / "dist" / "hitthesis-student-v1.0.0.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sources:
            entry = zipfile.ZipInfo(PREFIX + name, FIXED_TIME)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = (0o100644 << 16)
            archive.writestr(entry, data)
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad:
            raise SystemExit(f"Corrupt archive entry: {bad}")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".zip.sha256").write_text(digest + "  " + output.name + "\n", encoding="ascii")
    print(f"{output.name}: {len(sources)} files, SHA256 {digest}")


if __name__ == "__main__":
    main()
