# -*- coding: utf-8 -*-
"""رسومات المفاهيم لدراسة رسالة ابن المجدي — تُكتب في figures/ بأسماء c01 … c26"""
import os, sys, csv, json, math, warnings, datetime as dt
warnings.filterwarnings('ignore')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, FancyBboxPatch, Polygon, Ellipse, Wedge, Rectangle
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
FIG = os.path.join(ROOT, 'figures')
DATA = os.path.join(ROOT, 'data')
os.makedirs(FIG, exist_ok=True)
for p in ['Amiri-Regular.ttf', 'Amiri-Bold.ttf']:
    for d in [os.path.join(ROOT, 'fonts'), os.path.expanduser('~/.fonts')]:
        if os.path.exists(os.path.join(d, p)):
            font_manager.fontManager.addfont(os.path.join(d, p))
            break
plt.rcParams.update({'font.family': ['Amiri', 'DejaVu Sans'], 'font.size': 13, 'axes.unicode_minus': False,
                     'savefig.dpi': 170, 'savefig.bbox': 'tight', 'mathtext.fontset': 'dejavuserif'})

INK, BLUE, RED, GREEN, GOLD, GREY, SKY, PURPLE = '#1f2937', '#1d4ed8', '#b91c1c', '#15803d', '#b45309', '#6b7280', '#dbeafe', '#7c3aed'
PHI, EPS = 30.0444, 23 + 35 / 60
D = math.pi / 180


def save(fig, name):
    fig.savefig(os.path.join(FIG, name))
    plt.close(fig)
    print('saved', name)


def clean(ax, eq=True):
    if eq:
        ax.set_aspect('equal')
    ax.axis('off')


def arrow(ax, a, b, c=INK, lw=1.5, style='->', ls='-'):
    ax.annotate('', xy=b, xytext=a, arrowprops=dict(arrowstyle=style, color=c, lw=lw, ls=ls))


def angle_arc(ax, center, r, t1, t2, c, label=None, lr=1.25, fs=12):
    ax.add_patch(Arc(center, 2 * r, 2 * r, theta1=t1, theta2=t2, color=c, lw=1.5))
    if label:
        m = math.radians((t1 + t2) / 2)
        ax.text(center[0] + lr * r * math.cos(m), center[1] + lr * r * math.sin(m), label, color=c,
                ha='center', va='center', fontsize=fs)


# ---------------------------------------------------------------------------
def c01_timeline():
    people = [  # (الاسم، الوفاة هـ، الوفاة م، المدينة، المستوى)
        ('ابن يونس المصري', 399, 1009, 'القاهرة (الفاطميون)', 1.2),
        ('نجم الدين المصري', 730, 1330, 'القاهرة', -1.2),
        ('ابن الشاطر', 777, 1375, 'دمشق', 1.0),
        ('الخليلي', 780, 1380, 'دمشق', -2.1),
        ('جمال الدين المارداني', 809, 1406, 'القاهرة', 2.0),
        ('ابن المجدي', 850, 1447, 'القاهرة', -1.2),
        ('سبط المارديني', 912, 1506, 'القاهرة', 1.0),
    ]
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.add_patch(Rectangle((1250, -0.35), 1517 - 1250, 0.7, color='#fef3c7', zorder=0))
    ax.text(1180, -0.62, 'دولة المماليك (648–923 هـ / 1250–1517 م)', ha='center', fontsize=13, color=GOLD)
    ax.axhline(0, color=INK, lw=2)
    for y in range(1000, 1551, 50):
        ax.plot([y, y], [-0.06, 0.06], color=INK)
        ax.text(y, -0.2, str(y), ha='center', fontsize=10, color=GREY)
    for name, h, m, city, lev in people:
        up = 1 if lev > 0 else -1
        yy = lev
        hi = name == 'ابن المجدي'
        ax.plot([m, m], [0, yy], color=RED if hi else BLUE, lw=2.2 if hi else 1.2)
        ax.plot(m, 0, 'o', color=RED if hi else BLUE, ms=9 if hi else 6)
        ax.text(m, yy + 0.08 * up, f'{name}\nت {h} هـ / {m} م — {city}', ha='center',
                va='bottom' if up > 0 else 'top', fontsize=12 if hi else 11,
                color=RED if hi else INK, fontweight='bold' if hi else 'normal',
                bbox=dict(fc='white', ec=RED if hi else '#cbd5e1', boxstyle='round,pad=0.3'))
    ax.annotate('', xy=(1366, 0.45), xytext=(1447, 0.45), arrowprops=dict(arrowstyle='<->', color=RED, lw=2))
    ax.text(1406, 0.52, 'عمر ابن المجدي 767–850 هـ', color=RED, ha='center', fontsize=11)
    ax.set_xlim(970, 1560)
    ax.set_ylim(-2.9, 2.8)
    ax.axis('off')
    ax.set_title('أعلام الفلك والميقات من ابن يونس إلى سبط المارديني', fontsize=16)
    save(fig, 'c01_timeline.png')


def c02_teachers():
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7)
    ax.axis('off')

    def box(x, y, t, fc, ec, w=2.5, h=0.62, fs=11.5):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.05', fc=fc, ec=ec, lw=1.3))
        ax.text(x, y, t, ha='center', va='center', fontsize=fs)
    box(6.5, 3.5, 'ابن المجدي\n(767–850 هـ)', '#fee2e2', RED, w=2.6, h=1.0, fs=14)
    teachers = [('البلقيني — الفقه', 1), ('ابن الملقن — الفقه', 2), ('الكمال الدميري — الفقه', 3),
                ('التقي بن عز الدين الحنبلي\nالفرائض والحساب', 4.1), ('الشمس العجيمي — العربية', 5.2),
                ('الجمال المارداني\nالميقات ومتعلقاته', 6.3)]
    for t, y in teachers:
        box(10.8, y, t, '#e0e7ff', BLUE, w=3.6, h=0.75 if '\n' in t else 0.6)
        arrow(ax, (9.0, y), (7.85, 3.5 + (y - 3.6) * 0.18), c=BLUE)
    ax.text(10.8, 6.85, 'شيوخه', ha='center', fontsize=15, color=BLUE)
    students = [('ابن الجيعان أبو زكريا الدمياطي\nالرياضيات', 6.1), ('المناوي — الحساب والفلك', 5.0),
                ('البدر المارداني', 4.1), ('النور الوراق المالكي', 3.2), ('الشهاب السجيني', 2.3),
                ('الزين زكريا', 1.4), ('البدر حسن الأعرج', 0.6)]
    for t, y in students:
        box(2.2, y, t, '#dcfce7', GREEN, w=3.6, h=0.75 if '\n' in t else 0.55)
        arrow(ax, (5.15, 3.5 + (y - 3.5) * 0.18), (4.05, y), c=GREEN)
    ax.text(2.2, 6.85, 'تلاميذه', ha='center', fontsize=15, color=GREEN)
    ax.set_title('سلسلة الأخذ: شيوخ ابن المجدي وتلاميذه (عن السخاوي والشوكاني)', fontsize=15)
    save(fig, 'c02_teachers.png')


