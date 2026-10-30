# -*- coding: utf-8 -*-
"""
خوارزمية ابن المجدي (ت 850 هـ) في «خلاصة الأقوال في معرفة الوقت ورؤية الهلال»
مكتوبة بلغة حديثة، مع مقارنتها بالحساب الفلكي الحديث (Skyfield + DE421)
وبمعياري يالوب (Yallop 1997) وعودة (Odeh 2004).

كل دالة تحمل في تعليقها نص ابن المجدي الذي تُنفّذه.
"""
import math
import numpy as np
from skyfield.api import load_file, wgs84
from skyfield import almanac
from skyfield.framelib import ecliptic_frame
import skyfield_data, os

D2R = math.pi / 180.0
EPS_MAJDI = 23 + 35 / 60          # الميل الأعظم عند فلكيي القرن التاسع (كج له)
R = 60.0                          # الستيني: نصف القطر في حساب الجيوب

_DATA = skyfield_data.get_skyfield_data_path()
eph = load_file(os.path.join(_DATA, 'de421.bsp'))
from skyfield.api import load
ts = load.timescale(builtin=True)
earth, sun, moon = eph['earth'], eph['sun'], eph['moon']

CAIRO = dict(name='القاهرة', lat=30.0444, lon=31.2357, tz=2.0)


def sind(x): return math.sin(x * D2R)
def cosd(x): return math.cos(x * D2R)
def tand(x): return math.tan(x * D2R)
def asind(x): return math.asin(max(-1.0, min(1.0, x))) / D2R
def acosd(x): return math.acos(max(-1.0, min(1.0, x))) / D2R
def atan2d(y, x): return math.atan2(y, x) / D2R
def norm360(x): return x % 360.0
def norm180(x): return (x + 180.0) % 360.0 - 180.0


# ---------------------------------------------------------------------------
# 1) مسائل الوقت بالربع المجيب
# ---------------------------------------------------------------------------
def shadow(h, gnomon=12.0):
    """«وضعت الخيط على مثل الارتفاع ... ونزلت إليه بالقامة ... وجدت الظل ... وجدت قطره»
    الظل المبسوط z = Q·ctg h ، وقطر الظل d = Q / sin h (Q = 12 إصبعًا أو 7 أقدام)."""
    return gnomon / tand(h), gnomon / sind(h)


def altitude_from_shadow(z, gnomon=12.0):
    return atan2d(gnomon, z)


def declination(lam, eps=EPS_MAJDI):
    """«ضع على الستيني والمري على جيب الميل الأعظم ونقلت إلى بعد الدرجة حاز المري جيب الميل»
    sin δ = sin ε · sin λ"""
    return asind(sind(eps) * sind(lam))


def meridian_altitude(phi, delta):
    """«إن نقصت الميل من تمام العرض في الجنوب وزدته عليه في الشمال حصلت الغاية،
    فإن زاد المجموع على ص (90) فهي تمام الزائد»  :  H = 90 − φ + δ"""
    g = 90 - phi + delta
    return 180 - g if g > 90 else g


def asl_and_qutr(phi, delta):
    """الأصل = R·cos δ·cos φ ، بُعد القطر = R·sin δ·sin φ"""
    return R * cosd(delta) * cosd(phi), R * sind(delta) * sind(phi)


def mahfuz1(phi, delta):
    """المحفوظ الأول = R·sin δ·tg φ  (ويساوي أيضا جيب سعة المشرق مضروبًا في sin φ)"""
    return R * sind(delta) * tand(phi)


def mahfuz2(phi, h):
    """المحفوظ الثاني = R·sin h / cos φ"""
    return R * sind(h) / cosd(phi)


def half_arc(phi, delta):
    """«فإن وقع المري على مثل المحفوظ الأول قطع الخيط من أول القوس نصف التعديل»
    sin(نصف التعديل) = tg φ·tg δ ، نصف قوس النهار = 90 + نصف التعديل (في الشمال)"""
    half_eq = asind(tand(phi) * tand(delta))
    return 90 + half_eq, half_eq


