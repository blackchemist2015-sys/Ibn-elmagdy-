# -*- coding: utf-8 -*-
"""ضبط ملف Word الناتج من pandoc للعربية:
- اتجاه الفقرات من اليمين (bidi) في المتن والحواشي، والنصوص العربية (rtl)، والجداول (bidiVisual).
- محاذاة المتن بالتساوي (ضبط)، وتباعد الأسطر 1.5، وتوسيط التعليقات تحت الأشكال.
- لغة التدقيق العربية (ar-EG) حتى لا يعلّم Word الكلمات العربية أخطاءً إملائية.
- حدود للجداول وتظليل لصف العنوان.
- تضمين خط Amiri داخل الملف (مُعمّى على طريقة OOXML) ليظهر على أي جهاز.
الاستعمال: python3 rtl_docx.py ملف.docx [مجلد_الخطوط]"""
import os, re, sys, uuid, zipfile, shutil, tempfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PR = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
q = lambda t: '{%s}%s' % (W, t)
AR = re.compile('[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
FONT = 'Amiri'
LANG = 'ar-EG'

# ترتيب عناصر خصائص الفقرة والنص في مخطط OOXML (يلزم Word احترامه)
PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl', 'numPr',
             'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap',
             'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd',
             'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc',
             'textDirection', 'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr',
             'sectPr', 'pPrChange']
RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'dstrike', 'outline',
             'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish', 'webHidden', 'color', 'spacing',
             'w', 'kern', 'position', 'sz', 'szCs', 'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText',
             'vertAlign', 'rtl', 'cs', 'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath']
TBLPR_ORDER = ['tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize', 'tblStyleColBandSize',
               'tblW', 'jc', 'tblCellSpacing', 'tblInd', 'tblBorders', 'shd', 'tblLayout', 'tblCellMar', 'tblLook']
TCPR_ORDER = ['cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd', 'noWrap', 'tcMar',
              'textDirection', 'tcFitText', 'vAlign', 'hideMark']


def child(parent, tag, order, attrs=None, first=False):
    """يعيد العنصر الابن (وينشئه في موضعه الصحيح بحسب ترتيب المخطط)."""
    el = parent.find(q(tag))
    if el is None:
        el = etree.Element(q(tag))
        idx = order.index(tag) if tag in order else len(order)
        pos = len(parent)
        for i, c in enumerate(parent):
            name = etree.QName(c).localname
            if name in order and order.index(name) > idx:
                pos = i
                break
        parent.insert(pos, el)
    for k, v in (attrs or {}).items():
        el.set(q(k), v)
    return el


def get_pr(el, tag):
    pr = el.find(q(tag))
    if pr is None:
        pr = etree.Element(q(tag))
        el.insert(0, pr)
    return pr


def fix_paragraphs(root, justify_styles):
    for p in root.iter(q('p')):
        ppr = get_pr(p, 'pPr')
        alltxt = ''.join(t.text or '' for t in p.iter(q('t')))
        if not AR.search(alltxt) and re.search('[A-Za-z]', alltxt):
            # فقرة لاتينية خالصة (مرجع أو حاشية إنجليزية): من اليسار إلى اليمين
            b = ppr.find(q('bidi'))
            if b is None:
                b = child(ppr, 'bidi', PPR_ORDER)
            b.set(q('val'), '0')
            child(ppr, 'jc', PPR_ORDER, {'val': 'left'})
            continue
        child(ppr, 'bidi', PPR_ORDER)
        st = ppr.find(q('pStyle'))
        sid = st.get(q('val')) if st is not None else 'Normal'
        has_math = p.find('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMathPara') is not None
        if sid in justify_styles and not has_math:
            child(ppr, 'jc', PPR_ORDER, {'val': 'both'})
        for r in p.iter(q('r')):
            txt = ''.join(t.text or '' for t in r.iter(q('t')))
            if AR.search(txt):
                rpr = get_pr(r, 'rPr')
                child(rpr, 'rtl', RPR_ORDER)