def c03_sphere():
    """الكرة السماوية في مستوى نصف النهار"""
    fig, ax = plt.subplots(figsize=(9, 8.5))
    R = 1
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(t), np.sin(t), color=INK, lw=1.8)
    ax.plot([-1.15, 1.15], [0, 0], color=GREEN, lw=2.2)
    ax.fill_between(np.cos(t[200:]), np.sin(t[200:]), 0, color='#e5e7eb', alpha=0.6)
    phi = math.radians(PHI)
    P = (-math.cos(phi), math.sin(phi))           # القطب الشمالي جهة الشمال (يسار)
    ax.plot([-P[0], P[0]], [-P[1], P[1]], color=GREY, lw=1, ls='-.')
    e = (math.sin(phi), math.cos(phi))
    ax.plot([-e[0], e[0]], [-e[1], e[1]], color=BLUE, lw=2)
    for dd, c, lab in [(EPS, GOLD, 'مدار الشمس في أول السرطان'), (0, BLUE, None), (-EPS, PURPLE, 'مدار الشمس في أول الجدي')]:
        if dd == 0:
            continue
        cc = (math.sin(math.radians(dd)) * P[0], math.sin(math.radians(dd)) * P[1])
        r = math.cos(math.radians(dd))
        ax.plot([cc[0] - r * e[0], cc[0] + r * e[0]], [cc[1] - r * e[1], cc[1] + r * e[1]], color=c, lw=1.6, ls='--')
        ax.text(cc[0] + r * e[0] + 0.03, cc[1] + r * e[1], lab, color=c, fontsize=11)
    ax.plot(*P, 'o', color=INK); ax.text(P[0] - 0.05, P[1] + 0.05, 'القطب الشمالي', ha='right')
    ax.plot(0, 1, 'o', color=INK); ax.text(0, 1.06, 'سمت الرأس', ha='center')
    ax.plot(0, -1, 'o', color=INK); ax.text(0, -1.1, 'النظير', ha='center')
    ax.text(e[0] + 0.03, e[1] + 0.02, 'معدل النهار', color=BLUE, fontsize=12)
    ax.text(1.17, 0.03, 'الجنوب', fontsize=12); ax.text(-1.17, 0.03, 'الشمال', ha='right', fontsize=12)
    ax.text(0.55, -0.08, 'الأفق', color=GREEN, fontsize=13)
    angle_arc(ax, (0, 0), 0.3, 180 - PHI, 180, RED, 'φ', 1.35)
    ax.text(-1.1, -0.2, 'ارتفاع القطب φ = عرض البلد', color=RED, fontsize=11)
    angle_arc(ax, (0, 0), 0.22, 90 - PHI, 90, GOLD, '', 1.3)
    ax.text(0.07, 0.3, '90 − φ', color=GOLD, fontsize=11)
    ax.text(-1.15, -1.32, 'ما فوق الخط الأخضر ظاهر من الكرة، وما تحته خفي. الكواكب تدور على دوائر موازية لمعدل النهار،', fontsize=11)
    ax.text(-1.15, -1.45, 'فيكون قوس النهار هو ما فوق الأفق من مدار الكوكب. وفي القاهرة يرتفع القطب 30° تقريبًا.', fontsize=11)
    ax.set_xlim(-1.3, 1.5); ax.set_ylim(-1.5, 1.2)
    clean(ax)
    ax.set_title('الكرة السماوية في مستوى دائرة نصف النهار — القاهرة', fontsize=15)
    save(fig, 'c03_sphere.png')


def c04_ecliptic():
    """الميل والمطالع: المثلث بين معدل النهار وفلك البروج"""
    fig, ax = plt.subplots(figsize=(11, 6))
    lam = np.linspace(0, 360, 361)
    dec = np.degrees(np.arcsin(np.sin(math.radians(EPS)) * np.sin(np.radians(lam))))
    ax.axhline(0, color=BLUE, lw=2)
    ax.plot(lam, dec, color=GOLD, lw=2.4)
    ax.text(362, 1, 'معدل النهار', color=BLUE, fontsize=12)
    ax.text(120, 23, 'فلك البروج (طريق الشمس السنوي)', color=GOLD, fontsize=12)
    L = 50
    d = math.degrees(math.asin(math.sin(math.radians(EPS)) * math.sin(math.radians(L))))
    a = math.degrees(math.atan2(math.cos(math.radians(EPS)) * math.sin(math.radians(L)), math.cos(math.radians(L))))
    ax.plot(L, d, 'o', color=RED, ms=10); ax.text(L - 2, d + 2, 'الشمس', color=RED, ha='right')
    ax.plot([a, L], [0, d], color=RED, lw=1.5, ls='--')
    ax.annotate('', xy=(a, d), xytext=(a, 0), arrowprops=dict(arrowstyle='<->', color=RED, lw=1.8))
    ax.text(a + 1.5, d / 2, f'الميل δ ≈ {d:.1f}°', color=RED, fontsize=12)
    ax.annotate('', xy=(L, -3.2), xytext=(0, -3.2), arrowprops=dict(arrowstyle='<->', color=GOLD, lw=1.6))
    ax.text(L / 2, -5.2, f'بعد الدرجة λ = {L}° (على البروج)', color=GOLD, ha='center', fontsize=11)
    ax.annotate('', xy=(a, -8.2), xytext=(0, -8.2), arrowprops=dict(arrowstyle='<->', color=BLUE, lw=1.6))
    ax.text(a / 2, -10.3, f'المطالع α ≈ {a:.1f}° (على المعدل)', color=BLUE, ha='center', fontsize=11)
    for x, t in [(0, 'رأس الحمل'), (90, 'رأس السرطان'), (180, 'رأس الميزان'), (270, 'رأس الجدي'), (360, 'رأس الحمل')]:
        ax.plot([x, x], [-1, 1], color=INK)
        ax.text(x, 26.5 if x in (90,) else (-26.5 if x == 270 else 2), t, ha='center', fontsize=11)
    ax.text(30, 13, 'ε = 23;35°  (الميل الأعظم)', color=PURPLE, fontsize=12)
    ax.text(185, -18, 'sin δ = sin ε · sin λ        tan α = cos ε · tan λ', fontsize=13,
            bbox=dict(fc='white', ec=GREY))
    ax.set_xlim(-10, 380); ax.set_ylim(-28, 29)
    ax.set_xlabel('الطول على فلك البروج (درجة)'); ax.set_ylabel('الميل (درجة)')
    ax.grid(alpha=0.25)
    ax.set_title('الميل والمطالع: الشمس على فلك البروج وظلّها على معدل النهار', fontsize=15)
    save(fig, 'c04_ecliptic.png')


def c05_quadrant_ops():
    """أعمال الربع الثلاثة: التجييب والتقويس والنقل"""
    fig, axs = plt.subplots(1, 3, figsize=(16, 6))
    th = np.linspace(0, np.pi / 2, 100)
    for ax in axs:
        ax.plot(60 * np.cos(th), 60 * np.sin(th), color=INK, lw=1.6)
        ax.plot([0, 60], [0, 0], color=INK, lw=1.6); ax.plot([0, 0], [0, 60], color=INK, lw=1.6)
        for i in range(10, 60, 10):
            ax.plot([i, i], [0, math.sqrt(3600 - i * i)], color='#d1d5db', lw=0.6)
            ax.plot([0, math.sqrt(3600 - i * i)], [i, i], color='#d1d5db', lw=0.6)
        ax.text(30, -6, 'الستيني', ha='center', fontsize=11)
        ax.set_xlim(-8, 70); ax.set_ylim(-12, 68); clean(ax)
    # التجييب
    ax = axs[0]; a = 35
    x, y = 60 * math.cos(math.radians(a)), 60 * math.sin(math.radians(a))
    ax.plot([0, x], [0, y], color=RED, lw=2)
    arrow(ax, (x, y), (0, y), c=BLUE, ls='--')
    ax.text(x + 2, y + 2, '35°', color=RED)
    ax.text(1, y + 2, f'R sin 35° = {60 * math.sin(math.radians(a)):.1f}', color=BLUE, fontsize=11)
    ax.set_title('1) التجييب: من القوس إلى جيبه', fontsize=14)
    # التقويس
    ax = axs[1]; s = 45
    xx = math.sqrt(3600 - s * s)
    arrow(ax, (0, s), (xx, s), c=BLUE, ls='--')
    ax.plot([0, xx], [0, s], color=RED, lw=2)
    ax.text(xx + 1, s + 2, f'{math.degrees(math.asin(s / 60)):.1f}°', color=RED)
    ax.text(1, s + 2, 'الجيب 45', color=BLUE, fontsize=11)
    ax.set_title('2) التقويس: من الجيب إلى قوسه', fontsize=14)
    # النقل
    ax = axs[2]; m = 40; b = 30
    ax.plot([0, 0], [0, 60], color=RED, lw=2.5)
    ax.plot(0, m, 'o', color=GOLD, ms=10)
    ax.text(2, m, 'المري على 40', color=GOLD, fontsize=11)
    X, Y = m * math.cos(math.radians(b)), m * math.sin(math.radians(b))
    ax.plot([0, 60 * math.cos(math.radians(b))], [0, 60 * math.sin(math.radians(b))], color=RED, lw=2, ls='-')
    ax.plot(X, Y, 'o', color=GOLD, ms=10)
    ax.add_patch(Arc((0, 0), 2 * m, 2 * m, theta1=b, theta2=90, color=GOLD, lw=1.2, ls=':'))
    arrow(ax, (X, Y), (X, 0), c=BLUE, ls='--')
    ax.text(X + 1, Y / 2, f'40 × sin 30° = {m * math.sin(math.radians(b)):.0f}', color=BLUE, fontsize=11)
    ax.text(X - 4, -10, f'40 × cos 30° = {m * math.cos(math.radians(b)):.1f}', color=PURPLE, fontsize=11, ha='center')
    ax.set_title('3) النقل: ضرب عددٍ في جيب قوس', fontsize=14)
    fig.suptitle('الأعمال الثلاثة التي تقوم عليها مسائل الرسالة كلها', fontsize=16, y=1.02)
    save(fig, 'c05_quadrant_ops.png')


