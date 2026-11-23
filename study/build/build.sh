#!/usr/bin/env bash
# بناء الدراسة وبحث المعيار: Word (معادلات Word أصلية وخط Amiri مضمَّن) و PDF (عبر Chromium) و HTML
set -euo pipefail
cd "$(dirname "$0")/.."
build () {   # $1 = ملف المصدر، $2 = اسم الناتج
  pandoc "$1" -o "$2.docx" --reference-doc=build/reference.docx --resource-path=.:.. --toc --toc-depth=2
  python3 build/rtl_docx.py "$2.docx"
  pandoc "$1" -s --mathml --toc --toc-depth=2 \
    --css=build/style.css --embed-resources --resource-path=.:..:build -o "$2.html"
  NODE_PATH="$(npm root -g)" node build/topdf.js "$2.html" "$2.pdf"
}
build study.md ibn_al_majdi_study
build criterion.md ibn_al_majdi_criterion
build ifta_project.md ibn_al_majdi_ifta_project
build ifta_proposal.md ibn_al_majdi_ifta_proposal
