# -*- coding: utf-8 -*-
import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['Amiri', 'DejaVu Sans']
o = json.load(open('data/criteria_compare.json'))
c = o['confusion']
classes = [('غير ممكنة', '#8B1E2D'), ('تلسكوب', '#E9A23B'), ('منظار', '#7FB069'), ('عين', '#2F7F79')]
lab = {'غير ممكنة': 'غير ممكنة حتى بالتلسكوب', 'تلسكوب': 'بالتلسكوب فقط', 'منظار': 'بالمنظار، وقد تُرى بالعين', 'عين': 'بالعين المجردة'}
grades = [('0', 'غير ممكنة'), ('1', 'جائزة قريبة من الخفاء'), ('2', 'جائزة قريبة من البيان'), ('3', 'بيّن')]
fig, ax = plt.subplots(figsize=(12, 5.2))
for i, (g, gname) in enumerate(grades):
    tot = sum(c[k].get(g, 0) for k, _ in classes); left = 0
    for k, col in classes:
        v = c[k].get(g, 0) / tot * 100
        ax.barh(i, v, left=left, color=col, label=lab[k] if i == 0 else None, height=.62)
        if v >= 6: ax.text(left + v / 2, i, f'{v:.0f}%', ha='center', va='center', color='white', fontsize=12, weight='bold')
        left += v
    ax.text(101, i, f'{tot} أمسية', va='center', fontsize=11)
ax.set_yticks(range(4)); ax.set_yticklabels([g[1] for g in grades], fontsize=13)
ax.set_xlim(0, 112); ax.set_xlabel('نسبة الأمسيات في كل درجة إمكان (معيار عودة 2004)', fontsize=12)
ax.set_title('كل درجة من درجات ابن المجدي: بأيّ وسيلة يُرى الهلال فيها؟ (القاهرة، 2020 أمسية)', fontsize=15)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=4, fontsize=11, frameon=False)
for s in ['top', 'right']: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig('figures/y02_majdi_ladder.png', dpi=150)

cr = o['criteria']
names = [k for k in cr if not k.startswith('ابن المجدي')]
names.sort(key=lambda k: cr[k]['vs_majdi1'])
fig, ax = plt.subplots(figsize=(12, 7.6))
y = range(len(names))
ax.barh([i + .2 for i in y], [cr[k]['vs_majdi1'] for k in names], height=.38, color='#C8922A', label='مع «جائزة قريبة من الخفاء» فما فوقها (الإمكان)')
ax.barh([i - .2 for i in y], [cr[k]['vs_majdi2'] for k in names], height=.38, color='#2F7F79', label='مع «جائزة قريبة من البيان» فما فوقها')
for i, k in enumerate(names):
    ax.text(cr[k]['vs_majdi1'] + .3, i + .2, f"{cr[k]['vs_majdi1']:.1f}", va='center', fontsize=9)
    ax.text(cr[k]['vs_majdi2'] + .3, i - .2, f"{cr[k]['vs_majdi2']:.1f}", va='center', fontsize=9)
short = lambda k: k.split(' (')[0] if '(' in k and not k.startswith(('يالوب','عودة')) else k.replace('(A–B)','').replace('(A–D)','').replace('(A–C)','').replace('(A)','').strip()
ax.set_yticks(list(y)); ax.set_yticklabels([short(k) for k in names], fontsize=12)
ax.set_xlim(60, 101); ax.set_xlabel('نسبة الأمسيات التي اتفق فيها المعيار وحكم ابن المجدي (%)', fontsize=12)
ax.set_title('موافقة المعايير القديمة والحديثة لمعيار ابن المجدي (القاهرة، 2020 أمسية)', fontsize=15)
ax.legend(loc='upper center', bbox_to_anchor=(0.4, -0.1), ncol=2, fontsize=11, frameon=False)
for s in ['top', 'right']: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig('figures/y03_criteria_vs_majdi.png', dpi=150)