def c06_shadow():
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot([-1, 13], [0, 0], color=INK, lw=2)
    ax.text(12.5, -0.5, 'سطح الأفق', ha='center')
    ax.plot([0, 0], [0, 4], color=GOLD, lw=5)
    ax.text(-0.3, 2, 'المقياس\n(القامة = 12 إصبعًا)', ha='right', va='center', color=GOLD)
    h = 25
    z = 4 / math.tan(math.radians(h))
    ax.plot([0, z], [4, 0], color=RED, lw=1.6)
    for k in (0.6, 1.2):
        ax.plot([0 + k * 0.3, z + k * 0.3 + 1.5], [4 + k * 0.7 + 0.7, 0.7 * k], color='#fbbf24', lw=1, ls=':')
    ax.plot([0, z], [0, 0], color=BLUE, lw=6, alpha=0.7)
    ax.text(z / 2, -0.55, 'الظل المبسوط  z = 12 · ctg h', color=BLUE, ha='center', fontsize=13)
    ax.text(z / 2 + 0.3, 2.3, 'قطر الظل  d = 12 / sin h', color=RED, fontsize=13, rotation=-17)
    angle_arc(ax, (z, 0), 1.3, 180 - h, 180, GREEN, 'h', 1.25)
    ax.text(z - 2.6, 0.25, 'الارتفاع', color=GREEN, fontsize=11)
    ax.plot(z + 1.9, 4.6, 'o', color='#f59e0b', ms=22)
    ax.text(z + 1.9, 5.35, 'الشمس', ha='center')
    # الظل المنكوس
    ox = -0.5
    ax.text(5.5, 4.9, 'كلما انخفضت الشمس طال الظل المبسوط؛ وعند ارتفاع 45° يساوي الظلُّ القامةَ.', fontsize=12)
    ax.set_xlim(-3, 13.5); ax.set_ylim(-1.2, 5.8)
    clean(ax)
    ax.set_title('الظل وقطره: «وضعت الخيط على مثل الارتفاع ... وجدت الظل ... وجدت قطره»', fontsize=15)
    save(fig, 'c06_shadow.png')


def c07_ghaya():
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.plot([-1.2, 1.2], [0, 0], color=GREEN, lw=2)
    t = np.linspace(0, np.pi, 200)
    ax.plot(np.cos(t), np.sin(t), color=INK, lw=1.5)
    for dd, c, lab in [(EPS, GOLD, 'أول السرطان'), (0, BLUE, 'الاعتدال'), (-EPS, PURPLE, 'أول الجدي')]:
        H = 90 - PHI + dd
        x, y = math.cos(math.radians(H)), math.sin(math.radians(H))
        ax.plot([0, x], [0, y], color=c, lw=1.8)
        ax.plot(x, y, 'o', color=c, ms=12)
        ax.text(x * 1.1 + (0.18 if dd > 0 else 0), y * 1.06, f'{lab}: {H:.1f}°', color=c, ha='center', fontsize=12)
    angle_arc(ax, (0, 0), 0.35, 0, 90 - PHI, BLUE, '90 − φ', 1.45)
    ax.text(-1.15, -0.15, 'الشمال', fontsize=12); ax.text(1.05, -0.15, 'الجنوب', fontsize=12)
    ax.text(-0.12, 1.03, 'سمت الرأس', ha='right')
    ax.plot(0, 1, 'o', color=INK)
    ax.text(-1.15, 0.95, 'الغاية = تمام العرض + الميل الشمالي', fontsize=13)
    ax.text(-1.15, 0.83, 'الغاية = تمام العرض − الميل الجنوبي', fontsize=13)
    ax.text(-1.15, 0.71, 'فإن جاوز المجموعُ 90 أُخذ تمامه إلى 180', fontsize=12, color=GREY)
    ax.set_xlim(-1.25, 1.3); ax.set_ylim(-0.25, 1.2)
    clean(ax)
    ax.set_title('الغاية (ارتفاع الشمس وقت الزوال) في القاهرة على مدار السنة', fontsize=15)
    save(fig, 'c07_ghaya.png')


def c08_day_arcs():
    fig, axs = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [1.25, 1]})
    ax = axs[0]
    phi = math.radians(PHI)
    for dd, c, lab in [(EPS, GOLD, 'أول السرطان'), (0, BLUE, 'الاعتدالان'), (-EPS, PURPLE, 'أول الجدي')]:
        d = math.radians(dd)
        H0 = math.degrees(math.acos(-math.tan(phi) * math.tan(d)))
        tt = np.linspace(-H0, H0, 300)
        alt = np.degrees(np.arcsin(np.sin(phi) * np.sin(d) + np.cos(phi) * np.cos(d) * np.cos(np.radians(tt))))
        az = np.degrees(np.arctan2(np.sin(np.radians(tt)), np.cos(np.radians(tt)) * np.sin(phi) - np.tan(d) * np.cos(phi)))
        ax.plot(az, alt, color=c, lw=2.2, label=f'{lab}: نصف القوس {H0:.1f}° = {H0 / 15:.2f} ساعة')
    ax.axhline(0, color=GREEN, lw=2)
    ax.set_xticks([-120, -90, -60, -30, 0, 30, 60, 90, 120])
    ax.set_xticklabels(['', 'المشرق', '', '', 'الجنوب', '', '', 'المغرب', ''])
    ax.set_ylabel('الارتفاع (درجة)')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(alpha=0.25)
    ax.set_title('مسير الشمس اليومي فوق أفق القاهرة', fontsize=14)
    ax = axs[1]
    days = np.arange(0, 365)
    lam = (days - 79) * 360 / 365.25
    d = np.arcsin(math.sin(math.radians(EPS)) * np.sin(np.radians(lam)))
    half = np.degrees(np.arccos(-math.tan(phi) * np.tan(d)))
    ax.plot(days, 2 * half / 15, color=GOLD, lw=2.4, label='طول النهار = قوس النهار ÷ 15')
    ax.axhline(12, color=BLUE, ls='--')
    ax.fill_between(days, 12, 2 * half / 15, where=2 * half / 15 > 12, color=GOLD, alpha=0.2, label='التعديل (زيادة)')
    ax.fill_between(days, 2 * half / 15, 12, where=2 * half / 15 < 12, color=PURPLE, alpha=0.2, label='التعديل (نقص)')
    ax.set_xticks([0, 79, 172, 266, 355]); ax.set_xticklabels(['يناير', 'الاعتدال', 'السرطان', 'الاعتدال', 'الجدي'])
    ax.set_ylabel('ساعات'); ax.legend(fontsize=11, loc='lower center'); ax.grid(alpha=0.25)
    ax.set_title('قوس النهار والتعديل على مدار السنة', fontsize=14)
    fig.suptitle('نصف قوس النهار = 90° ± نصف التعديل،  sin(نصف التعديل) = tan φ · tan δ', fontsize=15, y=1.02)
    save(fig, 'c08_day_arcs.png')


