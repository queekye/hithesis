#!/usr/bin/env python3
"""Compile synthetic student fixtures and reject unsafe Word-form overflow.

Run after generating the upstream class with scripts/prepare-student.sh or
scripts/prepare-student-windows.cmd. Requires Python with pypdf, XeLaTeX,
BibTeX, pdftotext and pdftoppm. All generated files stay under _work/student-validation.
The default run includes a raster comparison against the unchanged parent.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
STUDENT = ROOT / "student"
OUTPUT = ROOT / "_work" / "student-validation"
RESULTS: list[dict] = []


def required_tool(name: str, override: str | None) -> str:
    found = shutil.which(override or name)
    if not found:
        raise RuntimeError(f"Required tool is missing: {override or name}")
    return found


def run_command(command: list[str], cwd: Path, env: dict[str, str],
                record: Path) -> subprocess.CompletedProcess:
    completed = subprocess.run(command, cwd=cwd, env=env,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=180)
    record.write_bytes(completed.stdout)
    return completed


def compile_case(name: str, source: str, *, rejection: str | None = None,
                 bibliography: bool = False) -> Path | None:
    case = OUTPUT / name
    case.mkdir(parents=True, exist_ok=True)
    assert case.resolve().is_relative_to(OUTPUT.resolve()), "Output path escaped validation directory"
    # Only this fixture's generated single files are removed, never recursively.
    # A stale PDF/auxiliary file must not make a broken rerun appear successful.
    for previous in case.glob(f"{name}.*"):
        if previous.is_file():
            assert previous.resolve().parent == case.resolve(), "Unexpected output file target"
            previous.unlink()
    tex = case / f"{name}.tex"
    tex.write_text(source, encoding="utf-8")
    command = [ARGS.xelatex, "-interaction=nonstopmode", "-halt-on-error",
               "-file-line-error", f"-output-directory={case}", str(tex)]
    first = run_command(command, STUDENT, ENV, case / "xelatex-pass1.txt")
    log = first.stdout.decode("utf-8", errors="replace")
    log_file = case / f"{name}.log"
    if log_file.exists():
        log += "\n" + log_file.read_text(encoding="utf-8", errors="replace")
    if rejection:
        if first.returncode == 0:
            raise AssertionError(f"{name}: invalid input compiled successfully")
        # TeX wraps long lines at max_print_line, sometimes inside a word.
        if compact(rejection) not in compact(log):
            raise AssertionError(f"{name}: failure did not contain {rejection!r}")
        return None
    if first.returncode != 0:
        raise AssertionError(f"{name}: XeLaTeX pass 1 failed; see {case}")
    if bibliography:
        bib = run_command([ARGS.bibtex, name], case, ENV, case / "bibtex.txt")
        if bib.returncode != 0:
            raise AssertionError(f"{name}: BibTeX failed; see {case}")
    for pass_number in (2, 3):
        completed = run_command(command, STUDENT, ENV,
                                case / f"xelatex-pass{pass_number}.txt")
        if completed.returncode != 0:
            raise AssertionError(f"{name}: XeLaTeX pass {pass_number} failed; see {case}")
    pdf = case / f"{name}.pdf"
    if not pdf.is_file() or not PdfReader(pdf).pages:
        raise AssertionError(f"{name}: PDF is missing or empty")
    final_log = log_file.read_text(encoding="utf-8", errors="replace")
    for issue in ("There were undefined references", "There were undefined citations",
                  "Citation ", "Label(s) may have changed"):
        if issue in final_log:
            raise AssertionError(f"{name}: unresolved output after three passes: {issue}")
    return pdf


def pdf_text(pdf: Path) -> str:
    target = pdf.with_suffix(".extracted.txt")
    completed = run_command([ARGS.pdftotext, "-enc", "UTF-8", str(pdf), str(target)],
                            STUDENT, ENV, pdf.parent / "pdftotext.txt")
    if completed.returncode != 0 or not target.exists():
        raise AssertionError(f"pdftotext failed for {pdf}")
    return target.read_text(encoding="utf-8")


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def evaluate(name: str, action) -> None:
    started = time.monotonic()
    result = {"case": name, "passed": False}
    try:
        detail = action()
        result.update(passed=True, detail=detail or "passed")
    except (AssertionError, RuntimeError, subprocess.TimeoutExpired, OSError,
            ValueError) as error:
        result["detail"] = str(error)
    result["seconds"] = round(time.monotonic() - started, 2)
    for index, previous in enumerate(RESULTS):
        if previous["case"] == name:
            RESULTS[index] = result
            break
    else:
        RESULTS.append(result)
    print(f"{'PASS' if result['passed'] else 'FAIL'} {name}: {result['detail']}",
          flush=True)
    (OUTPUT / "results.json").write_text(
        json.dumps(RESULTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def core_fixture(name: str) -> None:
    source = (ROOT / "tests" / "student-core" / f"{name}.tex").read_text(encoding="utf-8")
    pdf = compile_case(f"core-{name}", source)
    assert pdf is not None
    text = compact(pdf_text(pdf))
    if name == "guide-academic":
        assert "对使用AI工具的情况均已在文中以明确方式标注" in text, \
            "Updated official declaration is absent from PDF text"


def rejected_core(name: str, message: str) -> str:
    source = (ROOT / "tests" / "student-core" / f"{name}.tex").read_text(encoding="utf-8")
    compile_case(f"core-{name}", source, rejection=message)
    return f"rejected with {message}"


def starter(name: str, substitutions: tuple[tuple[str, str], ...] = (),
            anonymous: bool = False) -> str:
    source = (STUDENT / "thesis.tex").read_text(encoding="utf-8")
    for old, new in substitutions:
        if old not in source:
            raise AssertionError(f"Missing fixture substitution {old!r}")
        source = source.replace(old, new)
    pdf = compile_case(f"starter-{name}", source, bibliography=True)
    assert pdf is not None
    reader = PdfReader(pdf)
    text = compact(pdf_text(pdf))
    if anonymous:
        for identity in ("示例学生", "Example Student", "示例导师", "Professor Example", "DEMO-ONLY"):
            assert compact(identity) not in text, f"Anonymous PDF leaks {identity!r}"
        assert not (reader.metadata or {}).get("/Author"), "Anonymous PDF has an author metadata field"
        for backmatter in ("示例委员甲", "示例秘书", "AI工具使用说明", "答辩委员会决议"):
            assert compact(backmatter) not in text, f"Anonymous PDF includes back matter {backmatter!r}"
    else:
        assert "对使用AI工具的情况均已在文中以明确方式标注" in text, \
            "Updated official declaration is absent from starter PDF"
        assert "ExampleStudent" in text and "示例学生" in text, \
            "Nonanonymous synthetic identity disappeared"
        bbl = pdf.with_suffix(".bbl").read_text(encoding="utf-8")
        assert "[C]" in bbl or "［C］" in bbl, "Conference entry has no [C] marker"
        for bibliography_value in ("Example Conference", "Example Press"):
            assert bibliography_value in bbl, f"Conference field omitted: {bibliography_value}"
        assert re.search(r"10-+20", bbl), "Conference page range was omitted"
    return f"{len(reader.pages)} pages; text and bibliography checks passed"


WORD_PREAMBLE = r"""\documentclass[type=doctor,campus=harbin,fontset=fandol,tocblank=false]{hitthesis-student}
\usepackage[mode=word]{hitstudent-backmatter}
\begin{document}
"""


def word_rejection(name: str, rows: str, decision: str, expected: str,
                   setup: str = "") -> str:
    preamble = WORD_PREAMBLE
    if name == "master-scope":
        preamble = preamble.replace("type=doctor", "type=master")
    source = (preamble + setup + "\n\\begin{resolutiontext}\n"
              + "\\hitwordresolution{" + rows + "}{" + decision + "}\n"
              + "\\end{resolutiontext}\n\\end{document}\n")
    compile_case(f"word-reject-{name}", source, rejection=expected)
    return f"rejected with {expected}"


def guide_continuation() -> str:
    rows = "\n".join(r"\hitcommitteerow{委员}{虚构委员}{教授（是）}{示例单位}{示例学科}"
                     for _ in range(80))
    paragraphs = "\n\n".join("这是合成决议的续页测试段落。" * 8 for _ in range(40))
    source = (WORD_PREAMBLE.replace("mode=word", "mode=guide")
              + "\\begin{resolutiontext}\n\\begin{hitcommittee}\n" + rows
              + "\n\\end{hitcommittee}\n" + paragraphs
              + "\n\n合成续页末尾标记。\n\\end{resolutiontext}\n\\end{document}\n")
    pdf = compile_case("guide-continuation", source)
    assert pdf is not None
    reader = PdfReader(pdf)
    assert len(reader.pages) >= 5, "Long native back matter did not flow onto multiple pages"
    text = compact(pdf_text(pdf))
    assert text.count("虚构委员") == 80, "Native committee list lost or duplicated rows"
    assert text.count("职务") >= 2, "Committee headings were not repeated on continuation pages"
    assert text.count("这是合成决议的续页测试段落。") == 320, "Native decision lost or duplicated text"
    assert "合成续页末尾标记" in text, "Native back matter lost its last paragraph"
    return f"{len(reader.pages)} pages; 80 rows and 320 sentences retained"


def upstream_pixels() -> str:
    source = (ROOT / "tests" / "student-core" / "default.tex").read_text(encoding="utf-8")
    wrapper = compile_case("pixels-wrapper", source)
    parent = source.replace(",fixhidden=false", "").replace("{hitthesis-student}", "{hithesisbook}", 1)
    parent = re.sub(r"\\makeatletter.*?\\makeatother\s*", "", parent, count=1, flags=re.S)
    parent = parent.replace(r"\hitanonymousTF", r"\takeSecond")
    parent = parent.replace(r"\hitsetup{", "\\newcommand{\\takeSecond}[2]{#2}\n\\hitsetup{", 1)
    baseline = compile_case("pixels-upstream", parent)
    assert wrapper is not None and baseline is not None
    counts = []
    rendered = []
    for pdf in (wrapper, baseline):
        target = pdf.parent / "raster"
        target.mkdir(exist_ok=True)
        assert target.resolve().is_relative_to(OUTPUT.resolve()), "Raster path escaped validation directory"
        for previous in target.glob("page-*.ppm"):
            if previous.is_file():
                assert previous.resolve().parent == target.resolve(), "Unexpected raster target"
                previous.unlink()
        completed = run_command([ARGS.pdftoppm, "-r", "100", str(pdf), str(target / "page")],
                                STUDENT, ENV, pdf.parent / "pdftoppm.txt")
        assert completed.returncode == 0, f"pdftoppm failed for {pdf}"
        pages = sorted(target.glob("page-*.ppm"), key=lambda p: int(p.stem.split("-")[-1]))
        assert pages, f"pdftoppm produced no pages for {pdf}"
        assert len(pages) == len(PdfReader(pdf).pages), "Raster file count differs from the current PDF page count"
        counts.append(len(pages))
        rendered.append(pages)
    assert counts[0] == counts[1], f"Wrapper changed page count: {counts}"
    for index, (actual, expected) in enumerate(zip(*rendered), 1):
        assert actual.read_bytes() == expected.read_bytes(), \
            f"Default wrapper changed pixels on page {index} at 100 dpi"
    return f"{counts[0]} pages are byte-identical at 100 dpi"


def main() -> int:
    global ARGS, ENV
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xelatex")
    parser.add_argument("--bibtex")
    parser.add_argument("--pdftotext")
    parser.add_argument("--pdftoppm")
    parser.add_argument("--case", action="append", help="Run named cases only (repeatable)")
    ARGS = parser.parse_args()
    ARGS.xelatex = required_tool("xelatex", ARGS.xelatex)
    ARGS.bibtex = required_tool("bibtex", ARGS.bibtex)
    ARGS.pdftotext = required_tool("pdftotext", ARGS.pdftotext)
    ARGS.pdftoppm = required_tool("pdftoppm", ARGS.pdftoppm)
    for runtime in ("hithesisbook.cls", "hithesisbook.cfg", "hithesis.sty", "hithesis.bst"):
        if not (STUDENT / runtime).is_file() and not (ROOT / runtime).is_file():
            raise RuntimeError(f"Generate the upstream runtime before validation: {runtime}")
    ENV = os.environ.copy()
    # Preserve default TeX search paths with the trailing empty path element.
    for variable in ("TEXINPUTS", "BSTINPUTS", "BIBINPUTS"):
        ENV[variable] = os.pathsep.join((str(STUDENT), str(ROOT), ENV.get(variable, ""), ""))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    # Targeted retries retain the independent successful cases and replace only
    # the selected results, so the final report can show the complete matrix.
    existing_results = OUTPUT / "results.json"
    if ARGS.case and existing_results.exists():
        previous = json.loads(existing_results.read_text(encoding="utf-8"))
        if not isinstance(previous, list) or any(
                not isinstance(item, dict) or "case" not in item for item in previous):
            raise RuntimeError("Previous results.json has an unexpected format")
        RESULTS.extend(previous)
    cases = {}
    for name in ("default", "flags-standalone", "guide-academic", "guide-professional-anonymous"):
        cases[f"core-{name}"] = lambda name=name: core_fixture(name)
    for name, message in (("invalid-degreecategory", "Invalid degreecategory"),
                          ("invalid-layout", "Invalid layout"),
                          ("unsupported-campus", "requires Harbin master or doctor")):
        cases[f"core-{name}"] = lambda name=name, message=message: rejected_core(name, message)
    degree_types = (("doctor-academic", ()),
                    ("master-academic", (("type=doctor", "type=master"),)),
                    ("master-professional", (("type=doctor", "type=master"),
                                              ("degreecategory=academic", "degreecategory=professional"))),
                    ("doctor-professional", (("degreecategory=academic", "degreecategory=professional"),)),
                    ("anonymous", (("guide2025=true", "guide2025=true,anonymous=true"),)),
                    ("layout-c", (("layout=upstream", "layout=c"),)),
                    ("word", (("mode=guide", "mode=word"),
                              ("back/resolution-guide", "back/resolution-word"),
                              ("back/authorization-guide", "back/authorization-word"))),
                    ("word-c", (("mode=guide", "mode=word"), ("layout=upstream", "layout=c"),
                                ("back/resolution-guide", "back/resolution-word"),
                                ("back/authorization-guide", "back/authorization-word"))))
    for name, substitutions in degree_types:
        cases[f"starter-{name}"] = lambda name=name, substitutions=substitutions: starter(
            name, substitutions, anonymous=name == "anonymous")
    row = r"\hitwordrow{290.93}{甲}{教授（是）}{示例单位}{示例学科}"
    negative_word = (
        ("cell-width", r"\hitwordrow{290.93}{" + "X" * 80 + r"}{教授（是）}{示例单位}{示例学科}",
         "合成短决议。", "exceeds 52bp width", ""),
        ("cell-height", r"\hitwordrow{290.93}{甲\\乙\\丙\\丁}{教授（是）}{示例单位}{示例学科}",
         "合成短决议。", "exceeds 21bp height", ""),
        ("decision-width", "", "X" * 300, "exceeds 424.6bp width", ""),
        ("decision-height", "", "\n\n".join("合成段落。" for _ in range(60)),
         "Decision text exceeds the fixed 260bp space", ""),
        ("duplicate-row", row + "\n" + row, "合成短决议。", "Duplicate fixed row", ""),
        ("non-a4", "", "合成短决议。", "requires A4 paper", r"\setlength{\paperwidth}{200mm}"),
        ("master-scope", "", "合成短决议。", "requires a Chinese Harbin doctor thesis", ""),
    )
    for name, rows, decision, expected, setup in negative_word:
        cases[f"word-reject-{name}"] = lambda name=name, rows=rows, decision=decision, expected=expected, setup=setup: word_rejection(
            name, rows, decision, expected, setup)
    cases["guide-continuation"] = guide_continuation
    cases["upstream-default-pixels"] = upstream_pixels
    if ARGS.case:
        missing = set(ARGS.case) - set(cases)
        if missing:
            parser.error("Unknown cases: " + ", ".join(sorted(missing)))
        cases = {name: cases[name] for name in ARGS.case}
    for name, action in cases.items():
        evaluate(name, action)
    failures = sum(not result["passed"] for result in RESULTS)
    print(f"{len(RESULTS) - failures}/{len(RESULTS)} cases passed; results: {OUTPUT / 'results.json'}")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError) as error:
        print(f"Validation setup failed: {error}", file=sys.stderr)
        sys.exit(2)