def hour_angle(phi, delta, h):
    """جيب الترتيب = المحفوظ الثاني ∓ المحفوظ الأول = R·cos δ·cos t
    «ضع على الستيني والمري على جيب تمام الميل ... فإن وقع المري على مثل جيب الترتيب
    قطع من آخره فضل الدائر»  :  cos t = (sin h − sin φ sin δ)/(cos φ cos δ)"""
    tartib = mahfuz2(phi, h) - mahfuz1(phi, delta)
    return acosd(tartib / (R * cosd(delta)))


def altitude_no_azimuth(phi, delta):
    """الارتفاع الذي لا سمت له (ارتفاع الشمس على دائرة أول السموت): sin h₀ = sin δ / sin φ"""
    return asind(sind(delta) / sind(phi)) if delta * phi > 0 and abs(delta) < abs(phi) else None


def azimuth(phi, delta, t, h):
    """«ضع على تمام الارتفاع والمري على جيب فضل الدائر ونقلت إلى الميل... وجدت السمت»
    sin A = cos δ·sin t / cos h  (A يُعدّ من خط المشرق والمغرب)، والصيغة التامة:"""
    # السمت من الجنوب نحو الغرب (موجبًا) ثم يُحوَّل إلى بعدٍ عن خط المشرق والمغرب
    A_s = atan2d(sind(t), cosd(t) * sind(phi) - tand(delta) * cosd(phi))
    return A_s


def asr_altitude(phi, delta, shafii=True):
    """«إن زدت على ظل مبسوط الغاية قامة واستخرجت ارتفاع الجملة حصل ارتفاع العصر»
    ctg h_asr = ctg H + 1 (المثل الأول)"""
    H = meridian_altitude(phi, delta)
    k = 1 if shafii else 2
    return math.atan(1.0 / (1.0 / tand(H) + k)) / D2R


def twilight_hour_angle(phi, delta, depression):
    """«إن استخرجت الدائر لارتفاع يط (19) أو يز (17) بدرجة النظير حصل حصتا الفجر والشفق»"""
    return hour_angle(phi, delta, -depression)


def qibla(phi, L, phi_m=21.4225, L_m=39.8262):
    """«إن جعلت عرض مكة بُعدًا ... وفضل الطولين فضل دائر وحصّلت سمت ارتفاعه حصل سمت تلك البلد»
    مكة تُعامَل ككوكب ميله = عرض مكة وفضل دائره = فضل الطولين."""
    dL = L_m - L
    q = atan2d(sind(dL), cosd(phi) * tand(phi_m) - sind(phi) * cosd(dL))
    return norm360(q)          # من الشمال نحو الشرق


def right_ascension(lam, eps=EPS_MAJDI):
    """«ضع على الميل ودخلت إليه في المنكوسة بقدر خمسة وخمسين» : 55 ≈ 60·cos ε
    tg α = cos ε·tg λ  (المطالع الفلكية، تُعدّ من أول الجدي بإضافة 90)"""
    return norm360(atan2d(cosd(eps) * sind(lam), cosd(lam)))


def oblique_ascension(lam, phi, eps=EPS_MAJDI):
    """مطالع البلد = المطالع الفلكية − نصف التعديل"""
    a = right_ascension(lam, eps)
    d = declination(lam, eps)
    return norm360(a - asind(tand(phi) * tand(d)))


def oblique_descension(lam, phi, eps=EPS_MAJDI):
    """مطالع الغروب لدرجةٍ = مطالع البلد لنظيرها (درجة + 180) — «مطالع نظير الشمس ونظير جزء الهلال»"""
    return oblique_ascension(norm360(lam + 180), phi, eps)


# ---------------------------------------------------------------------------
# 2) مسائل القمر
# ---------------------------------------------------------------------------
def moon_latitude_majdi(lam_moon, node):
    """«أسقطت مقوم الجوزهر من مقوم القمر تبقى الحصة، فضع على الستيني والمري على خمسة،
    وانقل إلى الحصة طردا وعكسا، وانزل من المري إلى القوس تجد عرض القمر وجهته شمال
    إن كانت الحصة أقل من ستة بروج»   sin β = sin 5° · sin(λ − Ω)"""
    F = norm360(lam_moon - node)
    return asind(sind(5.0) * sind(F))


def mean_node(t):
    T = (t.tt - 2451545.0) / 36525.0
    return norm360(125.0445479 - 1934.1362891 * T)


