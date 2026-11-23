# -*- coding: utf-8 -*-
"""
محرك حساب معيار ابن المجدي لأي تاريخ وأي موضع (مكتبة Astronomy Engine، صالحة لقرون).
- majdi(day, lat, lon): متغيرات «خلاصة الأقوال» مساء اليوم المدني المعطى، بخطوات الرسالة.
- modern(day, lat, lon): الغروبان والمكث الحديث وتصنيف معيار عودة (2004) للمقارنة.
لا يؤخذ من الحساب الحديث في majdi إلا مقوّما النيّرين وقت الزوال (كما كان يؤخذان من التقويم).
"""
import math, datetime as dt
import astronomy as A

D2R = math.pi / 180
EPS = 23 + 35 / 60            # الميل الأعظم عند ابن المجدي
DAL = 4.5                     # «دل» = 4;30
sind = lambda x: math.sin(x * D2R); cosd = lambda x: math.cos(x * D2R); tand = lambda x: math.tan(x * D2R)
asind = lambda x: math.asin(max(-1, min(1, x))) / D2R
acosd = lambda x: math.acos(max(-1, min(1, x))) / D2R
atan2d = lambda y, x: math.atan2(y, x) / D2R
n360 = lambda x: x % 360
n180 = lambda x: (x + 180) % 360 - 180


def _t(d: dt.datetime):
    return A.Time.Make(d.year, d.month, d.day, d.hour, d.minute, d.second + d.microsecond / 1e6)


def noon_utc(day: dt.date, lon: float) -> dt.datetime:
    return dt.datetime(day.year, day.month, day.day, 12) - dt.timedelta(hours=lon / 15)


def decl(l): return asind(sind(EPS) * sind(l))
def ra(l): return n360(atan2d(cosd(EPS) * sind(l), cosd(l)))
def half_arc(phi, d):
    x = tand(phi) * tand(d)
    return None if abs(x) > 1 else 90 + asind(x)


def parallax(lam, phi):
    """جدول الرسالة (51′…30′ طولًا، 6′…41′ عرضًا)، معكوسًا في نصف الكرة الجنوبي"""
    d = abs(n180(lam))
    if phi < 0:
        d = 180 - d
    plon, plat = 51 - 21 * d / 180, 6 + 35 * d / 180
    return plon, (-plat if phi < 0 else plat)


def mean_node(t: A.Time):
    T = t.tt / 36525
    return n360(125.0445479 - 1934.1362891 * T)


def majdi(day: dt.date, lat: float, lon: float) -> dict:
    t1 = noon_utc(day, lon); t2 = t1 + dt.timedelta(days=1)
    T1, T2 = _t(t1), _t(t2)
    ls1, lm1 = A.SunPosition(T1).elon, A.EclipticGeoMoon(T1).lon
    ls2, lm2 = A.SunPosition(T2).elon, A.EclipticGeoMoon(T2).lon
    bs, bm = n360(ls2 - ls1), n360(lm2 - lm1)
    v = dict(elong_noon=n180(lm1 - ls1), baht_moon=bm, baht_sun=bs)
    hd = half_arc(lat, decl(ls1))
    if hd is None:
        v['grade'] = 'none'; return v
    hissa = (hd + 10) / 6
    ls, lm = ls1 + bs * hissa / 60, lm1 + bm * hissa / 60
    plon, plat = parallax(lm, lat)
    lmv = lm - plon / 60
    beta = asind(sind(5) * sind(lm - mean_node(T1))); bv = beta - plat / 60
    dm = asind(sind(bv) * cosd(EPS) + cosd(bv) * sind(EPS) * sind(lmv))
    am = n360(atan2d(sind(lmv) * cosd(EPS) - tand(bv) * sind(EPS), cosd(lmv)))
    ds = decl(ls); Hs = half_arc(lat, ds); Hm = half_arc(lat, dm)
    if Hs is None or Hm is None:
        v['grade'] = 'none'; return v
    lag = n180((am + Hm) - (ra(ls) + Hs))
    arcv = -asind(sind(lat) * sind(ds) + cosd(lat) * cosd(ds) * cosd(Hs + lag))
    alt = asind(sind(lat) * sind(dm) + cosd(lat) * cosd(dm) * cosd(Hm - lag))
    elong = n180(lmv - ls); nur = acosd(cosd(elong) * cosd(bv)); S = (arcv + elong) / 2
    q1 = lag >= 12 and arcv >= 12 and alt >= 10
    q2 = lag >= 8 and alt >= 6.5 and nur >= 10          # حدّ ابن يونس
    if v['elong_noon'] <= 0:
        g = 'pre'
    elif v['elong_noon'] <= DAL or lag <= 0:
        g = 0
    elif q1 or S >= 13:
        g = 3
    elif S < 7:
        g = 0
    else:
        g = 2 if S >= 10 else 1
    v.update(hissa=hissa, beta=beta, beta_vis=bv, plon=plon, plat=abs(plat), lag=lag, lag_min=lag * 4,
             arcv=arcv, alt=alt, elong=elong, nur=nur, S=S, q1=q1, q2=q2, grade=g)
    return v