def c09_analemma():
    """أصل طريقة المحفوظين: تحليل ارتفاع الشمس إلى بعد القطر + الأصل × جيب تمام فضل الدائر"""
    fig, ax = plt.subplots(figsize=(11, 9))
    R = 6
    phi = math.radians(PHI); d = math.radians(18); t = math.radians(50)
    t_ = np.linspace(0, 2 * np.pi, 300)
    ax.plot(R * np.cos(t_), R * np.sin(t_), color=INK, lw=1.4)
    ax.plot([-R - 0.6, R + 0.6], [0, 0], color=GREEN, lw=2.2)
    u = np.array([-math.cos(phi), math.sin(phi)])           # نحو القطب
    e = np.array([math.sin(phi), math.cos(phi)])            # في مستوى المعدل نحو الجنوب العالي
    ax.plot(*zip(-R * u, R * u), color=GREY, lw=1, ls='-.')
    ax.plot(*zip(-R * e, R * e), color=BLUE, lw=1.5)
    C = R * math.sin(d) * u
    r = R * math.cos(d)
    A1, A2 = C - r * e, C + r * e
    ax.plot(*zip(A1, A2), color=GOLD, lw=3)
    ax.text(*(A2 + np.array([0.1, 0.2])), 'مدار الشمس (مُسقَطًا على خط)', color=GOLD, fontsize=12)
    ax.plot(*C, 'o', color=INK)
    X = C + r * math.cos(t) * e
    ax.plot(*X, 'o', color=RED, ms=12)
    ax.text(X[0] + 0.25, X[1] + 0.35, 'الشمس (مُسقَطة)', color=RED)
    # الارتفاع الكلي
    ax.plot([X[0], X[0]], [0, X[1]], color=RED, lw=3)
    ax.plot([X[0] - 1.6, X[0] + 0.1], [C[1], C[1]], color=GREY, lw=1, ls=':')
    ax.annotate('', xy=(X[0] + 0.5, C[1]), xytext=(X[0] + 0.5, 0), arrowprops=dict(arrowstyle='<->', color=PURPLE, lw=2))
    ax.text(X[0] + 0.65, C[1] / 2, 'بعد القطر = R sin δ sin φ', color=PURPLE, fontsize=13, va='center')
    ax.annotate('', xy=(X[0] + 0.5, X[1]), xytext=(X[0] + 0.5, C[1]), arrowprops=dict(arrowstyle='<->', color=BLUE, lw=2))
    ax.text(X[0] + 0.65, (X[1] + C[1]) / 2, 'الأصل × cos t = R cos δ cos φ cos t', color=BLUE, fontsize=13, va='center')
    ax.text(X[0] - 0.2, C[1] + 0.3, 'R sin h', color=RED, fontsize=14, ha='right')
    ax.annotate('', xy=X, xytext=C, arrowprops=dict(arrowstyle='<->', color=GOLD, lw=1.5))
    ax.text(*((X + C) / 2 + np.array([-1.3, 0.1])), 'R cos δ cos t\n(جيب الترتيب)', color=GOLD, fontsize=11, ha='center')
    ax.text(-R - 0.5, 0.2, 'الشمال', fontsize=12); ax.text(R + 0.1, 0.2, 'الجنوب', fontsize=12)
    ax.text(*(R * u + np.array([-0.2, 0.2])), 'القطب', ha='right')
    ax.text(*(R * e + np.array([0.1, 0.1])), 'معدل النهار', color=BLUE)
    ax.text(-R, -R - 0.9, 'R sin h  =  بعد القطر  +  الأصل · cos t', fontsize=16, color=INK,
            bbox=dict(fc='#fef9c3', ec=GOLD))
    ax.text(-R, -R - 1.8, 'وبالقسمة على cos φ:  المحفوظ الثاني − المحفوظ الأول = جيب الترتيب', fontsize=14)
    ax.set_xlim(-R - 1, R + 6.5); ax.set_ylim(-R - 2.2, R + 0.8)
    clean(ax)
    ax.set_title('سرّ «المحفوظين»: تحليل ارتفاع الشمس في مستوى نصف النهار', fontsize=15)
    save(fig, 'c09_analemma.png')


def c10_asr():
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot([-1, 14], [0, 0], color=INK, lw=2)
    ax.plot([0, 0], [0, 3], color=GOLD, lw=5)
    H = 60
    z0 = 3 / math.tan(math.radians(H))
    ax.plot([0, z0], [0, 0], color=BLUE, lw=7, alpha=0.8)
    ax.text(z0 / 2, -0.45, 'ظل الزوال', color=BLUE, ha='center')
    ax.plot([z0, z0 + 3], [0, 0], color=RED, lw=7, alpha=0.8)
    ax.text(z0 + 1.5, -0.45, '+ قامة', color=RED, ha='center')
    ha = math.degrees(math.atan(1 / (1 / math.tan(math.radians(H)) + 1)))
    ax.plot([0, z0 + 3], [3, 0], color=RED, lw=1.4, ls='--')
    ax.plot([0, z0], [3, 0], color=BLUE, lw=1.4, ls='--')
    ax.text(5.5, 2.4, f'مثال: غاية {H}° ← ظل الزوال {12 / math.tan(math.radians(H)):.1f} إصبعًا', fontsize=13)
    ax.text(5.5, 1.8, f'ظل العصر = {12 / math.tan(math.radians(H)):.1f} + 12 = {12 / math.tan(math.radians(H)) + 12:.1f} ← ارتفاع العصر {ha:.1f}°', fontsize=13)
    ax.text(5.5, 1.2, 'ctg h(العصر) = ctg (الغاية) + 1', fontsize=14, color=RED)
    ax.set_xlim(-2, 14); ax.set_ylim(-1, 3.5)
    clean(ax)
    ax.set_title('ارتفاع العصر: «إن زدت على ظل مبسوط الغاية قامة واستخرجت ارتفاع الجملة»', fontsize=15)
    save(fig, 'c10_asr.png')


def c11_twilight():
    fig, ax = plt.subplots(figsize=(12, 6))
    ys = np.linspace(-25, 30, 300)
    for i in range(len(ys) - 1):
        y = ys[i]
        c = '#0f172a' if y < -19 else ('#1e3a8a' if y < -17 else ('#c2410c' if y < 0 else '#bfdbfe'))
        ax.axhspan(ys[i], ys[i + 1], color=c, alpha=0.35 if y < 0 else 0.25, lw=0)
    ax.axhline(0, color=GREEN, lw=2.5); ax.text(9.5, 0.6, 'الأفق', color=GREEN, fontsize=13)
    ax.axhline(-17, color=GOLD, lw=2, ls='--'); ax.axhline(-19, color='#93c5fd', lw=2, ls='--')
    ax.text(0.2, -15.6, 'يز = 17°: غروب الشفق الأحمر (العشاء)', color=INK, fontsize=13)
    ax.text(0.2, -22.5, 'يط = 19°: طلوع الفجر الصادق', color='white', fontsize=13)
    ax.plot(5, -17, 'o', color='#f59e0b', ms=18)
    ax.annotate('', xy=(6.2, -17), xytext=(6.2, 0), arrowprops=dict(arrowstyle='<->', color=INK, lw=2))
    ax.text(6.4, -8.5, 'انحطاط الشمس\n= ارتفاع نظيرها', color=INK, fontsize=12)
    ax.text(0.2, 20, 'يحسب ابن المجدي «الدائر» لارتفاعٍ قدره 19 أو 17 «بدرجة النظير»:\n'
            'أي يعامل نظير الشمس (النقطة المقابلة لها) كأنه كوكب فوق الأفق ارتفاعه 19° أو 17°.', fontsize=12)
    ax.set_xlim(0, 12); ax.set_ylim(-25, 30)
    ax.set_xticks([]); ax.set_ylabel('ارتفاع الشمس (درجة)')
    ax.set_title('حصتا الفجر والشفق', fontsize=15)
    save(fig, 'c11_twilight.png')


