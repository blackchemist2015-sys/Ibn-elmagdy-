# -*- coding: utf-8 -*-
"""رسومات دراسة رسالة ابن المجدي — تُكتب في figures/"""
import os, sys, csv, math, warnings
warnings.filterwarnings('ignore')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Arc, FancyBboxPatch, FancyArrowPatch, Circle, Wedge
import arabic_reshaper
from bidi.algorithm import get_display

NATIVE_BIDI = tuple(int(x) for x in matplotlib.__version__.split('.')[:2]) >= (3, 10)
HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, '..', 'figures')
DATA = os.path.join(HERE, '..', 'data', 'hilal_cairo.csv')
os.makedirs(FIG, exist_ok=True)

for p in [os.path.expanduser('~/.fonts/Amiri-Regular.ttf'), os.path.expanduser('~/.fonts/Amiri-Bold.ttf')]:
    if os.path.exists(p):
        font_manager.fontManager.addfont(p)
plt.rcParams.update({'font.family': ['Amiri', 'DejaVu Sans'], 'font.size': 13, 'axes.unicode_minus': False,
                     'savefig.dpi': 200, 'savefig.bbox': 'tight'})

INK, BLUE, RED, GREEN, GOLD, GREY = '#1f2937', '#1d4ed8', '#b91c1c', '#15803d', '#b45309', '#6b7280'


def A(s):
    """matplotlib ≥ 3.10 يشكّل النص العربي ويعكس اتجاهه بنفسه (عبر libraqm)؛
    أما الإصدارات الأقدم فتحتاج إلى arabic_reshaper و python-bidi."""
    if NATIVE_BIDI:
        return s
    return get_display(arabic_reshaper.reshape(s))


def save(fig, name):
    fig.savefig(os.path.join(FIG, name))
    plt.close(fig)
    print('saved', name)


def load_rows():
    with open(DATA, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except ValueError:
                pass
    return rows


# ---------------------------------------------------------------------------
def fig_quadrant():
    """شكل 1: الربع المجيب وطريقة استخراج جيب الميل والظل"""
    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    Rr = 60
    th = np.linspace(0, np.pi / 2, 200)
    ax.plot(Rr * np.cos(th), Rr * np.sin(th), color=INK, lw=2)
    for i in range(0, 61, 5):
        ax.plot([i, i], [0, math.sqrt(Rr ** 2 - i ** 2)], color=GREY, lw=0.4 if i % 15 else 0.9)
        ax.plot([0, math.sqrt(Rr ** 2 - i ** 2)], [i, i], color=GREY, lw=0.4 if i % 15 else 0.9)
    ax.plot([0, Rr], [0, 0], color=INK, lw=2)
    ax.plot([0, 0], [0, Rr], color=INK, lw=2)
    for deg in range(0, 91, 10):
        x, y = Rr * math.cos(math.radians(deg)), Rr * math.sin(math.radians(deg))
        ax.plot([x, 1.03 * x], [y, 1.03 * y], color=INK, lw=1)
        ax.text(1.08 * x, 1.08 * y, str(deg), ha='center', va='center', fontsize=10)
    # الخيط على قوس 40 (مثلا ارتفاع) والمري
    a = 40
    ax.plot([0, Rr * math.cos(math.radians(a))], [0, Rr * math.sin(math.radians(a))], color=RED, lw=1.8)
    mr = 23.58 / 90 * 60  # موضع توضيحي للمري
    eps = 23.58
    rm = Rr * math.sin(math.radians(eps))
    mx, my = rm * math.cos(math.radians(a)), rm * math.sin(math.radians(a))
    ax.plot(mx, my, 'o', color=GOLD, ms=9, zorder=5)
    ax.annotate('', xy=(mx, 0), xytext=(mx, my), arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.5, ls='--'))
    ax.annotate('', xy=(0, my), xytext=(mx, my), arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.5, ls='--'))
    ax.text(mx + 1.5, my + 1.5, A('المري'), color=GOLD, fontsize=13)
    ax.text(Rr * 0.62 * math.cos(math.radians(a)) + 2, Rr * 0.62 * math.sin(math.radians(a)) + 3,
            A('الخيط'), color=RED, fontsize=13, rotation=a)
    ax.text(30, -5.5, A('الستيني (خط المشرق) — الجيوب المبسوطة نازلة منه'), ha='center', fontsize=12)
    ax.text(-5.5, 30, A('جيب التمام — الجيوب المنكوسة'), ha='center', va='center', rotation=90, fontsize=12)
    ax.text(0, -2, A('المركز'), ha='right', va='top', fontsize=11)
    ax.text(42, 52, A('قوس الارتفاع'), fontsize=13, color=INK)
    ax.text(5, -11.5, A('مثال: المري على جيب الميل الأعظم (R sin ε) ثم الخيط على بعد الدرجة λ'), fontsize=11, color=GREY)
    ax.text(5, -15.5, A('فيصير بُعد المري عن الستيني = R sin ε sin λ = R sin δ'), fontsize=11, color=GREY)
    ax.set_xlim(-10, 70)
    ax.set_ylim(-18, 70)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(A('الربع المجيب — رسومه والعمل بالخيط والمري'), fontsize=15)
    save(fig, 'fig01_quadrant.png')