def interpolate_position(lam_noon, daily_motion, degrees_of_time):
    """«اقسم ما بين الوقت المفروض وأقرب الزوالين ... من الدرج على ستة أبدًا ... ضع على الستيني
    والمري على البهت وانقل إلى المحفوظ»  : Δλ = البهت × (الزمن بالأجزاء ÷ 6) ÷ 60 = البهت × ز/360"""
    return lam_noon + daily_motion * (degrees_of_time / 6.0) / 60.0


def parallax_correction_altitude(h):
    """«وينبغي أن تُعدَّل بزيادة درجة على الارتفاع من أول ارتفاعه إلى ثلاثين، ومن إحدى وثلاثين
    إلى ستين ثلاثة أرباع درجة، وبتمام الزائد على ذلك دقائق» — بالدرجات"""
    if h <= 30:
        return 1.0
    if h <= 60:
        return 0.75
    return (90 - h) / 60.0


def parallax_tables(lam):
    """اختلاف المنظر في الطول والعرض بحسب البعد عن الاعتدالين (بالدقائق):
    الطول: 51′ في رأس الحمل و30′ في رأس الميزان، والعرض: 6′ (و) في الحمل و41′ في الميزان.
    «وفيما بينهما يؤخذ بنسبة الفضل ويزاد على الأقل أو ينقص من الأكثر بحسب البعد عن أحد الاعتدالين»"""
    d = abs(norm180(lam))               # البعد عن رأس الحمل 0..180
    p_lon = 51 - (51 - 30) * d / 180.0
    p_lat = 6 + (41 - 6) * d / 180.0
    return p_lon, p_lat


# ---------------------------------------------------------------------------
# 3) الحساب الحديث للمواضع
# ---------------------------------------------------------------------------
def ecl_lonlat(body, t, topos=None):
    obs = earth if topos is None else earth + topos
    lat, lon, dist = obs.at(t).observe(body).apparent().frame_latlon(ecliptic_frame)
    return lon.degrees, lat.degrees, dist.km


def altaz(body, t, topos):
    alt, az, _ = (earth + topos).at(t).observe(body).apparent().altaz()
    return alt.degrees, az.degrees


def sunset_time(day_utc, loc):
    """غروب الشمس (مركزها مع الانكسار المعتاد كما في التقاويم: -0.8333°)"""
    topos = wgs84.latlon(loc['lat'], loc['lon'])
    t0 = ts.utc(day_utc.year, day_utc.month, day_utc.day, 12 - loc['tz'])
    t1 = ts.utc(day_utc.year, day_utc.month, day_utc.day, 23 - loc['tz'])
    f = almanac.sunrise_sunset(eph, topos)
    times, ev = almanac.find_discrete(t0, t1, f)
    for tt, e in zip(times, ev):
        if e == 0:
            return tt
    return None


def moonset_time(after, loc):
    topos = wgs84.latlon(loc['lat'], loc['lon'])
    f = almanac.risings_and_settings(eph, moon, topos)
    times, ev = almanac.find_discrete(after, after + 0.5, f)
    for tt, e in zip(times, ev):
        if e == 0:
            return tt
    return None


def new_moons(y0, y1):
    t0, t1 = ts.utc(y0, 1, 1), ts.utc(y1, 1, 1)
    times, phases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    return [t for t, p in zip(times, phases) if p == 0]