def c12_qibla():
    fig, axs = plt.subplots(1, 2, figsize=(15, 6.5), gridspec_kw={'width_ratios': [1.2, 1]})
    ax = axs[0]
    cai = (31.2357, 30.0444); mec = (39.8262, 21.4225)

    def xyz(lo, la):
        lo, la = math.radians(lo), math.radians(la)
        return np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])
    a, b = xyz(*cai), xyz(*mec)
    om = math.acos(np.dot(a, b))
    pts = [(math.sin((1 - f) * om) * a + math.sin(f * om) * b) / math.sin(om) for f in np.linspace(0, 1, 50)]
    lo = [math.degrees(math.atan2(p[1], p[0])) for p in pts]; la = [math.degrees(math.asin(p[2])) for p in pts]
    ax.plot(lo, la, color=RED, lw=2.5, label='أقصر طريق (دائرة عظمى)')
    ax.plot(*cai, 'o', color=BLUE, ms=11); ax.text(cai[0] - 0.4, cai[1] + 0.4, 'القاهرة', ha='right', fontsize=13)
    ax.plot(*mec, 's', color=GREEN, ms=11); ax.text(mec[0] + 0.4, mec[1], 'مكة المكرمة', fontsize=13)
    arrow(ax, cai, (cai[0], cai[1] + 3), c=INK)
    ax.text(cai[0], cai[1] + 3.3, 'الشمال', ha='center')
    ax.add_patch(Arc(cai, 3, 3, theta1=90 - 136.1, theta2=90, color=GOLD, lw=2))
    ax.text(cai[0] + 1.9, cai[1] + 0.9, 'سمت القبلة\n136° من الشمال', color=GOLD, fontsize=12)
    ax.set_xlim(26, 45); ax.set_ylim(18, 35); ax.set_aspect('equal'); ax.grid(alpha=0.3)
    ax.set_xlabel('الطول (درجة)'); ax.set_ylabel('العرض (درجة)'); ax.legend(loc='lower left')
    ax.set_title('سمت القبلة في القاهرة', fontsize=14)
    ax = axs[1]
    P, Z, M = (0, 0.95), (-0.65, 0.05), (0.6, -0.4)
    for p, q in [(P, Z), (P, M), (Z, M)]:
        ax.plot(*zip(p, q), color=INK, lw=1.8)
    for p, t in [(P, 'القطب'), (Z, 'القاهرة (سمت الرأس)'), (M, 'مكة (تُعامَل كوكبًا)')]:
        ax.plot(*p, 'o', color=RED); ax.text(p[0], p[1] + (0.07 if p[1] > 0 else -0.12), t, ha='center', fontsize=12)
    ax.text(-0.62, 0.55, '90 − عرض القاهرة', fontsize=11, ha='center', rotation=54)
    ax.text(0.42, 0.3, '90 − عرض مكة\n(= تمام «الميل»)', fontsize=11)
    ax.text(0.04, 0.62, 'زاوية القطب =\nفضل الطولين\n(«فضل الدائر»)', fontsize=10.5, color=BLUE, ha='center')
    ax.text(-0.42, -0.02, 'السمت', fontsize=12, color=GOLD)
    ax.text(-0.9, -0.75, 'فكرة ابن المجدي: اجعل عرض مكة «ميلًا» وفضل الطولين «فضل دائر»،\nثم احسب سمت هذا «الكوكب» فيكون هو سمت القبلة.', fontsize=12)
    ax.set_xlim(-1, 1); ax.set_ylim(-0.95, 1.2); clean(ax)
    ax.set_title('المثلث الكروي للقبلة', fontsize=14)
    save(fig, 'c12_qibla.png')


def c13_eastwest():
    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(np.cos(t), np.sin(t), color=INK, lw=1.6)
    ax.plot(0, 0, 'o', color=GOLD, ms=12); ax.text(0.05, 0.06, 'الشاقول/المقياس', fontsize=11)
    shadow_dir = math.radians(200)
    S = (math.cos(shadow_dir), math.sin(shadow_dir))
    ax.plot([0, S[0]], [0, S[1]], color=GREY, lw=6, alpha=0.6)
    ax.text(S[0] - 0.05, S[1] - 0.1, 'طرف الظل', ha='right', fontsize=12)
    A = 35
    E = (math.cos(shadow_dir + math.radians(A)), math.sin(shadow_dir + math.radians(A)))
    ax.add_patch(Arc((0, 0), 1.0, 1.0, theta1=math.degrees(shadow_dir), theta2=math.degrees(shadow_dir) + A, color=RED, lw=2))
    ax.text(-0.62, -0.06, 'سمت الوقت', color=RED, fontsize=12)
    ax.plot([E[0], -E[0]], [E[1], -E[1]], color=BLUE, lw=2.5)
    ax.text(E[0] - 0.05, E[1] + 0.05, 'المغرب', color=BLUE, ha='right', fontsize=13)
    ax.text(-E[0] + 0.05, -E[1] - 0.05, 'المشرق', color=BLUE, fontsize=13, va='top')
    ax.plot([-E[1], E[1]], [E[0], -E[0]], color=GREEN, lw=1.5, ls='--')
    ax.text(E[1] + 0.05, -E[0], 'خط نصف النهار', color=GREEN, fontsize=12)
    ax.text(-1.05, -1.25, 'يُرسم على الأرض دائرة حول المقياس، ويُعلَّم طرف الظل على محيطها،\n'
            'ثم يُبعد عنه بقدر سمت الوقت في خلاف جهته، فيُخرَج من ثَمّ قطرٌ هو خط المشرق والمغرب.', fontsize=11.5)
    ax.set_xlim(-1.2, 1.3); ax.set_ylim(-1.45, 1.2); clean(ax)
    ax.set_title('إقامة خط المشرق والمغرب بظل الشاقول', fontsize=15)
    save(fig, 'c13_eastwest.png')