def fig_triangle():
    """شكل 2: المثلث الفلكي القطب-السمت-الكوكب وعناصره عند ابن المجدي"""
    fig, ax = plt.subplots(figsize=(9, 8))
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(t), np.sin(t), color=INK, lw=1.5)
    ax.plot([-1, 1], [0, 0], color=INK, lw=1.2)                       # الأفق (مُسقَط)
    phi = math.radians(30)
    # القطب
    P = (-math.cos(phi), math.sin(phi))
    Z = (0, 1)
    ax.plot([0, P[0] * 1.0], [0, P[1]], color=GREY, lw=0.8, ls=':')
    # معدل النهار: قطر عمودي على محور القطب
    eq = (math.sin(phi), math.cos(phi))
    ax.plot([-eq[0], eq[0]], [-eq[1], eq[1]], color=BLUE, lw=1.3, ls='--')
    ax.text(eq[0] * 1.05, eq[1] * 1.05, A('معدل النهار'), color=BLUE, fontsize=12)
    # مدار الشمس (ميل δ)
    d = math.radians(20)
    cx, cy = P[0] * math.sin(d) * 0 + eq[0] * 0, 0
    c = (math.cos(phi) * 0, 0)
    off = (math.sin(d) * (-math.cos(phi)), math.sin(d) * math.sin(phi))
    rad = math.cos(d)
    ax.plot([off[0] - rad * eq[0], off[0] + rad * eq[0]], [off[1] - rad * eq[1], off[1] + rad * eq[1]], color=GOLD, lw=1.5)
    ax.text(off[0] + rad * eq[0] + 0.03, off[1] + rad * eq[1], A('مدار الشمس'), color=GOLD, fontsize=12)
    for pnt, lab in [(P, 'القطب (P)'), (Z, 'سمت الرأس (Z)')]:
        ax.plot(*pnt, 'o', color=INK)
        ax.text(pnt[0] - 0.05, pnt[1] + 0.05, A(lab), ha='right', fontsize=12)
    X = (0.45, 0.62)
    ax.plot(*X, 'o', color=RED, ms=9)
    ax.text(X[0] + 0.04, X[1] + 0.03, A('الشمس/الكوكب (X)'), color=RED, fontsize=12)
    for a_, b_ in [(P, Z), (Z, X), (P, X)]:
        ax.plot([a_[0], b_[0]], [a_[1], b_[1]], color=RED, lw=1.6)
    ax.text(-0.33, 0.97, A('90 − φ  (تمام العرض)'), fontsize=11)
    ax.text(0.27, 0.86, A('90 − h (تمام الارتفاع)'), fontsize=11, rotation=-35)
    ax.text(-0.25, 0.55, A('90 − δ (تمام الميل)'), fontsize=11, rotation=15)
    ax.text(-0.42, 0.68, 't', fontsize=13, color=GREEN)
    ax.text(0.02, 0.88, 'A', fontsize=13, color=GREEN)
    ax.text(-1.0, -0.08, A('الأفق'), fontsize=12)
    ax.text(-1.1, -1.25, A('sin h = sin φ sin δ + cos φ cos δ cos t      (فضل الدائر t)'), fontsize=12)
    ax.text(-1.1, -1.40, A('cos t = (المحفوظ الثاني ∓ المحفوظ الأول) / (R cos δ) = جيب الترتيب / جيب تمام الميل'), fontsize=12)
    ax.set_xlim(-1.3, 1.4)
    ax.set_ylim(-1.5, 1.25)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(A('المثلث الفلكي وعناصر «فضل الدائر» و«السمت» في الرسالة'), fontsize=15)
    save(fig, 'fig02_triangle.png')


