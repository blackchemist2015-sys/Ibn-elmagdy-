# -*- coding: utf-8 -*-
"""إحصاءات اختبار معيار ابن المجدي — تُكتب في data/summary.json"""
import os, csv, json
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
rows = list(csv.DictReader(open(os.path.join(DATA, 'hilal_cairo.csv'), encoding='utf-8')))
for r in rows:
    for k, v in r.items():
        try:
            r[k] = float(v)
        except ValueError:
            pass

out = {'n_evenings': len(rows)}

# 1) مصفوفة التوافق: حكم ابن المجدي × نطاقات عودة ويالوب
conf = defaultdict(Counter)
confy = defaultdict(Counter)
for r in rows:
    conf[int(r['majdi_code'])][r['odeh']] += 1
    confy[int(r['majdi_code'])][r['yallop']] += 1
out['confusion_odeh'] = {k: dict(v) for k, v in sorted(conf.items())}
out['confusion_yallop'] = {k: dict(v) for k, v in sorted(confy.items())}

# نسبة الاتفاق الثنائي: (ابن المجدي ≥ 1) مقابل (عودة A أو B: بالعين)
def agree(pred, truth):
    tp = sum(1 for p, t in zip(pred, truth) if p and t)
    tn = sum(1 for p, t in zip(pred, truth) if not p and not t)
    fp = sum(1 for p, t in zip(pred, truth) if p and not t)
    fn = sum(1 for p, t in zip(pred, truth) if not p and t)
    return dict(tp=tp, tn=tn, fp=fp, fn=fn, accuracy=round((tp + tn) / len(pred), 4))

naked = [r['odeh'] in ('A', 'B') for r in rows]
out['binary_majdi_ge1_vs_odeh_AB'] = agree([r['majdi_code'] >= 1 for r in rows], naked)
out['binary_majdi_ge2_vs_odeh_AB'] = agree([r['majdi_code'] >= 2 for r in rows], naked)
out['binary_majdi_eq3_vs_odeh_A'] = agree([r['majdi_code'] == 3 for r in rows], [r['odeh'] == 'A' for r in rows])
out['binary_q2_vs_odeh_AB'] = agree([r['majdi_q2'] == 1 for r in rows], naked)

# 2) معايرة العتبات: أفضل حدّ لـ S، ولـ «دل»
def best_threshold(key, truth, grid):
    best = None
    for g in grid:
        a = agree([r[key] >= g for r in rows], truth)['accuracy']
        if best is None or a > best[1]:
            best = (round(float(g), 2), a)
    return best

out['best_S_for_odeh_AB'] = best_threshold('S', naked, np.arange(5, 14, 0.1))
out['best_S_for_odeh_A'] = best_threshold('S', [r['odeh'] == 'A' for r in rows], np.arange(5, 16, 0.1))
out['best_S_for_any_optical'] = best_threshold('S', [r['odeh'] != 'D' for r in rows], np.arange(3, 12, 0.1))
out['best_noon_for_odeh_AB'] = best_threshold('elong_noon', naked, np.arange(0, 14, 0.1))
out['best_noon_for_any_optical'] = best_threshold('elong_noon', [r['odeh'] != 'D' for r in rows], np.arange(0, 14, 0.1))
vis = [r['elong_noon'] for r in rows if r['odeh'] in ('A', 'B')]
inv = [r['elong_noon'] for r in rows if r['odeh'] == 'D']
out['noon_elong_min_naked_eye'] = round(min(vis), 2)
out['noon_elong_max_invisible'] = round(max(inv), 2)
out['noon_elong_le_4_5_and_visible'] = sum(1 for r in rows if r['elong_noon'] <= 4.5 and r['odeh'] in ('A', 'B'))
out['noon_elong_le_4_5_total'] = sum(1 for r in rows if r['elong_noon'] <= 4.5)
for alt in (10, 12):
    out[f'noon_elong_le_{alt}_and_naked_eye'] = sum(1 for r in rows if r['elong_noon'] <= alt and r['odeh'] in ('A', 'B'))

