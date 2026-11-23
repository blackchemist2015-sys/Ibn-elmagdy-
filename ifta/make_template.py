# -*- coding: utf-8 -*-
"""ينشئ قالب إدخال بيانات دار الإفتاء (ifta/template/ifta_data_template.xlsx)،
وملف بيانات تجريبية مولَّدة للاختبار فقط (ifta/demo/demo_data_SYNTHETIC.xlsx)."""
import os, sys, datetime as dt
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_ifta import HEAD, HMONTHS, style_sheet, CAIRO
import majdi_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))

INSTR = [
    'قالب إدخال بيانات دار الإفتاء المصرية — مشروع مطابقة معيار ابن المجدي',
    '',
    'صفٌّ واحد لكل شهر هجري، مرتّبةً من الأقدم إلى الأحدث، دون انقطاع ما أمكن.',
    'العمود الأساسي هو «أول الشهر المعلن»: التاريخ الميلادي لليوم الأول من الشهر كما أعلنته دار الإفتاء (بصيغة سنة-شهر-يوم).',
    'من هذا العمود وحده يستنتج البرنامج نتيجة تحرّي الهلال: إذا كان الشهر السابق 29 يومًا فقد أُعلنت الرؤية مساء التاسع والعشرين، وإن كان 30 يومًا فلم تثبت الرؤية وأُكمل الشهر.',
    'عمود «ثبتت رؤية هلاله؟» اختياري (نعم/لا)، ويفيد في كشف أخطاء الإدخال إذا خالف طول الشهر.',
    'عمود «أساس القرار» مهم: رؤية / حساب / إكمال / غير معروف. فقد تغيّرت سياسة الإثبات عبر 130 سنة، ويمكن استبعاد القرارات المبنية على الحساب من استخراج المعيار.',
    'موضع الرؤية وإحداثياته اختيارية؛ وإذا تُركت حُسب للقاهرة (العرض 30.0444، الطول 31.2357).',
    'المصدر: رقم البيان أو السجل أو الجريدة وتاريخها، ليمكن الرجوع إليه.',
    '',
    'التشغيل: python3 ifta/run_ifta.py ملف_البيانات.xlsx مجلد_النتائج',
]


def template(path):
    wb = openpyxl.Workbook()
    ws0 = wb.active; ws0.title = 'تعليمات'
    for line in INSTR:
        ws0.append([line])
    ws0['A1'].font = Font(bold=True, size=14, name='Amiri')
    ws0.column_dimensions['A'].width = 140; ws0.sheet_view.rightToLeft = True
    ws = wb.create_sheet('البيانات'); ws.append(HEAD)
    style_sheet(ws, [10, 9, 14, 18, 22, 24, 14, 9, 9, 26, 30])
    dv1 = DataValidation(type='list', formula1='"نعم,لا"', allow_blank=True); ws.add_data_validation(dv1); dv1.add('E2:E3000')
    dv2 = DataValidation(type='list', formula1='"رؤية,حساب,إكمال,غير معروف"', allow_blank=True); ws.add_data_validation(dv2); dv2.add('F2:F3000')
    for r in range(2, 3001):
        ws.cell(r, 4).number_format = 'yyyy-mm-dd'
    ex = wb.create_sheet('مثال للصيغة')
    ex.append(HEAD)
    ex.append(['— صفوف توضيحية لصيغة الإدخال فقط، وليست بيانات رسمية —'])
    ex.append([1447, 9, 'رمضان', '2026-02-18', '', 'رؤية', 'القاهرة', '', '', 'رقم البيان وتاريخه', ''])
    ex.append([1447, 10, 'شوال', '2026-03-20', 'لا', 'رؤية', 'القاهرة', '', '', 'رقم البيان وتاريخه', ''])
    style_sheet(ex, [10, 9, 14, 18, 22, 24, 14, 9, 9, 26, 30])
    wb.save(path)


def demo(path, y0=1317, y1=1447, start=dt.date(1899, 5, 11)):
    """تقويم تجريبي: يبدأ كل شهر بعد أول ليلةٍ يُرى فيها الهلال بالعين بمعيار عودة في القاهرة، وإلا أُكمل 30.
    ليس بيانات دار الإفتاء؛ غرضه اختبار البرنامج فقط."""
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'البيانات'; ws.append(HEAD)
    s = start; hy, hm = y0, 1
    n = 0
    while hy <= y1:
        ws.append([hy, hm, HMONTHS[hm - 1], s.isoformat(), '', 'رؤية', 'القاهرة', '', '', 'تجريبي — معيار عودة', 'بيانات مولّدة للاختبار'])
        ev = s + dt.timedelta(days=28)
        m = E.modern(ev, *CAIRO)
        seen = m.get('odeh_zone') in ('A', 'B') and m.get('moon_age_h', -1) > 0
        s = s + dt.timedelta(days=29 if seen else 30)
        hm += 1
        if hm == 13:
            hm, hy = 1, hy + 1
        n += 1
        if n % 300 == 0:
            print(' ', n, s, flush=True)
    style_sheet(ws, [10, 9, 14, 18, 22, 24, 14, 9, 9, 26, 30])
    wb.save(path)


if __name__ == '__main__':
    os.makedirs(os.path.join(HERE, 'template'), exist_ok=True); os.makedirs(os.path.join(HERE, 'demo'), exist_ok=True)
    template(os.path.join(HERE, 'template', 'ifta_data_template.xlsx'))
    if '--demo' in sys.argv:
        demo(os.path.join(HERE, 'demo', 'demo_data_SYNTHETIC.xlsx'))
    print('done')