def fig_sunset_geometry():
    """شكل 3: هندسة الهلال عند الغروب — قوس المكث والرؤية والارتفاع والبعد المطلق والنور"""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.axhline(0, color=INK, lw=2)
    ax.fill_between([-12, 12], -14, 0, color='#e5e7eb')
    ax.text(10.8, 0.4, A('الأفق الغربي'), fontsize=13, ha='right')
    S = (0, -11)
    M = (4.5, 11)
    ax.plot(*S, 'o', color=GOLD, ms=18)
    ax.text(S[0] + 0.8, S[1], A('الشمس تحت الأفق'), fontsize=12)
    ax.plot(*M, 'o', color='#94a3b8', ms=16)
    ax.add_patch(Wedge(M, 0.45, 200, 340, color='white', zorder=6))
    ax.text(M[0] + 0.8, M[1] + 0.5, A('الهلال'), fontsize=13)
    # قوس الرؤية: فرق الارتفاعين
    ax.annotate('', xy=(-3, M[1]), xytext=(-3, S[1]), arrowprops=dict(arrowstyle='<->', color=RED, lw=1.8))
    ax.plot([-3, M[0]], [M[1], M[1]], color=RED, lw=0.6, ls=':')
    ax.plot([-3, S[0]], [S[1], S[1]], color=RED, lw=0.6, ls=':')
    ax.text(-3.3, 0, A('قوس الرؤية ARCV'), rotation=90, color=RED, ha='right', va='center', fontsize=12)
    # الارتفاع
    ax.annotate('', xy=(M[0], M[1]), xytext=(M[0], 0), arrowprops=dict(arrowstyle='<->', color=BLUE, lw=1.8))
    ax.text(M[0] + 0.3, 5, A('قوس الارتفاع h'), color=BLUE, fontsize=12)
    # البعد المطلق/النور
    ax.plot([S[0], M[0]], [S[1], M[1]], color=GREEN, lw=1.8)
    ax.text(1.0, -3.5, A('قوس النور ARCL'), color=GREEN, fontsize=12, rotation=70)
    # فرق السمت
    ax.annotate('', xy=(M[0], -1.2), xytext=(S[0], -1.2), arrowprops=dict(arrowstyle='<->', color=GOLD, lw=1.5))
    ax.text(2.2, -2.2, A('فرق السمت DAZ'), color=GOLD, fontsize=11, ha='center')
    # مدار الغروب المائل
    xs = np.linspace(-6, 9, 50)
    ax.plot(xs, (xs - M[0]) * (-1 / math.tan(math.radians(30))) + M[1], color=GREY, lw=0.8, ls='--')
    ax.text(8.6, 3.2, A('مسار نزول الهلال (مائل بزاوية 90 − φ)'), fontsize=10, color=GREY, rotation=-60)
    ax.text(-11.5, 12.5, A('قوس المكث: الزمن بين غروب الشمس وغروب الهلال (×4 دقائق لكل جزء)'), fontsize=12)
    ax.text(-11.5, 10.8, A('البعد المطلق: فضل ما بين موضعي النيرين في الطول (Δλ)'), fontsize=12)
    ax.text(-11.5, 9.1, A('cos ARCL = cos Δλ · cos β'), fontsize=12)
    ax.set_xlim(-12, 12)
    ax.set_ylim(-14, 14)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(A('متغيرات رؤية الهلال عند ابن المجدي لحظة غروب الشمس'), fontsize=15)
    save(fig, 'fig03_sunset_geometry.png')