# ---------------------------------------------------------------------------
# 4) خوارزمية ابن المجدي للهلال (فصل: «متى كان بين مقومي النيرين ...»)
# ---------------------------------------------------------------------------
def majdi_hilal(day, loc, eps=EPS_MAJDI, use_majdi_latitude=True):
    """يحسب متغيرات ابن المجدي لمساء اليوم المعطى (تاريخ ميلادي).
    المدخلات الوحيدة من الفلك الحديث: مقوما النيرين (الطول الحقيقي) وقت الزوال يومين متتاليين
    — وهي ما كان يأخذه ابن المجدي من الزيج/التقويم — وكل ما بعدها بخطواته هو."""
    phi = loc['lat']
    noon = ts.utc(day.year, day.month, day.day, 12 - loc['lon'] / 15)   # الزوال الوسطي
    noon2 = noon + 1
    ls1, _, _ = ecl_lonlat(sun, noon)
    lm1, bm_true, _ = ecl_lonlat(moon, noon)
    ls2, _, _ = ecl_lonlat(sun, noon2)
    lm2, _, _ = ecl_lonlat(moon, noon2)
    baht_s = norm360(ls2 - ls1)              # بهت الشمس
    baht_m = norm360(lm2 - lm1)              # بهت القمر
    elong_noon = norm180(lm1 - ls1)          # «ما بين مقومي النيرين نصف النهار»

    # «استخرجت نصف قوس النهار ... بزيادة عشرة درج أبدًا وقسمت المبلغ على و حصل حصة البعد»
    ds = declination(ls1, eps)
    half_day, _ = half_arc(phi, ds)
    hissa = (half_day + 10.0) / 6.0
    ls = ls1 + baht_s * hissa / 60.0          # مقوم الشمس عند الرؤية
    lm = lm1 + baht_m * hissa / 60.0          # مقوم الهلال عند الرؤية

    # «إن نقصت من مقوم الهلال عند الرؤية دقائق اختلاف الطول حصلت درجته المرئية»
    p_lon, p_lat = parallax_tables(lm)
    lm_vis = lm - p_lon / 60.0
    node = mean_node(noon)
    beta = moon_latitude_majdi(lm, node) if use_majdi_latitude else bm_true
    beta_vis = beta - p_lat / 60.0            # الاختلاف في العرض جنوبي في عروضنا

    # قوس المكث المحقّق: بمطالع غروب الهلال بحسب عرضه المرئي
    dm = asind(sind(beta_vis) * cosd(eps) + cosd(beta_vis) * sind(eps) * sind(lm_vis))
    am = norm360(atan2d(sind(lm_vis) * cosd(eps) - tand(beta_vis) * sind(eps), cosd(lm_vis)))
    a_s = right_ascension(ls, eps)
    ds = declination(ls, eps)
    Hs, _ = half_arc(phi, ds)                     # نصف قوس نهار الشمس
    Hm, _ = half_arc(phi, dm)                     # نصف قوس نهار الهلال
    lag = norm180((am + Hm) - (a_s + Hs))         # قوس المكث (أجزاء معدل النهار)
    lag_approx = norm180(oblique_descension(lm_vis, phi, eps) - oblique_descension(ls, phi, eps))

    # قوس الرؤية: «طرحت قوس المكث من نصف قوس الليل لدرجة الشمس بقي فضل الدائر وارتفاعه بدرجة نظير الشمس»
    t_sun = Hs + lag
    arcv = -asind(sind(phi) * sind(ds) + cosd(phi) * cosd(ds) * cosd(t_sun))
    # قوس الارتفاع: «أسقطت قوس المكث من نصف قوس النهار بدرجة الهلال بقي فضل الدائر وارتفاعه»
    t_moon = Hm - lag
    alt = asind(sind(phi) * sind(dm) + cosd(phi) * cosd(dm) * cosd(t_moon))
    az_m = azimuth(phi, dm, t_moon, alt)
    az_s = azimuth(phi, ds, Hs, 0)
    amp_moon = asind(sind(dm) / cosd(phi))        # سعة مغرب الهلال
    # البعد المطلق وقوس النور: cos(النور) = cos(البعد المطلق)·cos(العرض)
    elong = norm180(lm_vis - ls)
    nur = acosd(cosd(elong) * cosd(beta_vis))
    S = (arcv + elong) / 2.0                      # نصف مجموع قوسي الرؤية والبعد المطلق
    return dict(elong_noon=elong_noon, baht_m=baht_m, baht_s=baht_s, hissa=hissa,
                lam_sun=ls, lam_moon=lm, lam_moon_vis=lm_vis, p_lon=p_lon, p_lat=p_lat,
                beta=beta, beta_true_noon=bm_true, beta_vis=beta_vis, dec_moon=dm, dec_sun=ds,
                lag=lag, lag_min=lag * 4, lag_approx=lag_approx, arcv=arcv, alt=alt,
                daz=norm180(az_m - az_s), amp_moon=amp_moon, elong=elong, nur=nur,
                nur_minutes=4 * nur, S=S)


