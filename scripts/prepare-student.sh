#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p examples/hitbook/{chinese,english}/figures examples/hitart/{reports,reportplus}/figures
latex -interaction=nonstopmode -halt-on-error hithesis.ins
cp hithesisbook.cls hithesisbook.cfg hithesis.bst hithesis.ist student/
cp examples/hitbook/chinese/hithesis.sty student/
