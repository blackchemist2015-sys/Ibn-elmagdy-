# -*- coding: utf-8 -*-
"""التحقق من قول ابن المجدي: «يجوز أن يغرب الليلة الثانية من رؤيته والماضي لا يزيد على ساعة، كما يجوز
أن يغرب تلك الليلة والماضي أكثر من ساعتين، ويجوز غروبه ثالث ليلة والماضي لا يزيد على ساعة ونصف،
كما يجوز غروبه في تلك الليلة على ثلاث ساعات» — بأول رؤية بمعيار ابن المجدي (حكم ≥ 1) وبمعيار عودة (A/B)."""
import os, sys, csv, json, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(__file__))
from majdi import *

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
rows = list(csv.DictReader(open(os.path.join(DATA, 'hilal_cairo.csv'), encoding='utf-8')))
by = {}
for r in rows:
    by.setdefault(r['conj'], []).append(r)

def lag_hours(day):
    ss = sunset_time(day, CAIRO)
    ms = moonset_time(ss, CAIRO)
    return (ms - ss) * 24

res = {}
for name, test in [('majdi', lambda r: int(r['majdi_code']) >= 1), ('odeh', lambda r: r['odeh'] in ('A', 'B'))]:
    n2, n3 = [], []
    for k in sorted(by):
        rs = sorted(by[k], key=lambda r: int(r['night']))
        first = next((r for r in rs if test(r)), None)
        if first is None:
            continue
        d = dt.date.fromisoformat(first['date'])
        n2.append(lag_hours(d + dt.timedelta(days=1)))
        n3.append(lag_hours(d + dt.timedelta(days=2)))
    res[name] = dict(n=len(n2),
                     night2=dict(min=round(min(n2), 2), max=round(max(n2), 2),
                                 share_le_1h=round(sum(x <= 1 for x in n2) / len(n2), 3),
                                 share_gt_2h=round(sum(x > 2 for x in n2) / len(n2), 3)),
                     night3=dict(min=round(min(n3), 2), max=round(max(n3), 2),
                                 share_le_1_5h=round(sum(x <= 1.5 for x in n3) / len(n3), 3),
                                 share_gt_3h=round(sum(x > 3 for x in n3) / len(n3), 3)),
                     n2=[round(x, 3) for x in n2], n3=[round(x, 3) for x in n3])
json.dump(res, open(os.path.join(DATA, 'lag_nights.json'), 'w'), indent=0)
for k, v in res.items():
    print(k, v['n'], v['night2'], v['night3'])
