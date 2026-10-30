#!/usr/bin/env bash
# بناء الدراسة: Word (معادلات Word أصلية) و PDF (عبر Chromium) و HTML
set -euo pipefail
cd "$(dirname "$0")/.."
pandoc study.md -o ibn_al_majdi_study.docx --reference-doc=build/reference.docx \
  --resource-path=.:.. --toc --toc-depth=2
python3 build/rtl_docx.py ibn_al_majdi_study.docx
pandoc study.md -s --mathml --toc --toc-depth=2 \
  --css=build/style.css --embed-resources --resource-path=.:..:build -o ibn_al_majdi_study.html
NODE_PATH="$(npm root -g)" node build/topdf.js ibn_al_majdi_study.html ibn_al_majdi_study.pdf
