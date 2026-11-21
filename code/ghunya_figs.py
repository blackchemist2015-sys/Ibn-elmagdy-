# -*- coding: utf-8 -*-
"""رسوم باب «غنية الفهيم» — تُكتب في figures/ بأسماء g01 … g05"""
import os, sys, csv, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concepts import plt, save, FancyBboxPatch, arrow, INK, BLUE, RED, GREEN, GOLD, GREY, PURPLE

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
rows = list(csv.DictReader(open(os.path.join(DATA, 'ghunya.csv'), encoding='utf-8')))
for r in rows:
    for k, v in r.items():
        try:
            r[k] = float(v)
        except ValueError:
            pass
S = json.load(open(os.path.join(DATA, 'ghunya_summary.json'), encoding='utf-8'))


def g01_compare():
    """خطوات الغنية والخلاصة جنبًا إلى جنب"""
    gh = ['مقوّما النيرين وبُهتاهما نصف نهار التاسع والعشرين',
          'ساعات نصف النهار + ثلثا ساعة ← البعد من جداول الأبهات',
          'البعد المطلق = موضع القمر − موضع الشمس',
          'البعد بالمغارب = مطالع نظير القمر − مطالع نظير الشمس',
          'الحصة ← العرض؛ يُزاد ثلثاه أو يُنقص ← قوس المكث',
          'جدول نظير الشمس من جداول الدائر ← قوس الرؤية',
          'جدول نور الهلال ← دقائق النور',
          'جدول مقام الرؤية: يقابَل بقوس الرؤية']
    kh = ['مقوّما النيرين وبُهتاهما نصف نهار التاسع والعشرين (وشرط «دل»)',
          '(نصف قوس النهار + 10°) ÷ 6 ← حصة البعد بالربع',
          'البعد المطلق بعد إنقاص اختلاف الطول',
          'مطالع نظير الشمس ونظير جزء الهلال ← المكث بتقريب',
          'العرض المرئي ← قوس المكث المحقّق بمطالع غروب الهلال',
          'ارتفاع نظير الشمس بعد المكث ← قوس الرؤية',
          'قوس النور من البعد المطلق والعرض',
          'الأقوال الثلاثة (12، 12، 10) و(8، 7، 10) و(7، 10، 13)']
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_xlim(0, 15); ax.set_ylim(0, 10); ax.axis('off')
    ax.text(11.2, 9.6, 'غنية الفهيم (بالجداول)', ha='center', fontsize=16, color=BLUE, fontweight='bold')
    ax.text(3.8, 9.6, 'خلاصة الأقوال (بالربع المجيب)', ha='center', fontsize=16, color=GREEN, fontweight='bold')
    for i, (a, b) in enumerate(zip(gh, kh)):
        y = 8.8 - i * 1.1
        for x, t, fc, ec in [(11.2, a, '#e0e7ff', BLUE), (3.8, b, '#dcfce7', GREEN)]:
            ax.add_patch(FancyBboxPatch((x - 3.4, y - 0.38), 6.8, 0.76, boxstyle='round,pad=0.04', fc=fc, ec=ec, lw=1.3))
            ax.text(x, y, t, ha='center', va='center', fontsize=12)
        ax.plot([7.2, 7.8], [y, y], color=GREY, lw=1, ls=':')
        ax.text(7.5, y + 0.12, str(i + 1), ha='center', fontsize=10, color=GREY)
    ax.text(7.5, 0.2, 'الخطوات متقابلة واحدةً بواحدة: الغنية تحسب بالجداول، والخلاصة تنفّذ الحساب نفسه بالربع المجيب.',
            ha='center', fontsize=12, color=INK)
    ax.set_title('فصل الهلال في «غنية الفهيم» وفي «خلاصة الأقوال»', fontsize=17)
    save(fig, 'g01_compare.png')


def g02_latitude():
    """تعديل البعد بالمغارب بالعرض: ثلثا العرض أم نصفه؟"""
    b = np.array([r['beta_vis'] for r in rows]); d = np.array([r['lag'] - r['lag_maghrib'] for r in rows])
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.scatter(b, d, s=6, color=GREY, alpha=0.45, label='أمسيات القاهرة 1990–2049')
    x = np.linspace(-5.5, 5.5, 50)
    ax.plot(x, 2 / 3 * x, color=BLUE, lw=2.4, label='ثلثا العرض (الغنية والطوسي)')
    ax.plot(x, 0.5 * x, color=RED, lw=2, ls='--', label='نصف العرض («بعضهم»)')
    ax.plot(x, S['k_exact_fit'] * x, color=GREEN, lw=1.6, ls=':', label=f'أفضل معامل بالحساب = {S["k_exact_fit"]:.2f}')
    ax.axhline(0, color=INK, lw=0.6); ax.axvline(0, color=INK, lw=0.6)
    ax.set_xlabel('عرض الهلال المرئي (درجة) — موجب شمالي')
    ax.set_ylabel('قوس المكث − البعد بالمغارب (درجة)')
    ax.grid(alpha=0.3); ax.legend(loc='upper left')
    ax.set_title('تعديل «البعد بالمغارب» بعرض القمر للحصول على قوس المكث', fontsize=15)
    save(fig, 'g02_latitude.png')