def fix_tables(root):
    for tbl in root.iter(q('tbl')):
        tpr = get_pr(tbl, 'tblPr')
        child(tpr, 'bidiVisual', TBLPR_ORDER)
        child(tpr, 'tblW', TBLPR_ORDER, {'w': '5000', 'type': 'pct'})
        b = child(tpr, 'tblBorders', TBLPR_ORDER)
        for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            child(b, side, ['top', 'left', 'start', 'bottom', 'right', 'end', 'insideH', 'insideV'],
                  {'val': 'single', 'sz': '4', 'space': '0', 'color': '9CA3AF'})
        rows = tbl.findall(q('tr'))
        if rows:
            for tc in rows[0].findall(q('tc')):
                tcpr = get_pr(tc, 'tcPr')
                child(tcpr, 'shd', TCPR_ORDER, {'val': 'clear', 'color': 'auto', 'fill': 'E0E7FF'})


def fix_styles(root):
    # الإعدادات الافتراضية: الخط ولغة التدقيق وحجم النص العربي
    dd = root.find(q('docDefaults'))
    rpr = dd.find(q('rPrDefault')).find(q('rPr'))
    child(rpr, 'rFonts', RPR_ORDER, {'ascii': FONT, 'hAnsi': FONT, 'cs': FONT, 'eastAsia': FONT})
    child(rpr, 'lang', RPR_ORDER, {'val': LANG, 'bidi': LANG, 'eastAsia': 'en-US'})
    ppd = dd.find(q('pPrDefault'))
    if ppd is None:
        ppd = etree.SubElement(dd, q('pPrDefault'))
    ppr = get_pr(ppd, 'pPr')
    child(ppr, 'bidi', PPR_ORDER)
    for st in root.findall(q('style')):
        sid = st.get(q('styleId'))
        typ = st.get(q('type'))
        if typ == 'paragraph':
            ppr = get_pr(st, 'pPr')
            child(ppr, 'bidi', PPR_ORDER)
            if sid in ('BodyText', 'FirstParagraph', 'Compact', 'BlockText'):
                child(ppr, 'spacing', PPR_ORDER, {'line': '360', 'lineRule': 'auto', 'after': '120'})
            if sid in ('BodyText', 'FirstParagraph', 'BlockText', 'FootnoteText'):
                child(ppr, 'jc', PPR_ORDER, {'val': 'both'})
            if sid in ('ImageCaption', 'Caption', 'TableCaption', 'CaptionedFigure', 'Figure'):
                child(ppr, 'jc', PPR_ORDER, {'val': 'center'})
            if sid in ('Title', 'Subtitle'):
                child(ppr, 'jc', PPR_ORDER, {'val': 'center'})
        if typ in ('paragraph', 'character'):
            rpr = get_pr(st, 'rPr')
            if rpr.find(q('rFonts')) is not None or sid in ('Normal',):
                child(rpr, 'rFonts', RPR_ORDER, {'ascii': FONT, 'hAnsi': FONT, 'cs': FONT, 'eastAsia': FONT})
            sz = rpr.find(q('sz'))
            if sz is not None:
                child(rpr, 'szCs', RPR_ORDER, {'val': sz.get(q('val'))})
            if sid in ('ImageCaption', 'Caption', 'TableCaption'):
                child(rpr, 'sz', RPR_ORDER, {'val': '22'})
                child(rpr, 'szCs', RPR_ORDER, {'val': '22'})


def obfuscate(data, key_guid):
    """تعمية الخط المضمَّن: XOR لأول 32 بايتًا بمفتاح GUID معكوس البايتات (ECMA-376)."""
    key = bytes.fromhex(key_guid.strip('{}').replace('-', ''))[::-1]
    data = bytearray(data)
    for i in range(32):
        data[i] ^= key[i % 16]
    return bytes(data)