def c14_ascensions():
    signs = ['الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'السنبلة', 'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت']

    def ra(l):
        return math.degrees(math.atan2(math.cos(math.radians(EPS)) * math.sin(math.radians(l)), math.cos(math.radians(l)))) % 360

    def oa(l):
        d = math.asin(math.sin(math.radians(EPS)) * math.sin(math.radians(l)))
        return (ra(l) - math.degrees(math.asin(math.tan(math.radians(PHI)) * math.tan(d)))) % 360
    rr, oo = [], []
    for i in range(12):
        a, b = i * 30, i * 30 + 30
        rr.append((ra(b) - ra(a)) % 360 or 360)
        oo.append((oa(b) - oa(a)) % 360)
    x = np.arange(12)
    fig, ax = plt.subplots(figsize=(13, 5.8))
    ax.bar(x - 0.2, rr, 0.4, color=BLUE, label='المطالع الفلكية (خط الاستواء)')
    ax.bar(x + 0.2, oo, 0.4, color=GOLD, label='مطالع البلد (القاهرة)')
    ax.axhline(30, color=RED, ls='--'); ax.text(11.6, 30.6, '30°', color=RED)
    ax.set_xticks(x); ax.set_xticklabels(signs)
    ax.set_ylabel('أجزاء معدل النهار التي تطلع مع البرج')
    ax.legend(); ax.grid(axis='y', alpha=0.3)
    ax.set_title('مطالع البروج: كل برج 30° على البروج، لكن ما يطلع معه من معدل النهار يختلف', fontsize=15)
    save(fig, 'c14_ascensions.png')


def c15_moon_orbit():
    fig, ax = plt.subplots(figsize=(13, 5.5))
    om = 60
    lam = np.linspace(0, 360, 400)
    beta = np.degrees(np.arcsin(math.sin(math.radians(5)) * np.sin(np.radians(lam - om))))
    ax.axhline(0, color=GOLD, lw=2.5); ax.text(362, 0.2, 'فلك البروج', color=GOLD)
    ax.plot(lam, beta, color=BLUE, lw=2.5); ax.text(160, 5.4, 'فلك القمر المائل', color=BLUE)
    ax.plot(om, 0, 'o', color=RED, ms=12); ax.text(om - 3, -1.4, 'الرأس (الجوزهر)\nالعقدة الصاعدة', color=RED, ha='right', fontsize=11)
    ax.plot(om + 180, 0, 'o', color=PURPLE, ms=12); ax.text(om + 186, 0.5, 'الذنب', color=PURPLE, ha='center', fontsize=12)
    L = 110
    b = math.degrees(math.asin(math.sin(math.radians(5)) * math.sin(math.radians(L - om))))
    ax.plot(L, b, 'o', color='#64748b', ms=14)
    ax.annotate('', xy=(L, b), xytext=(L, 0), arrowprops=dict(arrowstyle='<->', color=GREEN, lw=2))
    ax.text(L + 2, b / 2, f'عرض القمر β = {b:.2f}°', color=GREEN, fontsize=12)
    ax.annotate('', xy=(L, -2.2), xytext=(om, -2.2), arrowprops=dict(arrowstyle='<->', color=RED, lw=1.6))
    ax.text((L + om) / 2, -2.9, 'الحصة F = مقوم القمر − مقوم الجوزهر', color=RED, ha='center', fontsize=12)
    ax.text(250, 3.6, 'sin β = sin 5° · sin F\nشمالي إن كانت الحصة أقل من ستة بروج', fontsize=13, bbox=dict(fc='white', ec=GREY))
    ax.set_xlim(-5, 380); ax.set_ylim(-6.2, 6.5)
    ax.set_xlabel('الطول على فلك البروج (درجة)'); ax.set_ylabel('العرض (درجة)')
    ax.grid(alpha=0.25)
    ax.set_title('عرض القمر من «الحصة»: ميل فلك القمر عن فلك البروج خمس درجات', fontsize=15)
    save(fig, 'c15_moon_orbit.png')


def c16_baht():
    fig, ax = plt.subplots(figsize=(12, 6))
    t = np.array([0, 24])
    lm = np.array([350.0, 363.2]); ls = np.array([358.0, 359.0])
    ax.plot(t, lm, color=BLUE, lw=2.5, label='مقوم القمر (بهته 13;12° في اليوم)')
    ax.plot(t, ls, color=GOLD, lw=2.5, label='مقوم الشمس (بهتها 1° في اليوم)')
    to = 6 + 40 / 60
    ax.axvline(to, color=RED, ls='--')
    ax.text(to + 0.2, 359.6, 'وقت الرؤية = نصف قوس النهار + 10°\n(الغروب + 40 دقيقة)', color=RED, fontsize=11)
    ym, ys = np.interp(to, t, lm), np.interp(to, t, ls)
    ax.plot(to, ym, 'o', color=BLUE, ms=10); ax.plot(to, ys, 'o', color=GOLD, ms=10)
    ax.annotate('', xy=(to - 0.3, ym), xytext=(to - 0.3, ys), arrowprops=dict(arrowstyle='<->', color=GREEN, lw=1.8))
    ax.text(to - 0.5, (ym + ys) / 2, 'البعد\nعند الرؤية', color=GREEN, ha='right', fontsize=11)
    ax.annotate('', xy=(0.3, 350), xytext=(0.3, 358), arrowprops=dict(arrowstyle='<->', color=PURPLE, lw=1.5))
    ax.text(0.6, 352.5, 'القمر خلف الشمس\n(قبل الاقتران)', color=PURPLE, fontsize=11)
    ax.set_xticks([0, 6, 12, 18, 24]); ax.set_xticklabels(['زوال اليوم الأول', '6 س', '12 س', '18 س', 'زوال اليوم الثاني'])
    ax.set_ylabel('المقوم (درجة)')
    ax.legend(loc='lower right'); ax.grid(alpha=0.3)
    ax.text(9.0, 363.0, 'المقوم لوقت مفروض = مقوم الزوال + البهت × (الزمن بالأجزاء ÷ 6) ÷ 60', fontsize=12,
            bbox=dict(fc='white', ec=GREY))
    ax.set_title('تقويم النيرين لوقت الرؤية بالبهت (استيفاء خطي بين زوالين)', fontsize=15)
    save(fig, 'c16_baht.png')


def c17_parallax():
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.add_patch(Circle((0, 0), 1, color='#bfdbfe', ec=BLUE, lw=1.5))
    ax.plot(0, 0, 'o', color=INK); ax.text(0.05, -0.15, 'مركز الأرض', fontsize=11)
    O = (math.cos(math.radians(60)), math.sin(math.radians(60)))
    ax.plot(*O, 'o', color=RED, ms=9); ax.text(O[0] - 0.1, O[1] + 0.1, 'الراصد', color=RED, ha='right')
    tang = np.array([math.sin(math.radians(60)), -math.cos(math.radians(60))])
    ax.plot([O[0] - 2 * tang[0], O[0] + 6 * tang[0]], [O[1] - 2 * tang[1], O[1] + 6 * tang[1]], color=GREEN, lw=1.5)
    ax.text(O[0] + 5.5 * tang[0], O[1] + 5.5 * tang[1] - 0.25, 'أفق الراصد', color=GREEN)
    M = (6.5, 1.4)
    ax.plot(*M, 'o', color='#64748b', ms=20); ax.text(M[0], M[1] + 0.35, 'القمر', ha='center')
    ax.plot([0, M[0]], [0, M[1]], color=BLUE, lw=1.6); ax.plot([O[0], M[0]], [O[1], M[1]], color=RED, lw=1.6)
    ax.text(3.3, 0.45, 'جهة القمر من مركز الأرض', color=BLUE, fontsize=11, rotation=12)
    ax.text(3.0, 1.35, 'جهة القمر من الراصد (أخفض)', color=RED, fontsize=11, rotation=2)
    ax.add_patch(Arc(M, 2.2, 2.2, theta1=180, theta2=192, color=GOLD, lw=2))
    ax.text(M[0] - 1.45, M[1] - 0.05, 'p', color=GOLD, fontsize=15)
    ax.text(-1.2, -1.6, 'اختلاف المنظر p: يرى الراصد القمرَ أخفض مما يُرى من مركز الأرض (الرسم مُبالَغ فيه).\n'
            'عند الأفق p ≈ 57′ تقريبًا، ويقل بارتفاع القمر: p ≈ 57′ · cos h. وللشمس يكاد يكون صفرًا لبعدها.', fontsize=12)
    ax.set_xlim(-1.4, 7.4); ax.set_ylim(-1.9, 2.3); clean(ax)
    ax.set_title('اختلاف المنظر: لماذا يُنقص ابن المجدي «دقائق اختلاف الطول» من مقوم الهلال', fontsize=15)
    save(fig, 'c17_parallax.png')


def c18_lag():
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))
    for ax, (title, moon_y, sun_y) in zip(axs, [('لحظة غروب الشمس', 6.0, 0.0), ('لحظة غروب الهلال', 0.0, -6.0)]):
        ax.axhspan(-9, 0, color='#e5e7eb'); ax.axhline(0, color=GREEN, lw=2.5)
        slope = math.tan(math.radians(90 - PHI))
        for x0, y, c, lab, ms in [(0, sun_y, '#f59e0b', 'الشمس', 20), (2.6, moon_y, '#64748b', 'الهلال', 16)]:
            xs = np.linspace(-4, 4, 10)
            ax.plot(x0 + xs / slope * 0 + xs * 0.5, y - xs * 0.5 * slope, color=c, lw=1, ls=':')
            ax.plot(x0, y, 'o', color=c, ms=ms); ax.text(x0 + 0.4, y + 0.3, lab, color=INK, fontsize=12)
        ax.set_xlim(-3, 6); ax.set_ylim(-9, 9)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=14)
    axs[0].annotate('', xy=(3.9, 6), xytext=(3.9, 0), arrowprops=dict(arrowstyle='<->', color=BLUE, lw=2))
    axs[0].text(4.1, 3, 'قوس الارتفاع', color=BLUE, fontsize=12)
    axs[1].annotate('', xy=(-1.3, 0), xytext=(-1.3, -6), arrowprops=dict(arrowstyle='<->', color=RED, lw=2))
    axs[1].text(-1.1, -3, 'قوس الرؤية\n(انحطاط الشمس)', color=RED, fontsize=12)
    fig.text(0.5, -0.04, 'قوس المكث = ما يدور من معدل النهار بين اللحظتين؛ كل جزء منه = 4 دقائق من الزمن.  '
             'مثال: مكث 12° = 48 دقيقة.', ha='center', fontsize=13)
    fig.suptitle('قوس المكث وقوس الارتفاع وقوس الرؤية (الأفق الغربي)', fontsize=16)
    save(fig, 'c18_lag.png')


