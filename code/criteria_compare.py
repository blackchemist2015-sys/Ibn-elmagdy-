# -*- coding: utf-8 -*-
"""مقارنة معيار ابن المجدي بالمعايير القديمة والحديثة، وبدرجات الإمكان (العين المجردة/المنظار/التلسكوب)،
على أمسيات القاهرة في data/hilal_cairo.csv (2020 أمسية)."""
import sys, json, math, datetime as dt
import pandas as pd, numpy as np
import astronomy as A
LAT, LON = 30.0444, 31.2357
d = pd.read_csv('data/hilal_cairo.csv')
obs = A.Observer(LAT, LON, 0)

def at_sunset(date):
    y, m, dd = map(int, date.split('-'))
    t0 = A.Time.Make(y, m, dd, 12 - LON / 15, 0, 0)
    ss = A.SearchRiseSet(A.Body.Sun, obs, A.Direction.Set, t0, 1)
    eq = A.Equator(A.Body.Moon, ss, obs, True, True)
    alt = A.Horizon(ss, obs, eq.ra, eq.dec, A.Refraction.Airless).altitude
    el = A.AngleFromSun(A.Body.Moon, ss)            # استطالة مركزية
    return alt, el

alts, els = zip(*[at_sunset(x) for x in d.date])
d['alt_ss'] = alts; d['elong_geo_ss'] = els
D = d.daz.abs()
crit = {
    'البابلي (العمر ≥ 24 ساعة والمكث ≥ 48 دقيقة)': (d.age_h >= 24) & (d.lag_min >= 48),
    'حدّ دانجون (البعد ≥ 7°)': d.arcl >= 7,
    'فوذرنغهام 1910': d.arcv_geo >= 12.0 - 0.008 * D ** 2,
    'ماوندر 1911': d.arcv_geo >= 11.0 - 0.05 * D - 0.01 * D ** 2,
    'الهندي (شوخ، بصيغة يالوب)': d.arcv_geo >= 10.3743 - 0.0137 * D - 0.0097 * D ** 2,
    'إلياس (البعد ≥ 10.5°)': d.arcl >= 10.5,
    'إسطنبول 1978 (الارتفاع ≥ 5° والبعد ≥ 8°)': (d.alt_ss >= 5) & (d.elong_geo_ss >= 8),
    'مابيمس الجديد 2021 (الارتفاع ≥ 3° والبعد ≥ 6.4°)': (d.alt_ss >= 3) & (d.elong_geo_ss >= 6.4),
    'شرط أم القرى (اجتماع قبل الغروب ومكث موجب)': (d.age_h > 0) & (d.lag_min > 0),
    'يالوب 1997: يُرى بالعين (A–B)': d.yallop.isin(['A', 'B']),
    'يالوب 1997: يُرى ولو بالأجهزة (A–D)': d.yallop.isin(['A', 'B', 'C', 'D']),
    'عودة 2004: يُرى بالعين (A)': d.odeh == 'A',
    'عودة 2004: يُرى ولو بالأجهزة (A–C)': d.odeh.isin(['A', 'B', 'C']),
}
mj = d.majdi_code
majdi = {'ابن المجدي ≥ جائزة قريبة من الخفاء': mj >= 1, 'ابن المجدي ≥ جائزة قريبة من البيان': mj >= 2, 'ابن المجدي = بيّن': mj == 3}
# درجات الإمكان المرجعية (عودة)
ref = {'بالعين المجردة': d.odeh == 'A', 'بالمنظار أو بالعين في صفاء الجو': d.odeh.isin(['A', 'B']),
       'بالتلسكوب (أي جهاز بصري)': d.odeh.isin(['A', 'B', 'C'])}
def agree(a, b):
    a, b = np.asarray(a), np.asarray(b)
    tp = int((a & b).sum()); tn = int((~a & ~b).sum()); fp = int((a & ~b).sum()); fn = int((~a & b).sum())
    return dict(agree=round((tp + tn) / len(a) * 100, 1), tp=tp, tn=tn, fp=fp, fn=fn)
out = {'n': len(d)}
# 1) ابن المجدي مقابل درجات الإمكان
out['majdi_vs_ref'] = {m: {r: agree(majdi[m], ref[r]) for r in ref} for m in majdi}
# 2) جدول التوزيع: درجة ابن المجدي × درجة الإمكان
cls = np.select([d.odeh == 'A', d.odeh == 'B', d.odeh == 'C'], ['عين', 'منظار', 'تلسكوب'], 'غير ممكنة')
out['confusion'] = pd.crosstab(mj, cls).to_dict()
# 3) كل معيار: موافقته لابن المجدي ولدرجات الإمكان
out['criteria'] = {}
for k, v in {**majdi, **crit}.items():
    out['criteria'][k] = dict(share_visible=round(v.mean() * 100, 1),
                             vs_majdi1=agree(v, majdi['ابن المجدي ≥ جائزة قريبة من الخفاء'])['agree'],
                             vs_majdi2=agree(v, majdi['ابن المجدي ≥ جائزة قريبة من البيان'])['agree'],
                             **{('vs_' + r): agree(v, ref[r])['agree'] for r in ref})
json.dump(out, open('data/criteria_compare.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
