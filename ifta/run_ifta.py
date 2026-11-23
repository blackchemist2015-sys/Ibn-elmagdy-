# -*- coding: utf-8 -*-
"""
مطابقة معيار ابن المجدي ببيانات دار الإفتاء المصرية، واستخراج «معيار دار الإفتاء» على بنية معيار ابن المجدي.

الاستعمال:
    python3 ifta/run_ifta.py ملف_البيانات.xlsx مجلد_النتائج [--exclude-calc]

ملف البيانات على قالب ifta/template/ifta_data_template.xlsx (ورقة «البيانات»)، صفٌّ لكل شهر هجري:
السنة، الشهر، أول الشهر المعلن (ميلادي)، وما توفر من: نتيجة التحري، أساس القرار، موضع الرؤية وإحداثياته، المصدر.

الفكرة: إذا عُرف أول كل شهر، فطول الشهر السابق يكشف نتيجة تحرّي الهلال مساء التاسع والعشرين منه:
  29 يومًا ← أُعلنت رؤية الهلال تلك الليلة؛  30 يومًا ← لم تثبت الرؤية فأُكمل الشهر.
"""
import os, sys, json, math, argparse, datetime as dt
from collections import Counter, defaultdict
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import majdi_engine as E

CAIRO = (30.0444, 31.2357)
HMONTHS = ['محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة', 'رجب', 'شعبان',
           'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة']
GRADE_AR = {3: 'يُرى بيّنًا', 2: 'جائزة قريبة إلى البيان', 1: 'جائزة قريبة من الخفاء', 0: 'غير ممكنة',
            'pre': 'قبل الاجتماع وقت الزوال', 'none': 'لا تغرب الشمس'}
HEAD = ['السنة الهجرية', 'الشهر الهجري', 'اسم الشهر', 'أول الشهر المعلن (ميلادي)',
        'ثبتت رؤية هلاله مساء 29 من الشهر السابق؟ (نعم/لا)', 'أساس القرار (رؤية/حساب/إكمال/غير معروف)',
        'موضع الرؤية', 'العرض', 'الطول', 'المصدر', 'ملاحظات']


# ---------------------------------------------------------------- قراءة البيانات
def as_date(x):
    if isinstance(x, dt.datetime):
        return x.date()
    if isinstance(x, dt.date):
        return x
    if isinstance(x, str) and x.strip():
        return dt.date.fromisoformat(x.strip()[:10])
    return None