def c19_phases():
    fig, ax = plt.subplots(figsize=(14, 4.6))
    els = [5, 7, 10, 13, 20, 30]
    for i, E in enumerate(els):
        cx = i * 2.3
        ax.add_patch(Circle((cx, 0), 0.85, color='#1f2937'))
        k = math.cos(math.radians(min(3 * E, 89)))
        kt = math.cos(math.radians(E))
        th = np.linspace(-np.pi / 2, np.pi / 2, 100)
        xo = 0.85 * np.cos(th); yo = 0.85 * np.sin(th)
        xi = 0.85 * k * np.cos(th)
        ax.fill(np.concatenate([cx + xo, cx + xi[::-1]]), np.concatenate([yo, yo[::-1]]), color='#fde68a')
        W = 15.5 * (1 - kt)
        ax.text(cx, -1.25, f'البعد {E}°', ha='center', fontsize=13)
        ax.text(cx, -1.65, f'عرض الهلال ≈ {W:.2f}′', ha='center', fontsize=11, color=GREY)
    ax.text(-1, 1.25, 'كلما زاد قوس النور (البعد بين النيرين) غلُظ الهلال وزاد ضوؤه؛ ودون نحو 7° لا يتكوّن هلال يُرى (حد دانجون).', fontsize=12)
    ax.set_xlim(-1.2, 12.8); ax.set_ylim(-1.9, 1.5); clean(ax)
    ax.set_title('قوس النور وسُمك الهلال (السُّمك في الرسم مُضخَّم للإيضاح، والأرقام حقيقية)', fontsize=15)
    save(fig, 'c19_phases.png')


def c20_day29():
    fig, ax = plt.subplots(figsize=(12, 5.5))
    conj = 29.15
    t = np.linspace(27.5, 30.8, 300)
    el = 12.19 * (t - conj)
    ax.plot(t, el, color=BLUE, lw=2.5, label='البعد بين النيرين (يزيد نحو 12° في اليوم)')
    ax.axhline(0, color=INK, lw=1)
    ax.axhline(4.5, color=RED, ls='--', lw=2); ax.text(27.55, 5.1, 'دل = 4;30°', color=RED, fontsize=13)
    for d, lab in [(29.0, 'زوال التاسع والعشرين'), (30.0, 'زوال الثلاثين')]:
        ax.axvline(d, color=GREY, ls=':')
        ax.plot(d, 12.19 * (d - conj), 'o', color=GOLD, ms=10)
        ax.text(d + 0.03, 12.19 * (d - conj) - (3.5 if d > 29.5 else 5.5), lab, fontsize=11, ha='left' if d > 29.5 else 'right')
    ax.axvline(conj, color=PURPLE, lw=1.5); ax.text(conj + 0.03, -9.5, 'الاقتران', color=PURPLE)
    ax.axvspan(29.27, 29.33, color=GREEN, alpha=0.3); ax.text(29.36, 10, 'الغروب', color=GREEN)
    ax.text(27.6, 15, 'هنا البعد عند زوال التاسع والعشرين سالب (الشمس متقدمة): «فذلك اليوم ليس هو تاسع عشرين الرؤية،\n'
            'فانتقل إلى الذي بعده». وفي زوال الثلاثين البعد ≈ 10° > دل، فالرؤية تلك الليلة ممكنة وتُفحص بالحدود.', fontsize=11.5)
    ax.set_xlabel('أيام الشهر'); ax.set_ylabel('البعد (درجة)')
    ax.set_ylim(-20, 22); ax.legend(loc='lower right'); ax.grid(alpha=0.3)
    ax.set_title('الشرط الأول في فصل الهلال: فضل ما بين مقومي النيرين وقت الزوال', fontsize=15)
    save(fig, 'c20_day29.png')


def c21_examples():
    sys.path.insert(0, HERE)
    from majdi import ts, sun, moon, earth, wgs84, sunset_time, CAIRO
    topos = wgs84.latlon(CAIRO['lat'], CAIRO['lon'])
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))
    for ax, day, title in [(axs[0], dt.date(2026, 3, 19), 'مساء الخميس 19 مارس 2026 (29 رمضان 1447)'),
                           (axs[1], dt.date(2026, 3, 20), 'مساء الجمعة 20 مارس 2026')]:
        ss = sunset_time(day, CAIRO)
        ax.axhspan(-12, 0, color='#e5e7eb'); ax.axhline(0, color=GREEN, lw=2)
        for k, mins in enumerate([0, 20, 40]):
            tt = ss + mins / 1440
            o = (earth + topos).at(tt)
            ma, mz, _ = o.observe(moon).apparent().altaz()
            sa, sz, _ = o.observe(sun).apparent().altaz()
            ax.plot(mz.degrees, ma.degrees, 'o', color='#64748b', ms=14 - 3 * k, alpha=1 - 0.25 * k)
            ax.plot(sz.degrees, sa.degrees, 'o', color='#f59e0b', ms=18 - 3 * k, alpha=1 - 0.25 * k)
            ax.text(mz.degrees + 0.5, ma.degrees + 0.6, f'الهلال +{mins}د', fontsize=10)
            ax.text(sz.degrees + 0.5, sa.degrees - 1.4, f'الشمس +{mins}د', fontsize=10)
        ax.set_xlim(255, 290); ax.set_ylim(-12, 24)
        ax.set_xlabel('السمت (درجة، 270 = المغرب)'); ax.set_ylabel('الارتفاع (درجة)')
        ax.grid(alpha=0.3); ax.set_title(title, fontsize=13)
    axs[0].text(256, 19, 'المكث 34 دقيقة، قوس الرؤية 7.7°، البعد 7.4°\nابن المجدي: «جائزة قريبة من الخفاء»', fontsize=11.5,
                bbox=dict(fc='#fef3c7', ec=GOLD))
    axs[1].text(256, 19, 'المكث 98 دقيقة، قوس الرؤية 21°، البعد 20.7°\nابن المجدي: «يُرى بيّنًا»', fontsize=11.5,
                bbox=dict(fc='#dcfce7', ec=GREEN))
    fig.suptitle('هلال شوال 1447 هـ في أفق القاهرة الغربي (مواضع حقيقية بعد الغروب بـ0 و20 و40 دقيقة)', fontsize=15)
    save(fig, 'c21_examples.png')


