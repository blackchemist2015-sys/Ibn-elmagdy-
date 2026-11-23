# -*- coding: utf-8 -*-
"""هلالا رمضان وشوال في القاهرة 1416–1446 هـ (1995–2025 م): درجة ابن المجدي مقابل معيار عودة، مساء أول غروب بعد الاجتماع."""
import sys, datetime as dt, json
sys.path.insert(0, 'ifta')
import astronomy as A
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')
from hijri_converter import Gregorian
from majdi_engine import majdi, modern
plt.rcParams['font.family'] = ['Amiri', 'DejaVu Sans']
LAT, LON = 30.0444, 31.2357
rows = []
t = A.Time.Make(1995, 1, 1, 0, 0, 0)
while True:
    nm = A.SearchMoonPhase(0, t, 40)
    if nm.Utc().year > 2025: break
    u = nm.Utc(); t = nm.AddDays(20)
    h = Gregorian(u.year, u.month, u.day).to_hijri()
    # الشهر الذي يبدأ بعد هذا الاجتماع
    mon = h.month % 12 + 1 if h.day > 15 else h.month
    hy = h.year + (1 if (h.day > 15 and h.month == 12) else 0)
    if mon not in (9, 10): continue
    day = (u + dt.timedelta(hours=2)).date()
    md = modern(day, LAT, LON)
    if md.get('moon_age_h', float('nan')) != md.get('moon_age_h') or md['moon_age_h'] < 0:
        day += dt.timedelta(days=1)
    v = majdi(day, LAT, LON); m = modern(day, LAT, LON)
    rows.append(dict(date=str(day), month=mon, year=hy, gyear=u.year, S=v.get('S'), grade=str(v['grade']),
                     elong_noon=v['elong_noon'], V=m['odeh_V'], zone=m['odeh_zone'], age=m['moon_age_h']))
json.dump(rows, open('data/years_cairo.json', 'w'), ensure_ascii=False, indent=1)
gc = {'pre': '#8B1E2D', '0': '#D1495B', '1': '#E9A23B', '2': '#7FB069', '3': '#2F7F79'}
gn = {'pre': 'قبل الاجتماع وقت الزوال', '0': 'غير ممكنة', '1': 'جائزة قريبة من الخفاء', '2': 'جائزة', '3': 'بيّنة'}
zm = {'A': 'o', 'B': 's', 'C': 'D', 'D': 'x'}
fig, axes = plt.subplots(2, 1, figsize=(13, 8.5), sharex=True)
for ax, mon, title in [(axes[0], 9, 'هلال رمضان'), (axes[1], 10, 'هلال شوال')]:
    rr = [r for r in rows if r['month'] == mon]
    for r in rr:
        y = r['S'] if r['S'] is not None else 0
        if r['grade'] == 'pre': y = 0
        ax.bar(r['year'], max(y, 0.4), color=gc[r['grade']], width=0.75)
        ax.text(r['year'], max(y, 0.4) + 0.4, r['zone'], ha='center', fontsize=9, color='#14213D')
    for th, lb in [(7, '7'), (10, '10'), (13, '13')]:
        ax.axhline(th, color='#555', lw=0.8, ls='--')
    ax.set_title(title + ' — القاهرة، مساء أول غروب بعد الاجتماع', fontsize=15)
    ax.set_ylabel('مقدار ابن المجدي S = ½(قوس الرؤية + البعد)', fontsize=11)
    ax.set_ylim(0, 24); ax.set_xlabel('السنة الهجرية', fontsize=11); ax.grid(axis='y', alpha=.2)
from matplotlib.patches import Patch
h = [Patch(color=gc[k], label=gn[k]) for k in gc]
fig.legend(handles=h, loc='lower center', ncol=5, fontsize=11, frameon=False)
fig.text(0.5, 0.055, 'الحرف فوق كل عمود: نطاق معيار عودة (A بالعين، B بالعين في صفاء، C بالمنظار فقط، D غير ممكنة)', ha='center', fontsize=11)
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig('figures/y01_years_cairo.png', dpi=150)
import collections
agree = collections.Counter((r['grade'], r['zone']) for r in rows)
print(len(rows), agree)