def modern(day: dt.date, lat: float, lon: float, tz_hours: float = 2.0) -> dict:
    """الحساب الحديث مساء اليوم المدني: الغروبان (مع الانكسار)، والمكث، وعمر القمر، ومعيار عودة."""
    obs = A.Observer(lat, lon, 0)
    start = _t(noon_utc(day, lon))
    ss = A.SearchRiseSet(A.Body.Sun, obs, A.Direction.Set, start, 1)
    if ss is None:
        return {}
    ms = A.SearchRiseSet(A.Body.Moon, obs, A.Direction.Set, start, 1.2)
    lag_min = (ms.ut - ss.ut) * 1440 if ms is not None else float('nan')
    nm = A.SearchMoonPhase(0, ss.AddDays(-32), 32)       # آخر اجتماع قبل الغروب
    while nm is not None:
        nx = A.SearchMoonPhase(0, nm.AddDays(1), 31)
        if nx is None or nx.ut > ss.ut:
            break
        nm = nx
    age_h = (ss.ut - nm.ut) * 24 if nm is not None and nm.ut <= ss.ut else float('nan')
    tb = ss.AddDays(max(lag_min, 0) * 4 / 9 / 1440)       # أفضل وقت (يالوب)
    def topo(body):
        eq = A.Equator(body, tb, obs, True, True)
        hor = A.Horizon(tb, obs, eq.ra, eq.dec, A.Refraction.Airless)
        return eq, hor
    meq, mh = topo(A.Body.Moon); seq, sh = topo(A.Body.Sun)
    # البعد الزاوي السطحي بين المركزين
    r1, d1, r2, d2 = meq.ra * 15, meq.dec, seq.ra * 15, seq.dec
    arcl = acosd(sind(d1) * sind(d2) + cosd(d1) * cosd(d2) * cosd(r1 - r2))
    arcv = mh.altitude - sh.altitude
    dist_km = meq.dist * 149597870.7
    sd = math.degrees(math.asin(1737.4 / dist_km)) * 60
    W = sd * (1 - cosd(arcl))
    V = arcv - (7.1651 - 6.3226 * W + 0.7319 * W ** 2 - 0.1018 * W ** 3)
    zone = 'A' if V >= 5.65 else 'B' if V >= 2 else 'C' if V >= -0.96 else 'D'
    loc = lambda t: (t.Utc() + dt.timedelta(hours=tz_hours)).strftime('%H:%M') if t else ''
    return dict(sunset_local=loc(ss), moonset_local=loc(ms), lag_min_modern=lag_min, moon_age_h=age_h,
                conj_utc=nm.Utc().strftime('%Y-%m-%d %H:%M') if nm else '', arcl_topo=arcl, arcv_topo=arcv,
                W=W, odeh_V=V, odeh_zone=zone)