def g03_criteria():
    c = S['criteria_vs_odeh_naked_eye']
    names = list(c.keys())
    short = ['كوشيار: اثنان من ثلاثة', 'كوشيار: الثلاثة كلها', 'ابن يونس (6½)', 'ابن يونس (6)',
             '«بعضهم»: البعد بالمغارب', 'الخلاصة: القول الأول', 'الخلاصة: المعيار المركّب']
    agree = [c[n]['agree'] * 100 for n in names]
    fp = [c[n]['false_pos'] for n in names]; fn = [c[n]['false_neg'] for n in names]
    order = np.argsort(agree)
    fig, ax = plt.subplots(figsize=(11, 6))
    cols = [BLUE if 'كوشيار' in short[i] else GOLD if 'يونس' in short[i] else PURPLE if 'بعضهم' in short[i] else GREEN for i in order]
    ax.barh(range(len(order)), [agree[i] for i in order], color=cols)
    for k, i in enumerate(order):
        ax.text(agree[i] + 0.2, k, f'{agree[i]:.1f}٪  (رؤية خاطئة {fp[i]}، فوات {fn[i]})', va='center', fontsize=11)
    ax.set_yticks(range(len(order))); ax.set_yticklabels([short[i] for i in order])
    ax.set_xlim(80, 101); ax.set_xlabel('نسبة الاتفاق مع معيار عودة (الرؤية بالعين) في 2020 أمسية')
    ax.grid(axis='x', alpha=0.3)
    ax.set_title('الحدود المنقولة في «الغنية» و«الخلاصة» مقابل المعيار الحديث', fontsize=15)
    save(fig, 'g03_criteria.png')


def g04_noon():
    fig, ax = plt.subplots(figsize=(11, 5.5))
    bins = np.arange(-6, 30, 0.5)
    for z, c, t in [('D', '#9ca3af', 'لا يُرى'), ('C', BLUE, 'بالأداة فقط'), ('B', GOLD, 'قد تحتاج أداة'), ('A', GREEN, 'بالعين المجردة')]:
        ax.hist([r['elong_noon'] for r in rows if r['odeh'] == z], bins=bins, color=c, alpha=0.6, label='عودة: ' + t)
    top = ax.get_ylim()[1]
    for v, c, t in [(2, PURPLE, 'الغنية: درجتان فأقل'), (4.5, RED, 'الخلاصة: «دل»'), (10, GREEN, 'الغنية: عشرة فأكثر')]:
        ax.axvline(v, color=c, lw=2.2)
        ax.text(v + 0.2, top * (0.92 if v != 4.5 else 0.8), t, color=c, fontsize=12)
    ax.axvspan(2, 10, color=GOLD, alpha=0.07)
    ax.text(6, top * 0.55, 'هنا فقط\nيلزم «التحرير»', ha='center', fontsize=12, color=GOLD)
    ax.set_xlim(-6, 30); ax.set_xlabel('فضل ما بين مقوّمي النيرين وقت الزوال (درجة)'); ax.set_ylabel('عدد الأمسيات')
    ax.legend(loc='upper right')
    ax.set_title('«إذا كان بين النيرين عند نصف النهار نحو درجتين فأقل أو عشرة فأكثر، إذ لا فائدة في التحرير»', fontsize=13)
    save(fig, 'g04_noon.png')


def g05_side():
    rec = np.array(json.load(open(os.path.join(DATA, 'ghunya_setting_sides.json'))))
    lam, dd = rec[:, 0], rec[:, 1]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.axvspan(90, 270, color=GOLD, alpha=0.12)
    ax.text(180, 15.5, 'الشمس في البروج الهابطة (من السرطان إلى الجدي)', ha='center', color=GOLD, fontsize=12)
    ax.scatter(lam, dd, s=10, c=np.where(dd < 0, RED, BLUE), alpha=0.6)
    ax.axhline(0, color=INK, lw=1)
    ax.text(2, 1, 'الهلال يغرب شمال مغرب الشمس', color=BLUE, fontsize=11)
    ax.text(2, -2.2, 'الهلال يغرب جنوب مغرب الشمس', color=RED, fontsize=11)
    ax.set_xticks(range(0, 361, 30))
    ax.set_xticklabels(['الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'السنبلة', 'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت', ''], fontsize=11)
    ax.set_xlabel('برج الشمس'); ax.set_ylabel('سعة مغرب الهلال − سعة مغرب الشمس (درجة)')
    ax.set_xlim(0, 360); ax.set_ylim(-18, 18); ax.grid(alpha=0.25)
    s = S['first_crescent_sets_south_of_sun']
    ax.set_title(f'جهة غروب الهلال عن مغرب الشمس في أول ليلة يُرى فيها ({s["n"]} شهرًا، القاهرة)', fontsize=14)
    save(fig, 'g05_side.png')


if __name__ == '__main__':
    g01_compare(); g02_latitude(); g03_criteria(); g04_noon(); g05_side()
