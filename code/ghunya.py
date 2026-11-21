# -*- coding: utf-8 -*-
"""
فصل «في حساب رؤية الأهلة» من «غنية الفهيم والطريق إلى حل التقويم» لابن المجدي:
اختبار قواعده على أمسيات القاهرة 1990–2049 نفسها.

- «البعد بالمغارب» = فضل مطالع نظير جزء القمر على مطالع نظير جزء الشمس (المكث دون العرض).
- يُعدَّل بثلثي العرض (رأي الطوسي) أو بنصفه (رأي «بعضهم») فيحصل قوس المكث.
- حدود كوشيار: النور 10، الرؤية 8، المكث 12؛ «فإن شهد من هذه اثنان فاحكم بالرؤية».
- حدود ابن يونس: النور 10، الارتفاع 6½ (وقيل 6)، المكث 8.
- «بعضهم»: البعد بالمغارب المعدّل بنصف العرض ≥ 12 إن كان العرض جنوبيًّا، و≥ 10 إن كان شماليًّا.
- لا فائدة في التحرير إذا كان بين النيرين وقت الزوال نحو درجتين فأقل أو عشرة فأكثر.
الناتج: data/ghunya.csv و data/ghunya_summary.json
"""
import os, sys, csv, json, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(__file__))
from majdi import majdi_hilal, CAIRO, azimuth
import numpy as np

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
rows = list(csv.DictReader(open(os.path.join(DATA, 'hilal_cairo.csv'), encoding='utf-8')))
out = []
for r in rows:
    v = majdi_hilal(dt.date.fromisoformat(r['date']), CAIRO)
    out.append(dict(date=r['date'], conj=r['conj'], night=int(r['night']), odeh=r['odeh'], yallop=r['yallop'],
                    elong_noon=float(v['elong_noon']), beta_vis=v['beta_vis'], lag=v['lag'],
                    lag_maghrib=v['lag_approx'], arcv=v['arcv'], alt=v['alt'], nur=v['nur'],
                    lag_modern_deg=float(r['lag_min']) / 4, majdi_code=int(r['majdi_code']),
                    dec_moon=v['dec_moon'], dec_sun=v['dec_sun'], lam_sun=float(v['lam_sun'])))
with open(os.path.join(DATA, 'ghunya.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

S = {}
# 1) معامل تعديل البعد بالمغارب بالعرض: (المكث − البعد بالمغارب) ÷ العرض المرئي
b = np.array([o['beta_vis'] for o in out]); d = np.array([o['lag'] - o['lag_maghrib'] for o in out])
dm = np.array([o['lag_modern_deg'] - o['lag_maghrib'] for o in out])
m = np.abs(b) > 0.5
S['k_exact_fit'] = round(float(np.sum(d[m] * b[m]) / np.sum(b[m] ** 2)), 3)
S['k_modern_fit'] = round(float(np.sum(dm[m] * b[m]) / np.sum(b[m] ** 2)), 3)
for k in (2 / 3, 1 / 2):
    S[f'rms_err_deg_k{k:.3f}'] = round(float(np.sqrt(np.mean((d - k * b) ** 2))), 3)
S['rms_err_deg_no_latitude'] = round(float(np.sqrt(np.mean(d ** 2))), 3)
# المعامل بحسب الفصل (طول الشمس)
lam = np.array([o['lam_sun'] for o in out]) % 360
S['k_by_season'] = {}
for name, lo, hi in [('حول الاعتدال الربيعي', 330, 30), ('حول الانقلاب الصيفي', 60, 120),
                     ('حول الاعتدال الخريفي', 150, 210), ('حول الانقلاب الشتوي', 240, 300)]:
    sel = ((lam >= lo) | (lam < hi)) if lo > hi else ((lam >= lo) & (lam < hi))
    sel &= m
    S['k_by_season'][name] = round(float(np.sum(d[sel] * b[sel]) / np.sum(b[sel] ** 2)), 3)

# 2) المعايير ومقارنتها بعودة (الرؤية بالعين = A أو B)
naked = np.array([o['odeh'] in ('A', 'B') for o in out])
def score(pred):
    pred = np.array(pred)
    return dict(visible=int(pred.sum()), agree=round(float(np.mean(pred == naked)), 4),
                false_pos=int(np.sum(pred & ~naked)), false_neg=int(np.sum(~pred & naked)))
def two_of_three(o):
    return (o['nur'] >= 10) + (o['arcv'] >= 8) + (o['lag'] >= 12) >= 2
crit = {
    'كوشيار (اثنان من ثلاثة: النور 10، الرؤية 8، المكث 12)': [two_of_three(o) and o['lag'] > 0 for o in out],
    'كوشيار (الثلاثة كلها)': [o['nur'] >= 10 and o['arcv'] >= 8 and o['lag'] >= 12 for o in out],
    'ابن يونس (النور 10، الارتفاع 6½، المكث 8)': [o['nur'] >= 10 and o['alt'] >= 6.5 and o['lag'] >= 8 for o in out],
    'ابن يونس برواية «ستة فقط»': [o['nur'] >= 10 and o['alt'] >= 6 and o['lag'] >= 8 for o in out],
    '«بعضهم» (البعد بالمغارب بنصف العرض: 12 جنوبي، 10 شمالي)':
        [(o['lag_maghrib'] + 0.5 * o['beta_vis']) >= (12 if o['beta_vis'] < 0 else 10) for o in out],
    'الخلاصة: القول الأول (12، 12، 10)': [o['lag'] >= 12 and o['arcv'] >= 12 and o['alt'] >= 10 for o in out],
    'الخلاصة: المعيار المركّب (قريبة إلى البيان فما فوق)': [o['majdi_code'] >= 2 for o in out],
}
S['criteria_vs_odeh_naked_eye'] = {k: score(v) for k, v in crit.items()}

# 3) قاعدة «لا فائدة في التحرير»: نحو درجتين فأقل أو عشرة فأكثر وقت الزوال
en = np.array([o['elong_noon'] for o in out])
S['noon_le_2'] = dict(n=int(np.sum(en <= 2)), naked_eye=int(np.sum((en <= 2) & naked)))
S['noon_ge_10'] = dict(n=int(np.sum(en >= 10)), naked_eye=int(np.sum((en >= 10) & naked)),
                       odeh_A=int(np.sum((en >= 10) & np.array([o['odeh'] == 'A' for o in out]))))
S['noon_between'] = int(np.sum((en > 2) & (en < 10)))

# 4) جهة غروب الهلال من مغرب الشمس (أول ليلة يُرى فيها بالعين عند عودة)
first = {}
for o in out:
    if o['odeh'] in ('A', 'B') and o['conj'] not in first:
        first[o['conj']] = o
phi = CAIRO['lat']
south = 0
recs = []
for o in first.values():
    amp_m = np.degrees(np.arcsin(np.sin(np.radians(o['dec_moon'])) / np.cos(np.radians(phi))))
    amp_s = np.degrees(np.arcsin(np.sin(np.radians(o['dec_sun'])) / np.cos(np.radians(phi))))
    recs.append((o['lam_sun'] % 360, amp_m - amp_s, o['beta_vis']))
    south += amp_m < amp_s
S['first_crescent_sets_south_of_sun'] = dict(n=len(first), south=int(south), share=round(south / len(first), 3))
json.dump(recs, open(os.path.join(DATA, 'ghunya_setting_sides.json'), 'w'))
json.dump(S, open(os.path.join(DATA, 'ghunya_summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
