# -*- coding: utf-8 -*-
"""
اختبار معيار ابن المجدي على أهلّة القاهرة 1990–2049 ومقارنته بمعياري يالوب وعودة،
وتعيين المتغيرات الواردة في الرسالة (دل، اختلاف المنظر، المكث في الليلتين الثانية والثالثة،
وتوالي الشهور النواقص والكوامل).
الناتج: data/hilal_cairo.csv و data/summary.json
"""
import sys, os, json, csv, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(__file__))
from majdi import *

OUT = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(OUT, exist_ok=True)
LOC = CAIRO
topos = wgs84.latlon(LOC['lat'], LOC['lon'])


def local_date(t):
    return (t.utc_datetime() + dt.timedelta(hours=LOC['tz'])).date()


rows = []
for nm in new_moons(1990, 2050):
    d0 = local_date(nm)
    for k in range(0, 3):
        day = d0 + dt.timedelta(days=k)
        m = modern_hilal(day, LOC)
        if m is None or m['moonset'] is None:
            continue
        age_h = (m['sunset'] - nm) * 24
        if age_h < 0:
            continue
        v = majdi_hilal(day, LOC)
        code, desc = majdi_verdict(v)
        # اختلاف المنظر الحقيقي في الطول والعرض عند الغروب (سطحي − مركزي)
        lg, bg, _ = ecl_lonlat(moon, m['sunset'])
        lt, bt, _ = ecl_lonlat(moon, m['sunset'], topos)
        rows.append(dict(
            conj=nm.utc_strftime('%Y-%m-%d %H:%M'), date=day.isoformat(), night=k, age_h=round(age_h, 2),
            elong_noon=round(float(v['elong_noon']), 3), lag_majdi=round(v['lag'], 3),
            lag_min_majdi=round(v['lag_min'], 1), arcv_majdi=round(v['arcv'], 3), alt_majdi=round(v['alt'], 3),
            elong_majdi=round(float(v['elong']), 3), nur_majdi=round(v['nur'], 3), S=round(float(v['S']), 3),
            beta_majdi=round(v['beta'], 3), beta_true=round(float(v['beta_true_noon']), 3),
            lam_moon=round(float(v['lam_moon']), 3), p_lon_majdi=round(v['p_lon'], 2), p_lat_majdi=round(v['p_lat'], 2),
            p_lon_true=round(float(norm180(lg - lt)) * 60, 2), p_lat_true=round(float(bg - bt) * 60, 2),
            majdi_code=code, majdi_desc=desc, majdi_q2=int(majdi_second_opinion(v)),
            lag_min=round(m['lag_min'], 1), arcl=round(m['arcl'], 3), arcv_geo=round(m['arcv_geo'], 3),
            arcv_topo=round(m['arcv_topo'], 3), daz=round(m['daz'], 3), W=round(m['W'], 3),
            q=round(m['q'], 3), yallop=yallop_zone(m['q']), V=round(m['V'], 3), odeh=odeh_zone(m['V'])))
    if len(rows) % 150 < 3:
        print(len(rows), rows[-1]['date'], flush=True)

with open(os.path.join(OUT, 'hilal_cairo.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print('rows', len(rows))