def embed_fonts(tmp, fonts_dir):
    files = {'embedRegular': 'Amiri-Regular.ttf', 'embedBold': 'Amiri-Bold.ttf'}
    if not all(os.path.exists(os.path.join(fonts_dir, f)) for f in files.values()):
        return False
    os.makedirs(os.path.join(tmp, 'word', 'fonts'), exist_ok=True)
    rels_path = os.path.join(tmp, 'word', '_rels', 'fontTable.xml.rels')
    rels = etree.Element('{%s}Relationships' % PR, nsmap={None: PR})
    ft_path = os.path.join(tmp, 'word', 'fontTable.xml')
    ft = etree.parse(ft_path)
    froot = ft.getroot()
    for f in froot.findall(q('font')):
        if f.get(q('name')) == FONT:
            froot.remove(f)
    font = etree.SubElement(froot, q('font'), {q('name'): FONT})
    etree.SubElement(font, q('charset'), {q('val'): 'B2'})
    etree.SubElement(font, q('family'), {q('val'): 'auto'})
    etree.SubElement(font, q('pitch'), {q('val'): 'variable'})
    for i, (tag, fn) in enumerate(files.items(), 1):
        guid = '{%s}' % str(uuid.uuid4()).upper()
        data = open(os.path.join(fonts_dir, fn), 'rb').read()
        name = 'font%d.odttf' % i
        open(os.path.join(tmp, 'word', 'fonts', name), 'wb').write(obfuscate(data, guid))
        rid = 'rIdFont%d' % i
        etree.SubElement(rels, '{%s}Relationship' % PR, Id=rid,
                         Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/font',
                         Target='fonts/' + name)
        e = etree.SubElement(font, q(tag))
        e.set('{%s}id' % R, rid)
        e.set(q('fontKey'), guid)
    ft.write(ft_path, xml_declaration=True, encoding='UTF-8', standalone=True)
    etree.ElementTree(rels).write(rels_path, xml_declaration=True, encoding='UTF-8', standalone=True)
    ctp = os.path.join(tmp, '[Content_Types].xml')
    ct = etree.parse(ctp)
    if not any(d.get('Extension') == 'odttf' for d in ct.getroot()):
        etree.SubElement(ct.getroot(), '{%s}Default' % CT, Extension='odttf',
                         ContentType='application/vnd.openxmlformats-officedocument.obfuscatedFont')
        ct.getroot().insert(0, ct.getroot()[-1])
    ct.write(ctp, xml_declaration=True, encoding='UTF-8', standalone=True)
    sp = os.path.join(tmp, 'word', 'settings.xml')
    st = etree.parse(sp)
    sr = st.getroot()
    if sr.find(q('embedTrueTypeFonts')) is None:
        e = etree.Element(q('embedTrueTypeFonts'))
        es = sr.find(q('embedSystemFonts'))
        (es.addprevious(e) if es is not None else sr.insert(0, e))
    st.write(sp, xml_declaration=True, encoding='UTF-8', standalone=True)
    return True


def main(path, fonts_dir):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(path) as z:
        z.extractall(tmp)
    justify = {'BodyText', 'FirstParagraph', 'BlockText', 'FootnoteText', 'Normal'}
    for part in ('document.xml', 'footnotes.xml'):
        fp = os.path.join(tmp, 'word', part)
        if os.path.exists(fp):
            t = etree.parse(fp)
            fix_paragraphs(t.getroot(), justify)
            fix_tables(t.getroot())
            t.write(fp, xml_declaration=True, encoding='UTF-8', standalone=True)
    sp = os.path.join(tmp, 'word', 'styles.xml')
    t = etree.parse(sp)
    fix_styles(t.getroot())
    t.write(sp, xml_declaration=True, encoding='UTF-8', standalone=True)
    embedded = embed_fonts(tmp, fonts_dir)
    out = path + '.tmp'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(tmp, '[Content_Types].xml'), '[Content_Types].xml')
        for base, _, fs in os.walk(tmp):
            for f in fs:
                full = os.path.join(base, f)
                arc = os.path.relpath(full, tmp)
                if arc != '[Content_Types].xml':
                    z.write(full, arc)
    shutil.move(out, path)
    shutil.rmtree(tmp)
    print('RTL + Arabic formatting applied to', path, '| font embedded:', embedded)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, '..', '..', 'fonts'))