def fig_ecliptic_angle():
    """شكل 4: زاوية فلك البروج مع الأفق الغربي عند الغروب في رأس الحمل ورأس الميزان وتحليل اختلاف المنظر"""
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    phi, eps, P = 30.04, 23.44, 56.0
    h = 10
    for ax, (ang, title, lon_tab, lat_tab) in zip(axs, [(90 - phi + eps, 'الشمس في رأس الحمل (الربيع)', 51, 6),
                                                        (90 - phi - eps, 'الشمس في رأس الميزان (الخريف)', 30, 41)]):
        ax.axhline(0, color=INK, lw=2)
        L = 9
        a = math.radians(ang)
        ax.plot([0, L * math.cos(math.pi - a)], [0, L * math.sin(math.pi - a)], color=BLUE, lw=2)
        ax.text(L * math.cos(math.pi - a) - 0.2, L * math.sin(math.pi - a), A('فلك البروج'), color=BLUE, ha='right')
        ax.add_patch(Arc((0, 0), 3, 3, theta1=180 - ang, theta2=180, color=GOLD, lw=1.5))
        ax.text(-2.4, 0.5, f'{ang:.1f}°', color=GOLD, fontsize=12)
        # الهلال على البروج وعمود اختلاف المنظر
        r = 6
        mx, my = r * math.cos(math.pi - a), r * math.sin(math.pi - a)
        ax.plot(mx, my, 'o', color='#64748b', ms=12)
        pa = P * math.cos(math.radians(h))
        scale = 0.06
        ax.annotate('', xy=(mx, my - pa * scale), xytext=(mx, my), arrowprops=dict(arrowstyle='->', color=RED, lw=2))
        ax.text(mx + 0.2, my - pa * scale / 2, A('اختلاف المنظر'), color=RED, fontsize=11)
        plon = pa * math.sin(a)
        plat = pa * math.cos(a)
        ax.text(-8.5, -1.6, A(f'في الطول ≈ {plon:.0f}′ (ابن المجدي: {lon_tab}′)'), fontsize=12)
        ax.text(-8.5, -2.6, A(f'في العرض ≈ {plat:.0f}′ (ابن المجدي: {lat_tab}′)'), fontsize=12)
        ax.set_title(A(title), fontsize=14)
        ax.set_xlim(-9, 3); ax.set_ylim(-3.2, 8)
        ax.set_aspect('equal'); ax.axis('off')
    fig.suptitle(y=1.0, t=A('لماذا يكون اختلاف المنظر في الطول 51′ في الحمل و30′ في الميزان (عرض القاهرة 30°)'), fontsize=15)
    save(fig, 'fig04_ecliptic_angle.png')


def fig_parallax_table(rows):
    """شكل 5: جدول ابن المجدي لاختلاف المنظر مقابل القيم الحقيقية عند الغروب"""
    rr = [r for r in rows if 0 < r['alt_majdi'] < 25 and r['night'] >= 0]
    lam = np.array([r['lam_moon'] for r in rr]) % 360
    pl = np.array([r['p_lon_true'] for r in rr])
    pb = np.array([r['p_lat_true'] for r in rr])
    x = np.linspace(0, 360, 361)
    d = np.abs(((x + 180) % 360) - 180)
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.2))
    axs[0].scatter(lam, pl, s=6, color=BLUE, alpha=0.45, label=A('الحقيقي عند الغروب (القاهرة)'))
    axs[0].plot(x, 51 - 21 * d / 180, color=RED, lw=2.2, label=A('ابن المجدي: 51′ ← 30′'))
    axs[1].scatter(lam, pb, s=6, color=GREEN, alpha=0.45, label=A('الحقيقي عند الغروب (القاهرة)'))
    axs[1].plot(x, 6 + 35 * d / 180, color=RED, lw=2.2, label=A('ابن المجدي: 6′ (و) ← 41′'))
    for ax, t in zip(axs, ['اختلاف المنظر في الطول (دقائق)', 'اختلاف المنظر في العرض (دقائق)']):
        ax.set_xlabel(A('طول الهلال (درجة) — 0 رأس الحمل، 180 رأس الميزان'))
        ax.set_title(A(t))
        ax.set_xticks(range(0, 361, 30))
        ax.grid(alpha=0.3)
        ax.legend(fontsize=11)
    fig.suptitle(A('تحقيق قيم اختلاف المنظر في الرسالة على 1990–2049'), fontsize=15, y=1.04)
    save(fig, 'fig05_parallax_table.png')


def fig_alt_parallax():
    """شكل 6: تعديل الارتفاع: درجة إلى 30، ثلاثة أرباع إلى 60، ثم (90−h) دقيقة"""
    h = np.linspace(0, 90, 361)
    maj = np.where(h <= 30, 60, np.where(h <= 60, 45, 90 - h))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(h, 57 * np.cos(np.radians(h)), color=BLUE, lw=2, label=A('اختلاف المنظر الحقيقي (أفقي 57′) = 57′ cos h'))
    ax.fill_between(h, 54 * np.cos(np.radians(h)), 61.5 * np.cos(np.radians(h)), color=BLUE, alpha=0.12,
                    label=A('مدى الاختلاف الأفقي 54′–61′'))
    ax.step(h, maj, where='post', color=RED, lw=2.2, label=A('قاعدة ابن المجدي'))
    ax.set_xlabel(A('ارتفاع القمر h (درجة)'))
    ax.set_ylabel(A('مقدار التعديل (دقائق قوس)'))
    ax.grid(alpha=0.3)
    ax.legend()
    ax.set_title(A('«تُعدِّل بزيادة درجة على الارتفاع ... إلى ثلاثين، ثلاثة أرباع إلى ستين، وبتمام الزائد دقائق»'), fontsize=13)
    save(fig, 'fig06_alt_parallax.png')