def read_input(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb['البيانات'] if 'البيانات' in wb.sheetnames else wb.active
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r is None or r[0] in (None, '') or r[3] in (None, ''):
            continue
        rows.append(dict(hy=int(r[0]), hm=int(r[1]), start=as_date(r[3]),
                         seen_decl=(str(r[4]).strip() if r[4] not in (None, '') else ''),
                         basis=(str(r[5]).strip() if r[5] not in (None, '') else 'غير معروف'),
                         place=(r[6] or ''), lat=r[7], lon=r[8], source=(r[9] or ''), notes=(r[10] or '')))
    rows.sort(key=lambda x: (x['hy'], x['hm']))
    return rows


def derive_evenings(rows):
    """لكل شهرٍ معروفٍ أوله وأول الشهر الذي قبله: مساء التحري = أول السابق + 28 يومًا."""
    ev, warn = [], []
    for prev, cur in zip(rows, rows[1:]):
        nxt = (prev['hy'] + (prev['hm'] == 12), prev['hm'] % 12 + 1)
        if (cur['hy'], cur['hm']) != nxt:
            warn.append(f"انقطاع في التسلسل بين {prev['hm']}/{prev['hy']} و{cur['hm']}/{cur['hy']}")
            continue
        n = (cur['start'] - prev['start']).days
        if n not in (29, 30):
            warn.append(f"طول غير معتاد للشهر {prev['hm']}/{prev['hy']}: {n} يومًا")
            continue
        seen = n == 29
        d = cur['seen_decl']
        if d in ('نعم', 'لا') and (d == 'نعم') != seen:
            warn.append(f"تعارض في {cur['hm']}/{cur['hy']}: عمود النتيجة «{d}» وطول الشهر السابق {n}")
        lat = float(cur['lat']) if cur['lat'] not in (None, '') else CAIRO[0]
        lon = float(cur['lon']) if cur['lon'] not in (None, '') else CAIRO[1]
        ev.append(dict(hy=cur['hy'], hm=cur['hm'], start=cur['start'], evening=prev['start'] + dt.timedelta(days=28),
                       prev_len=n, seen=seen, basis=cur['basis'], place=cur['place'] or 'القاهرة',
                       lat=lat, lon=lon, source=cur['source'], notes=cur['notes']))
    return ev, warn


# ---------------------------------------------------------------- الحساب
def compute(ev, progress=True):
    for i, e in enumerate(ev):
        e['m'] = E.majdi(e['evening'], e['lat'], e['lon'])
        e['x'] = E.modern(e['evening'], e['lat'], e['lon'])
        if progress and i % 200 == 0:
            print(f'  {i}/{len(ev)}', flush=True)
    return ev


# ---------------------------------------------------------------- المطابقة
def metrics(pred, truth):
    pred, truth = np.asarray(pred, bool), np.asarray(truth, bool)
    tp = int(np.sum(pred & truth)); tn = int(np.sum(~pred & ~truth))
    fp = int(np.sum(pred & ~truth)); fn = int(np.sum(~pred & truth))
    n = len(pred)
    sens = tp / (tp + fn) if tp + fn else float('nan'); spec = tn / (tn + fp) if tn + fp else float('nan')
    return dict(n=n, agree=(tp + tn) / n if n else float('nan'), tp=tp, tn=tn, fp=fp, fn=fn,
                sensitivity=sens, specificity=spec, balanced=(sens + spec) / 2)


def arrays(ev):
    ok = [e for e in ev if e['m'].get('grade') not in ('none', None) and 'S' in e['m']]
    g = lambda k: np.array([e['m'][k] for e in ok], float)
    return ok, dict(en=g('elong_noon'), arcv=g('arcv'), el=g('elong'), lag=g('lag'), alt=g('alt'), nur=g('nur'),
                    seen=np.array([e['seen'] for e in ok]))


def fit_criterion(X, y, grid_e0=np.arange(0, 8.01, 0.25), grid_w=np.arange(0.2, 0.801, 0.05)):
    """بنية ابن المجدي: (1) بوابة الزوال: البعد وقت الزوال > E0؛ (2) S_w = w·الرؤية + (1−w)·البعد ≥ T.
    يُختار ما يعظّم الدقة المتوازنة (متوسط نسبتي الإصابة في المرئي وغير المرئي)."""
    best = None
    pos, neg = y.sum(), (~y).sum()
    for e0 in grid_e0:
        gate = X['en'] > e0
        for w in grid_w:
            S = w * X['arcv'] + (1 - w) * X['el']
            S = np.where(gate, S, -1e9)
            order = np.argsort(-S); Ss = S[order]; ys = y[order]
            tp = np.cumsum(ys); fp = np.cumsum(~ys)
            bal = 0.5 * (tp / max(pos, 1) + (neg - fp) / max(neg, 1))
            valid = Ss > -1e8
            if not valid.any():
                continue
            k = int(np.argmax(np.where(valid, bal, -1)))
            T = Ss[k] if k + 1 >= len(Ss) or Ss[k + 1] <= -1e8 else (Ss[k] + Ss[k + 1]) / 2
            if best is None or bal[k] > best['balanced'] + 1e-12:
                best = dict(E0=float(e0), w=float(w), T=float(T), balanced=float(bal[k]))
    return best


def predict(X, p):
    S = p['w'] * X['arcv'] + (1 - p['w']) * X['el']
    return (X['en'] > p['E0']) & (S >= p['T']), S


def logistic(s, y, iters=50):
    """انحدار لوجستي بمتغيرٍ واحد (طريقة نيوتن): احتمال الرؤية = 1/(1+exp(−(a+b·s)))"""
    a, b = 0.0, 0.0
    for _ in range(iters):
        z = np.clip(a + b * s, -30, 30); p = 1 / (1 + np.exp(-z)); W = p * (1 - p) + 1e-9
        g = np.array([np.sum(y - p), np.sum((y - p) * s)])
        H = np.array([[np.sum(W), np.sum(W * s)], [np.sum(W * s), np.sum(W * s * s)]])
        step = np.linalg.solve(H + 1e-9 * np.eye(2), g); a += step[0]; b += step[1]
        if np.abs(step).max() < 1e-8:
            break
    return a, b


def graded(a, b):
    """حدود الدرجات الأربع على S_w عند احتمال الرؤية 10٪ و50٪ و90٪"""
    s = lambda p: (math.log(p / (1 - p)) - a) / b
    return dict(T10=s(0.1), T50=s(0.5), T90=s(0.9))


def analyse(ev, exclude_calc=False, boot=200, seed=1):
    ok, X = arrays(ev)
    sel = np.array([not (exclude_calc and e['basis'] == 'حساب') for e in ok])
    Xs = {k: v[sel] for k, v in X.items()}; y = Xs['seen']
    res = dict(n_evenings=len(ok), n_used=int(sel.sum()), n_seen=int(y.sum()), n_not=int((~y).sum()))
    # معيار ابن المجدي كما هو
    g = np.array([e['m']['grade'] for e in ok], dtype=object)[sel]
    gi = np.array([x if isinstance(x, int) else -1 for x in g])
    res['majdi'] = {
        'الحكم ≥ قريبة من الخفاء': metrics(gi >= 1, y),
        'الحكم ≥ قريبة إلى البيان': metrics(gi >= 2, y),
        'الحكم = بيّن': metrics(gi == 3, y),
        'القول الأول (12، 12، 10)': metrics(np.array([e['m']['q1'] for e in ok])[sel], y),
        'حدّ ابن يونس (8، 6½، 10)': metrics(np.array([e['m']['q2'] for e in ok])[sel] & (Xs['en'] > 0), y),
        'شرط «دل» وحده': metrics(Xs['en'] > E.DAL, y),
    }
    oz = np.array([e['x'].get('odeh_zone', 'D') for e in ok])[sel]
    res['odeh'] = {'عودة: بالعين (A أو B)': metrics(np.isin(oz, ['A', 'B']), y),
                   'عودة: بأي وسيلة (A أو B أو C)': metrics(np.isin(oz, ['A', 'B', 'C']), y)}
    conf = defaultdict(Counter)
    for gg, yy in zip(g, y):
        conf[GRADE_AR.get(gg, str(gg))]['رُئي' if yy else 'لم يُرَ'] += 1
    res['confusion_majdi'] = {k: dict(v) for k, v in conf.items()}
    # معيار دار الإفتاء
    p = fit_criterion(Xs, y)
    pred, S = predict(Xs, p)
    p['metrics'] = metrics(pred, y)
    gate = Xs['en'] > p['E0']
    a, b = logistic(S[gate], y[gate].astype(float))
    p['logistic'] = dict(a=a, b=b, **graded(a, b))
    rng = np.random.default_rng(seed); bs = []
    for _ in range(boot):
        idx = rng.integers(0, len(y), len(y))
        q = fit_criterion({k: v[idx] for k, v in Xs.items()}, y[idx])
        bs.append((q['E0'], q['w'], q['T']))
    bs = np.array(bs)
    p['ci95'] = {k: [float(np.percentile(bs[:, i], 2.5)), float(np.percentile(bs[:, i], 97.5))]
                 for i, k in enumerate(['E0', 'w', 'T'])}
    # تحقق زمني: الملاءمة على نصف الفترة واختبارها على النصف الآخر
    years = np.array([e['hy'] for e in ok])[sel]; mid = np.median(years)
    tv = {}
    for name, tr in [('ملاءمة على النصف الأول واختبار على الثاني', years <= mid),
                     ('ملاءمة على النصف الثاني واختبار على الأول', years > mid)]:
        q = fit_criterion({k: v[tr] for k, v in Xs.items()}, y[tr])
        pr, _ = predict({k: v[~tr] for k, v in Xs.items()}, q)
        tv[name] = dict(params={k: q[k] for k in ('E0', 'w', 'T')}, test=metrics(pr, y[~tr]))
    p['time_validation'] = tv
    res['ifta_criterion'] = p
    # حسب العقود الهجرية
    dec = defaultdict(list)
    for e, gg, yy, pp in zip([e for e, s_ in zip(ok, sel) if s_], gi, y, pred):
        dec[(e['hy'] // 10) * 10].append((gg >= 2, yy, pp))
    res['by_decade'] = {f'{k}–{k + 9}': dict(n=len(v), majdi=float(np.mean([a_ == b_ for a_, b_, _ in v])),
                                              ifta=float(np.mean([c_ == b_ for _, b_, c_ in v])),
                                              seen_share=float(np.mean([b_ for _, b_, _ in v])))
                        for k, v in sorted(dec.items())}
    return res, ok, sel, pred, S


# ---------------------------------------------------------------- المخرجات
def style_sheet(ws, widths=None):
    ws.sheet_view.rightToLeft = True
    for c in ws[1]:
        c.font = Font(bold=True, name='Amiri'); c.fill = PatternFill('solid', fgColor='E0E7FF')
        c.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
    ws.freeze_panes = 'A2'
    for i, w in enumerate(widths or [], 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w


def write_excel(path, ev, ok, sel, pred, S, res, warn, label):
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = 'البيانات والحساب'
    cols = ['السنة', 'الشهر', 'أول الشهر المعلن', 'مساء التحري (29)', 'طول الشهر السابق', 'نتيجة دار الإفتاء',
            'أساس القرار', 'الموضع', 'البعد وقت الزوال', 'قوس المكث (د)', 'قوس الرؤية', 'قوس الارتفاع',
            'البعد المطلق', 'قوس النور', 'مؤشر المتأخرين S', 'حكم ابن المجدي', 'مطابقة ابن المجدي',
            'S_w (دار الإفتاء)', 'حكم معيار دار الإفتاء', 'غروب الشمس', 'غروب القمر', 'المكث الحديث (د)',
            'عمر القمر (س)', 'عودة V', 'نطاق عودة', 'المصدر', 'ملاحظات']
    ws.append(cols)
    pmap = {id(e): (bool(pp), float(s)) for e, pp, s in zip([e for e, s_ in zip(ok, sel) if s_], pred, S)}
    r2 = lambda x: round(x, 2) if isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x)) else ''
    for e in ev:
        m, x = e['m'], e['x']
        g = m.get('grade')
        agree = '' if g in ('none', None) else ('نعم' if ((isinstance(g, int) and g >= 2) == e['seen']) else 'لا')
        pp = pmap.get(id(e))
        ws.append([e['hy'], HMONTHS[e['hm'] - 1], e['start'].isoformat(), e['evening'].isoformat(), e['prev_len'],
                   'رُئي' if e['seen'] else 'لم يُرَ (أُكمل)', e['basis'], e['place'],
                   r2(m.get('elong_noon')), r2(m.get('lag_min')), r2(m.get('arcv')), r2(m.get('alt')),
                   r2(m.get('elong')), r2(m.get('nur')), r2(m.get('S')), GRADE_AR.get(g, ''), agree,
                   r2(pp[1]) if pp else '', ('يُرى' if pp[0] else 'لا يُرى') if pp else '',
                   x.get('sunset_local', ''), x.get('moonset_local', ''), r2(x.get('lag_min_modern')),
                   r2(x.get('moon_age_h')), r2(x.get('odeh_V')), x.get('odeh_zone', ''), e['source'], e['notes']])
    style_sheet(ws, [8, 11, 13, 13, 9, 14, 11, 10] + [10] * 19)
    # الملخص
    ws2 = wb.create_sheet('ملخص المطابقة')
    ws2.append(['المعيار', 'عدد الأمسيات', 'نسبة المطابقة', 'رؤية صحيحة', 'عدم رؤية صحيح', 'رؤية خاطئة',
                'فوات رؤية', 'الحساسية', 'النوعية', 'الدقة المتوازنة'])
    allm = list(res['majdi'].items()) + list(res['odeh'].items()) + [('معيار دار الإفتاء المستخرج', res['ifta_criterion']['metrics'])]
    for k, mm in allm:
        ws2.append([k, mm['n'], round(mm['agree'], 4), mm['tp'], mm['tn'], mm['fp'], mm['fn'],
                    round(mm['sensitivity'], 3), round(mm['specificity'], 3), round(mm['balanced'], 4)])
    ws2.append([]); ws2.append(['حكم ابن المجدي ↓ / نتيجة دار الإفتاء →', 'رُئي', 'لم يُرَ'])
    for k in ['يُرى بيّنًا', 'جائزة قريبة إلى البيان', 'جائزة قريبة من الخفاء', 'غير ممكنة', 'قبل الاجتماع وقت الزوال']:
        c = res['confusion_majdi'].get(k, {})
        ws2.append([k, c.get('رُئي', 0), c.get('لم يُرَ', 0)])
    style_sheet(ws2, [42, 12, 13, 11, 13, 11, 10, 10, 10, 13])
    # المعيار المستخرج
    p = res['ifta_criterion']; lg = p['logistic']
    ws3 = wb.create_sheet('المعيار المستخرج')
    ws3.append(['البند', 'القيمة', 'فترة الثقة 95٪'])
    rows = [('بوابة الزوال: البعد وقت الزوال أكبر من (درجة)', round(p['E0'], 2), p['ci95']['E0']),
            ('وزن قوس الرؤية w في S_w = w·الرؤية + (1−w)·البعد', round(p['w'], 2), p['ci95']['w']),
            ('حدّ الرؤية على S_w (درجة)', round(p['T'], 2), p['ci95']['T']),
            ('الدقة المتوازنة', round(p['balanced'], 4), ''),
            ('درجة «غير ممكنة»: S_w أقل من (احتمال 10٪)', round(lg['T10'], 2), ''),
            ('درجة «قريبة من الخفاء»: حتى (احتمال 50٪)', round(lg['T50'], 2), ''),
            ('درجة «قريبة إلى البيان»: حتى (احتمال 90٪)', round(lg['T90'], 2), ''),
            ('درجة «بيّن»: S_w من', round(lg['T90'], 2), '')]
    for a, b, c in rows:
        ws3.append([a, b, f'{c[0]:.2f} – {c[1]:.2f}' if isinstance(c, list) else c])
    ws3.append([]); ws3.append(['التحقق الزمني', 'المعاملات', 'نسبة المطابقة في نصف الاختبار'])
    for k, v in p['time_validation'].items():
        ws3.append([k, json.dumps({a: round(b, 2) for a, b in v['params'].items()}, ensure_ascii=False), round(v['test']['agree'], 4)])
    style_sheet(ws3, [55, 22, 24])
    ws4 = wb.create_sheet('حسب العقود')
    ws4.append(['العقد الهجري', 'عدد الأمسيات', 'نسبة الرؤية المعلنة', 'مطابقة ابن المجدي', 'مطابقة معيار دار الإفتاء'])
    for k, v in res['by_decade'].items():
        ws4.append([k, v['n'], round(v['seen_share'], 3), round(v['majdi'], 3), round(v['ifta'], 3)])
    style_sheet(ws4, [14, 12, 16, 16, 20])
    ws5 = wb.create_sheet('تنبيهات البيانات')
    ws5.append(['تنبيه']); [ws5.append([w]) for w in warn]
    style_sheet(ws5, [90])
    ws6 = wb.create_sheet('عن الملف')
    ws6.append(['البيان']); ws6.append([label])
    ws6.append(['حكم ابن المجدي «مطابق» إذا كان «قريبة إلى البيان» فما فوق والرؤية معلنة، أو دون ذلك والرؤية غير معلنة.'])
    ws6.append(['الحساب: Astronomy Engine؛ خطوات ابن المجدي من «خلاصة الأقوال»؛ معيار عودة (2004) للمقارنة.'])
    style_sheet(ws6, [110])
    wb.save(path)


def figures(outdir, ok, sel, res, label):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts')
    for f in ('Amiri-Regular.ttf', 'Amiri-Bold.ttf'):
        if os.path.exists(os.path.join(root, f)):
            font_manager.fontManager.addfont(os.path.join(root, f))
    plt.rcParams.update({'font.family': ['Amiri', 'DejaVu Sans'], 'font.size': 13, 'axes.unicode_minus': False})
    _, X = arrays(ok); Xs = {k: v[sel] for k, v in X.items()}; y = Xs['seen']
    p = res['ifta_criterion']; lg = p['logistic']
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(Xs['el'][~y], Xs['arcv'][~y], s=10, c='#9ca3af', alpha=0.6, label='لم تُعلن الرؤية (أُكمل الشهر)')
    ax.scatter(Xs['el'][y], Xs['arcv'][y], s=10, c='#15803d', alpha=0.7, label='أُعلنت الرؤية')
    x = np.linspace(0, 30, 100)
    for v_, c in [(7, '#b91c1c'), (10, '#b45309'), (13, '#15803d')]:
        ax.plot(x, 2 * v_ - x, color=c, lw=1.4, ls='--')
    w = p['w']
    for T_, c, t in [(lg['T10'], '#7c3aed', '10٪'), (lg['T50'], '#1d4ed8', '50٪'), (lg['T90'], '#0f766e', '90٪')]:
        ax.plot(x, (T_ - (1 - w) * x) / w, color=c, lw=2.2, label=f'دار الإفتاء: احتمال الرؤية {t}')
    ax.set_xlim(0, 30); ax.set_ylim(0, 30)
    ax.set_xlabel('البعد المطلق (درجة)'); ax.set_ylabel('قوس الرؤية (درجة)')
    ax.legend(loc='lower right', fontsize=10); ax.grid(alpha=0.3)
    ax.set_title(f'قرارات دار الإفتاء على مستوى ابن المجدي — الخطوط المتقطعة حدود المتأخرين 7 و10 و13\n{label}', fontsize=12)
    fig.savefig(os.path.join(outdir, 'ifta_plane.png'), dpi=160, bbox_inches='tight'); plt.close(fig)
    dec = res['by_decade']; ks = list(dec)
    fig, ax = plt.subplots(figsize=(12, 5))
    xi = np.arange(len(ks))
    ax.bar(xi - 0.2, [dec[k]['majdi'] * 100 for k in ks], 0.4, color='#15803d', label='معيار ابن المجدي')
    ax.bar(xi + 0.2, [dec[k]['ifta'] * 100 for k in ks], 0.4, color='#1d4ed8', label='معيار دار الإفتاء المستخرج')
    ax.set_xticks(xi); ax.set_xticklabels(ks, rotation=45, fontsize=10)
    ax.set_ylim(50, 105); ax.set_ylabel('نسبة المطابقة ٪'); ax.legend(loc='lower center', ncol=2, fontsize=11); ax.grid(axis='y', alpha=0.3)
    ax.set_title(f'المطابقة حسب العقود الهجرية — {label}', fontsize=12)
    fig.savefig(os.path.join(outdir, 'ifta_decades.png'), dpi=160, bbox_inches='tight'); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input'); ap.add_argument('outdir')
    ap.add_argument('--exclude-calc', action='store_true', help='استبعاد القرارات المبنية على الحساب من الملاءمة')
    ap.add_argument('--label', default='بيانات دار الإفتاء المصرية')
    ap.add_argument('--boot', type=int, default=200)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    rows = read_input(a.input)
    ev, warn = derive_evenings(rows)
    print(f'{len(rows)} شهرًا، {len(ev)} أمسية تحرٍّ، {len(warn)} تنبيهًا')
    compute(ev)
    res, ok, sel, pred, S = analyse(ev, a.exclude_calc, a.boot)
    write_excel(os.path.join(a.outdir, 'ifta_results.xlsx'), ev, ok, sel, pred, S, res, warn, a.label)
    figures(a.outdir, ok, sel, res, a.label)
    res['label'] = a.label; res['warnings'] = warn
    json.dump(res, open(os.path.join(a.outdir, 'ifta_summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    p = res['ifta_criterion']
    print(json.dumps({k: res['majdi'][k]['agree'] for k in res['majdi']}, ensure_ascii=False, indent=1))
    print('معيار دار الإفتاء:', {k: round(p[k], 3) for k in ('E0', 'w', 'T', 'balanced')}, p['logistic'])


if __name__ == '__main__':
    main()