# 3) دقة الأدوات التقريبية في الرسالة
lag_err = [r['lag_min_majdi'] - r['lag_min'] for r in rows if r['lag_min'] == r['lag_min'] and r['lag_min'] > 0]
out['lag_error_minutes'] = dict(mean=round(float(np.mean(lag_err)), 2), std=round(float(np.std(lag_err)), 2))
arcv_err = [r['arcv_majdi'] - r['arcv_topo'] for r in rows if r['arcv_topo'] > 0]
out['arcv_error_vs_topocentric'] = dict(mean=round(float(np.mean(arcv_err)), 2), std=round(float(np.std(arcv_err)), 2))
el_err = [r['elong_majdi'] - r['arcl'] for r in rows if r['arcl'] > 0]
out['elong_minus_arcl'] = dict(mean=round(float(np.mean(el_err)), 2), std=round(float(np.std(el_err)), 2))
pl = [r['p_lon_majdi'] - r['p_lon_true'] for r in rows if 0 < r['alt_majdi'] < 25]
pb = [r['p_lat_majdi'] - r['p_lat_true'] for r in rows if 0 < r['alt_majdi'] < 25]
out['parallax_lon_error_arcmin'] = dict(mean=round(float(np.mean(pl)), 2), std=round(float(np.std(pl)), 2))
out['parallax_lat_error_arcmin'] = dict(mean=round(float(np.mean(pb)), 2), std=round(float(np.std(pb)), 2))
be = [r['beta_majdi'] - r['beta_true'] for r in rows]
out['latitude_error_deg'] = dict(mean=round(float(np.mean(be)), 3), std=round(float(np.std(be)), 3))

# 4) التقويم المبني على الرؤية: أطول توالٍ للنواقص والكوامل
by = defaultdict(list)
for r in rows:
    by[r['conj']].append(r)
def calendar(test):
    starts = []
    for k in sorted(by):
        rs = sorted(by[k], key=lambda r: r['night'])
        for r in rs:
            if test(r):
                starts.append(r['date'])
                break
    import datetime as dt
    ds = [dt.date.fromisoformat(s) for s in starts]
    lens = [(b - a).days for a, b in zip(ds, ds[1:])]
    def maxrun(v):
        m = c = 0
        for x in lens:
            c = c + 1 if x == v else 0
            m = max(m, c)
        return m
    return dict(months=len(lens), lengths=dict(Counter(lens)), max_run_29=maxrun(29), max_run_30=maxrun(30))

out['calendar_odeh_AB'] = calendar(lambda r: r['odeh'] in ('A', 'B'))
out['calendar_majdi_ge1'] = calendar(lambda r: r['majdi_code'] >= 1)
out['calendar_majdi_ge2'] = calendar(lambda r: r['majdi_code'] >= 2)

# 5) المكث في الليلتين الثانية والثالثة بعد أول رؤية (عودة A/B)
n2, n3 = [], []
for k in sorted(by):
    rs = sorted(by[k], key=lambda r: r['night'])
    idx = [i for i, r in enumerate(rs) if r['odeh'] in ('A', 'B')]
    if idx:
        i = idx[0]
        if i + 1 < len(rs): n2.append(rs[i + 1]['lag_min'] / 60)
        if i + 2 < len(rs): n3.append(rs[i + 2]['lag_min'] / 60)
out['night2_lag_hours'] = dict(n=len(n2), min=round(min(n2), 2), max=round(max(n2), 2),
                              share_le_1h=round(sum(x <= 1 for x in n2) / len(n2), 3),
                              share_gt_2h=round(sum(x > 2 for x in n2) / len(n2), 3))
out['night3_lag_hours'] = dict(n=len(n3), min=round(min(n3), 2), max=round(max(n3), 2),
                              share_le_1_5h=round(sum(x <= 1.5 for x in n3) / len(n3), 3),
                              share_gt_3h=round(sum(x > 3 for x in n3) / len(n3), 3))

# 6) أمثلة محلولة
out['examples'] = [r for r in rows if r['date'] in ('2025-03-29', '2025-03-30', '2026-02-17', '2026-02-18', '2026-03-19', '2026-03-20')]

json.dump(out, open(os.path.join(DATA, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'examples'}, ensure_ascii=False, indent=1))