def fig_latitude(rows):
    """شكل 7: عرض القمر بقاعدة ابن المجدي مقابل الحقيقي"""
    bm = np.array([r['beta_majdi'] for r in rows])
    bt = np.array([r['beta_true'] for r in rows])
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(bt, bm, s=6, color=GREEN, alpha=0.5)
    ax.plot([-5.5, 5.5], [-5.5, 5.5], color=RED, lw=1)
    ax.set_xlabel(A('عرض القمر الحقيقي (درجة)'))
    ax.set_ylabel(A('عرض القمر بقاعدة الرسالة sin β = sin 5° sin(λ−Ω)'))
    err = bm - bt
    ax.text(-5.2, 4.6, A(f'متوسط الفرق {np.mean(err):+.2f}°، الانحراف المعياري {np.std(err):.2f}°'), fontsize=12)
    ax.grid(alpha=0.3)
    ax.set_title(A('عرض القمر من «الحصة» (بعد القمر عن الجوزهر)'), fontsize=14)
    save(fig, 'fig07_latitude.png')


def fig_criterion(rows):
    """شكل 8: مستوى (البعد المطلق، قوس الرؤية) ونطاقات ابن المجدي مع تصنيف عودة"""
    col = {'A': GREEN, 'B': GOLD, 'C': BLUE, 'D': '#9ca3af'}
    lab = {'A': 'عودة: بالعين المجردة', 'B': 'عودة: بالعين وقد تحتاج أداة', 'C': 'عودة: بالأداة فقط', 'D': 'عودة: غير ممكنة'}
    fig, ax = plt.subplots(figsize=(10, 8))
    for z in ['D', 'C', 'B', 'A']:
        pts = [(r['elong_majdi'], r['arcv_majdi']) for r in rows if r['odeh'] == z and 0 < r['elong_majdi'] < 30]
        if pts:
            x, y = zip(*pts)
            ax.scatter(x, y, s=10, color=col[z], alpha=0.65, label=A(lab[z]))
    x = np.linspace(0, 30, 200)
    for Sv, c, t in [(7, RED, 'S = 7: لا تجوز رؤيته دونه'), (10, GOLD, 'S = 10'), (13, GREEN, 'S = 13: يُرى بيّنًا')]:
        ax.plot(x, 2 * Sv - x, color=c, lw=2)
        ax.text(2 * Sv - 13.3, 13.6, A(t), color=c, fontsize=12, rotation=-45)
    ax.add_patch(plt.Rectangle((12, 12), 18, 18, fill=False, ec=INK, lw=1.4, ls='--'))
    ax.text(12.3, 25.6, A('القول الأول:\nالمكث ≥ 12 والرؤية ≥ 12\nوالارتفاع ≥ 10 → بيّن'), fontsize=11)
    ax.set_xlim(0, 30); ax.set_ylim(0, 30)
    ax.set_xlabel(A('البعد المطلق Δλ (درجة)'))
    ax.set_ylabel(A('قوس الرؤية ARCV (درجة)'))
    ax.grid(alpha=0.3)
    ax.legend(loc='lower right', fontsize=11)
    ax.set_title(A('معيار المتأخرين عند ابن المجدي  S = ½(قوس الرؤية + البعد المطلق) — القاهرة 1990–2049'), fontsize=13)
    save(fig, 'fig08_criterion_plane.png')


def fig_noon(rows):
    """شكل 9: البعد بين النيرين وقت الزوال (دل) وتوزيعه بحسب الرؤية الحديثة"""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bins = np.arange(-6, 30, 0.5)
    for z, c, t in [('D', '#9ca3af', 'غير ممكنة'), ('C', BLUE, 'بالأداة فقط'), ('B', GOLD, 'قد تحتاج أداة'), ('A', GREEN, 'بالعين المجردة')]:
        v = [r['elong_noon'] for r in rows if r['odeh'] == z]
        ax.hist(v, bins=bins, color=c, alpha=0.6, label=A('عودة: ' + t))
    ax.axvline(4.5, color=RED, lw=2.4)
    ax.text(4.7, ax.get_ylim()[1] * 0.9, A('«دل» = 4;30°'), color=RED, fontsize=13)
    ax.set_xlim(-6, 30)
    ax.set_xlabel(A('فضل ما بين مقومي النيرين نصف النهار (درجة)'))
    ax.set_ylabel(A('عدد الأمسيات'))
    ax.legend()
    ax.set_title(A('الشرط الأول في الرسالة — فضل المقومين وقت الزوال'), fontsize=14)
    save(fig, 'fig09_noon_elongation.png')