def majdi_verdict(v, noon_limit=4.5):
    """تصنيف ابن المجدي بأقواله الثلاثة.
    يعيد (رمز, وصف):  0 غير ممكنة، 1 جائزة قريبة من الخفاء، 2 جائزة قريبة إلى البيان، 3 بيّنة."""
    if v['elong_noon'] <= noon_limit:
        return 0, 'غير ممكنة (البعد وقت الزوال ≤ دل)'
    if v['lag'] >= 12 and v['arcv'] >= 12 and v['alt'] >= 10:
        return 3, 'يُرى بيّنًا (المكث والرؤية ≥ 12 والارتفاع ≥ 10)'
    S = v['S']
    if S < 7:
        return 0, 'لا تجوز رؤيته (S < 7)'
    if S >= 13:
        return 3, 'رؤي بيّنًا (S ≥ 13)'
    if S >= 10:
        return 2, 'جائزة قريبة إلى البيان (10 ≤ S < 13)'
    return 1, 'جائزة قريبة من الخفاء (7 ≤ S < 10)'


def majdi_second_opinion(v):
    """القول الثاني: المكث ح (8) والارتفاع ز (7) [وفي نسخة: و = 6] والنور ي (10)"""
    return v['lag'] >= 8 and v['alt'] >= 7 and v['nur'] >= 10


# ---------------------------------------------------------------------------
# 5) الحساب الحديث للمعايير (يالوب وعودة)
# ---------------------------------------------------------------------------
def modern_hilal(day, loc):
    topos = wgs84.latlon(loc['lat'], loc['lon'])
    ss = sunset_time(day, loc)
    if ss is None:
        return None
    ms = moonset_time(ss - 0.25, loc)
    lag_min = (ms - ss) * 1440 if ms is not None else float('nan')
    tb = ss + (4.0 / 9.0) * max(lag_min, 0) / 1440.0      # أفضل وقت (يالوب)
    obs = (earth + topos).at(tb)
    m_app = obs.observe(moon).apparent()
    s_app = obs.observe(sun).apparent()
    malt, maz, mdist = m_app.altaz()
    salt, saz, _ = s_app.altaz()
    arcl = m_app.separation_from(s_app).degrees
    # ARCV الهندسي (دون انكسار) — مركزي الأرض لـ يالوب، سطحي لـ عودة
    g = earth.at(tb)
    gm = g.observe(moon).apparent()
    gs = g.observe(sun).apparent()
    # ارتفاع مركزي-أرضي: نحسبه من الإحداثيات الاستوائية مع زاوية الساعة المحلية
    def geo_alt(app):
        ra, dec, _ = app.radec(epoch='date')
        gast = tb.gast * 15
        H = gast + loc['lon'] - ra.hours * 15
        return asind(sind(loc['lat']) * sind(dec.degrees) + cosd(loc['lat']) * cosd(dec.degrees) * cosd(H))
    arcv_geo = geo_alt(gm) - geo_alt(gs)
    arcv_topo = malt.degrees - salt.degrees
    daz = norm180(maz.degrees - saz.degrees)
    # عرض الهلال (دقائق قوس)
    d_km = mdist.km
    sd = math.degrees(math.asin(1737.4 / d_km)) * 60      # نصف القطر الظاهري (دقائق)
    W = sd * (1 - cosd(arcl))
    q = (arcv_geo - (11.8371 - 6.3226 * W + 0.7319 * W ** 2 - 0.1018 * W ** 3)) / 10.0
    V = arcv_topo - (7.1651 - 6.3226 * W + 0.7319 * W ** 2 - 0.1018 * W ** 3)
    return dict(sunset=ss, moonset=ms, lag_min=lag_min, arcl=arcl, arcv_geo=arcv_geo,
                arcv_topo=arcv_topo, daz=daz, W=W, q=q, V=V, moon_alt_best=malt.degrees)


def yallop_zone(q):
    for lim, z in [(0.216, 'A'), (-0.014, 'B'), (-0.160, 'C'), (-0.232, 'D'), (-0.293, 'E')]:
        if q > lim:
            return z
    return 'F'


def odeh_zone(V):
    if V >= 5.65:
        return 'A'    # بالعين المجردة
    if V >= 2.0:
        return 'B'    # بالعين وقد تحتاج أداة
    if V >= -0.96:
        return 'C'    # بالأداة البصرية فقط
    return 'D'        # غير ممكنة