def c22_confusion():
    s = json.load(open(os.path.join(DATA, 'summary.json')))
    cm = s['confusion_odeh']
    rows = ['0', '1', '2', '3']; cols = ['A', 'B', 'C', 'D']
    M = np.array([[cm.get(r, {}).get(c, 0) for c in cols] for r in rows])
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.imshow(np.log1p(M), cmap='Blues')
    for i in range(4):
        for j in range(4):
            ax.text(j, i, str(M[i, j]), ha='center', va='center', fontsize=15,
                    color='white' if M[i, j] > 200 else INK)
    ax.set_xticks(range(4)); ax.set_xticklabels(['بالعين المجردة', 'قد تحتاج أداة', 'بالأداة فقط', 'غير ممكنة'])
    ax.set_yticks(range(4)); ax.set_yticklabels(['غير ممكنة', 'قريبة من الخفاء', 'قريبة إلى البيان', 'بيّن'])
    ax.set_xlabel('تصنيف معيار عودة (2004)'); ax.set_ylabel('حكم ابن المجدي')
    for (i, j) in [(0, 0), (3, 3), (3, 2), (0, 1)]:
        pass
    ax.set_title('مقارنة أحكام ابن المجدي بمعيار عودة: 2020 أمسية في القاهرة 1990–2049', fontsize=14)
    save(fig, 'c22_confusion.png')


def c23_runs():
    rows = list(csv.DictReader(open(os.path.join(DATA, 'hilal_cairo.csv'), encoding='utf-8')))
    by = {}
    for r in rows:
        by.setdefault(r['conj'], []).append(r)
    starts = []
    for k in sorted(by):
        rs = sorted(by[k], key=lambda r: int(r['night']))
        f = next((r for r in rs if int(r['majdi_code']) >= 1), None)
        if f:
            starts.append(dt.date.fromisoformat(f['date']))
    lens = [(b - a).days for a, b in zip(starts, starts[1:])]
    runs = {29: [], 30: []}
    c, prev = 0, None
    for x in lens + [0]:
        if x == prev:
            c += 1
        else:
            if prev in runs:
                runs[prev].append(c)
            c, prev = 1, x
    fig, axs = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={'width_ratios': [1, 1.4]})
    ax = axs[0]
    for v, col, off in [(29, PURPLE, -0.2), (30, GOLD, 0.2)]:
        vals = [runs[v].count(k) for k in range(1, 6)]
        ax.bar(np.arange(1, 6) + off, vals, 0.4, color=col, label=f'شهور {"ناقصة (29)" if v == 29 else "كاملة (30)"}')
    ax.axvline(3.5, color=PURPLE, ls='--'); ax.axvline(4.5, color=GOLD, ls='--')
    ax.set_xticks(range(1, 6)); ax.set_xlabel('عدد الشهور المتوالية'); ax.set_ylabel('عدد المرات')
    ax.legend(); ax.grid(axis='y', alpha=0.3)
    ax.set_title('أطوال التوالي في 60 سنة', fontsize=13)
    ax = axs[1]
    seg = lens[:72]
    for i, x in enumerate(seg):
        ax.add_patch(Rectangle((i % 24, -(i // 24)), 0.92, 0.85, color=PURPLE if x == 29 else GOLD))
        ax.text(i % 24 + 0.46, -(i // 24) + 0.42, str(x), ha='center', va='center', fontsize=8, color='white')
    ax.set_xlim(0, 24); ax.set_ylim(-2.2, 1)
    ax.axis('off')
    ax.set_title('أطوال الشهور الأولى (من 1990) بمعيار ابن المجدي — كل صف سنتان', fontsize=13)
    fig.suptitle('«لا يجوز أن تتوالى أكثر من ثلاثة شهور نواقص، ولا أكثر من أربعة كوامل»', fontsize=15, y=1.03)
    save(fig, 'c23_runs.png')


def c24_variables_map():
    """خريطة المتغيرات: من المعطيات إلى الحكم"""
    fig, ax = plt.subplots(figsize=(14, 7.5))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7.5); ax.axis('off')

    def box(x, y, t, fc, ec, w=2.6, h=0.9, fs=12):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.05', fc=fc, ec=ec, lw=1.4))
        ax.text(x, y, t, ha='center', va='center', fontsize=fs)
    box(12.3, 6.5, 'مقوما النيرين\nوقت الزوال', '#e0e7ff', BLUE); box(12.3, 5.0, 'البهتان', '#e0e7ff', BLUE)
    box(12.3, 3.5, 'عرض البلد φ', '#e0e7ff', BLUE); box(12.3, 2.0, 'مقوم الجوزهر', '#e0e7ff', BLUE)
    box(8.6, 6.5, 'فضل المقومين\n(الشرط: > دل)', '#fef3c7', GOLD); box(8.6, 5.0, 'مقوما النيرين\nعند الرؤية', '#fef3c7', GOLD)
    box(8.6, 3.5, 'الدرجة المرئية\nوالعرض المرئي', '#fef3c7', GOLD); box(8.6, 2.0, 'عرض القمر β', '#fef3c7', GOLD)
    box(4.9, 6.6, 'قوس المكث', '#dcfce7', GREEN, w=2.3); box(4.9, 5.35, 'قوس الرؤية', '#dcfce7', GREEN, w=2.3)
    box(4.9, 4.1, 'قوس الارتفاع', '#dcfce7', GREEN, w=2.3); box(4.9, 2.85, 'البعد المطلق', '#dcfce7', GREEN, w=2.3)
    box(4.9, 1.6, 'قوس النور', '#dcfce7', GREEN, w=2.3)
    box(1.4, 4.1, 'الحكم\nبالأقوال الثلاثة', '#fee2e2', RED, w=2.2, h=1.4, fs=13)
    for a, b in [((11.0, 6.5), (9.9, 6.5)), ((11.0, 5.0), (9.9, 5.0)), ((11.0, 6.3), (9.9, 5.2)),
                 ((11.0, 2.0), (9.9, 2.0)), ((8.6, 4.55), (8.6, 3.95)), ((8.6, 2.45), (8.6, 3.05)),
                 ((7.3, 3.5), (6.05, 6.5)), ((7.3, 3.5), (6.05, 5.35)), ((7.3, 3.5), (6.05, 4.1)),
                 ((7.3, 3.5), (6.05, 2.85)), ((7.3, 3.5), (6.05, 1.6)), ((11.0, 3.5), (9.9, 3.5))]:
        arrow(ax, a, b, c=GREY)
    for y in (6.6, 5.35, 4.1, 2.85, 1.6):
        arrow(ax, (3.75, y), (2.5, 4.1), c=RED)
    ax.text(12.3, 7.3, 'المعطيات', ha='center', fontsize=14, color=BLUE)
    ax.text(8.6, 7.3, 'الخطوات الوسيطة', ha='center', fontsize=14, color=GOLD)
    ax.text(4.9, 7.3, 'المتغيرات الخمسة', ha='center', fontsize=14, color=GREEN)
    ax.set_title('خريطة المتغيرات في فصل رؤية الهلال', fontsize=16)
    save(fig, 'c24_variables_map.png')


if __name__ == '__main__':
    for f in [c01_timeline, c02_teachers, c03_sphere, c04_ecliptic, c05_quadrant_ops, c06_shadow, c07_ghaya,
              c08_day_arcs, c09_analemma, c10_asr, c11_twilight, c12_qibla, c13_eastwest, c14_ascensions,
              c15_moon_orbit, c16_baht, c17_parallax, c18_lag, c19_phases, c20_day29, c21_examples,
              c22_confusion, c23_runs, c24_variables_map]:
        f()