def fig_flow():
    """شكل 10: مخطط خوارزمية ابن المجدي"""
    steps = [
        'مقوما النيرين وقت الزوال (من التقويم) + البهت',
        'الشرط الأول: إن كان الفضل ≤ دل (4;30°) فالرؤية غير ممكنة',
        'حصة البعد = (نصف قوس النهار + 10°) ÷ 6 ← مقوما النيرين عند الرؤية',
        'درجة الهلال المرئية = المقوم − اختلاف الطول (51′…30′)',
        'العرض: sin β = sin 5° sin(λ−Ω) ثم العرض المرئي = β − اختلاف العرض (6′…41′)',
        'قوس المكث = فضل مطالع غروب الهلال على مطالع غروب الشمس (×4 دقائق)',
        'قوس الرؤية (انحطاط الشمس عند غروب الهلال)، قوس الارتفاع، السمت، سعة المغرب',
        'البعد المطلق Δλ، وقوس النور: cos N = cos Δλ cos β',
        'الحكم: (12، 12، 10) أو (8، 7، 10) أو S = ½(الرؤية + البعد): 7 / 10 / 13',
    ]
    fig, ax = plt.subplots(figsize=(9, 12))
    ax.axis('off')
    n = len(steps)
    for i, s in enumerate(steps):
        y = 1 - (i + 0.5) / n
        ax.add_patch(FancyBboxPatch((0.04, y - 0.035), 0.92, 0.07, boxstyle='round,pad=0.01',
                                    fc='#eef2ff' if i not in (1, 8) else '#fef3c7', ec=BLUE, lw=1.3))
        ax.text(0.5, y, A(s), ha='center', va='center', fontsize=12.5)
        if i < n - 1:
            ax.annotate('', xy=(0.5, y - 0.046 - 0.02), xytext=(0.5, y - 0.04),
                        arrowprops=dict(arrowstyle='-|>', color=BLUE, lw=1.4))
    ax.set_title(A('خوارزمية رؤية الهلال في «خلاصة الأقوال»'), fontsize=15)
    save(fig, 'fig10_flowchart.png')


def fig_lag_nights(rows):
    """شكل 11: المكث في الليلتين الثانية والثالثة بعد أول رؤية (بمعيار ابن المجدي)"""
    import json
    p = os.path.join(os.path.dirname(DATA), 'lag_nights.json')
    if not os.path.exists(p):
        return
    d = json.load(open(p))['majdi']
    n2, n3 = d['n2'], d['n3']
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.hist(n2, bins=np.arange(0.5, 4.6, 0.1), color=BLUE, alpha=0.6, label=A('الليلة الثانية من الرؤية'))
    ax.hist(n3, bins=np.arange(0.5, 4.6, 0.1), color=GOLD, alpha=0.6, label=A('الليلة الثالثة من الرؤية'))
    top = ax.get_ylim()[1]
    for v, c, t, f in [(1, BLUE, 'ساعة', 0.95), (2, BLUE, 'ساعتان', 0.95), (1.5, GOLD, 'ساعة ونصف', 0.8), (3, GOLD, 'ثلاث ساعات', 0.8)]:
        ax.axvline(v, color=c, ls='--', lw=1.5)
        ax.text(v + 0.03, top * f, A(t), color=c, fontsize=11)
    ax.set_xlabel(A('الماضي من الليل عند غروب الهلال (ساعة)'))
    ax.set_ylabel(A('عدد الشهور'))
    ax.legend(loc='center right')
    ax.set_title(A('«يجوز أن يغرب الليلة الثانية من رؤيته والماضي لا يزيد على ساعة ...» — القاهرة 1990–2049'), fontsize=13)
    save(fig, 'fig11_lag_nights.png')


if __name__ == '__main__':
    fig_quadrant(); fig_triangle(); fig_sunset_geometry(); fig_ecliptic_angle(); fig_alt_parallax(); fig_flow()
    if os.path.exists(DATA):
        rows = load_rows()
        fig_parallax_table(rows); fig_latitude(rows); fig_criterion(rows); fig_noon(rows); fig_lag_nights(rows)
