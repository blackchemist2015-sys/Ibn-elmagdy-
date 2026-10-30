# -*- coding: utf-8 -*-
"""يضبط ملف Word الناتج من pandoc للكتابة من اليمين إلى اليسار:
الفقرات (bidi)، والنصوص العربية (rtl)، والجداول (bidiVisual)."""
import re, sys
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

AR = re.compile('[؀-ۿ]')

def add(parent, tag, first=False):
    if parent.find(qn(tag)) is None:
        el = OxmlElement(tag)
        parent.insert(0, el) if first else parent.append(el)

path = sys.argv[1]
doc = Document(path)
body = doc.element.body
for p in body.iter(qn('w:p')):
    # فقرات المعادلات المستقلة تبقى من اليسار إلى اليمين داخل المعادلة نفسها
    pPr = p.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr'); p.insert(0, pPr)
    add(pPr, 'w:bidi')
    for r in p.iter(qn('w:r')):
        t = ''.join(x.text or '' for x in r.iter(qn('w:t')))
        if AR.search(t):
            rPr = r.find(qn('w:rPr'))
            if rPr is None:
                rPr = OxmlElement('w:rPr'); r.insert(0, rPr)
            add(rPr, 'w:rtl')
for tbl in body.iter(qn('w:tbl')):
    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is not None:
        add(tblPr, 'w:bidiVisual')
for st in doc.styles:
    el = st.element
    if el.get(qn('w:type')) == 'paragraph':
        pPr = el.find(qn('w:pPr'))
        if pPr is None:
            pPr = OxmlElement('w:pPr'); el.append(pPr)
        add(pPr, 'w:bidi')
doc.save(path)
print('RTL applied to', path)
