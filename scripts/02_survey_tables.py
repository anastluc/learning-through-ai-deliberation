"""Build the dashboard datasets (JSON row arrays) from the re-analysis results.
Paired students are renumbered P01..P13.
Input: outputs/survey/. Output: outputs/survey/tables/*.json (used by make_figures.py).
The group linkage used in the chapter (matching respondents to groups by name) is not reproducible from the
shared data and is omitted."""
import json, pandas as pd, numpy as np, os
os.makedirs('outputs/survey/tables', exist_ok=True)
R = json.load(open('outputs/survey/survey_results.json'))
d = pd.read_csv('outputs/survey/survey_clean_long.csv')
SC = R['scale_def']
LAB = {'CT': 'Critical thinking', 'SR': 'Self-regulation', 'DEEP': 'Deep approach',
       'SURF': 'Surface / strain', 'LG': 'Perceived learning gain',
       'AC': 'Course-activity contribution', 'OV': 'Rating of assignment & tools'}
f2 = lambda x: f'{x:.2f}'
def pfmt(p):
    return '< .001' if p < .001 else ('= ' + f'{p:.3f}'.lstrip('0') if p < .01 else '= ' + f'{p:.2f}'.lstrip('0'))
def r2(x): return f'{x:.2f}'.replace('0.', '.', 1) if abs(x) < 1 else f'{x:.2f}'
def rho(x): return ('−' if x < 0 else '') + f'{abs(x):.2f}'.lstrip('0')
def pct(x): return f'{x:.0f}%'
def signed(x): return ('+' if x >= 0 else '−') + f'{abs(x):.2f}'

# ---------- scales ----------
rows = []
paired = {p['scale']: p for p in R['paired']}
base = {b['scale']: b for b in R['baseline_selection']}
late = {l['scale']: l for l in R['late_respondents']}
cross = {c['scale']: c for c in R['cross_sectional']}
for k in SC:
    rel = R['reliability'][k]; p = paired[k]
    rows.append(dict(scale=k, label=LAB[k], items=', '.join(SC[k]['items']), n_items=len(SC[k]['items']),
                     alpha=round(rel['students_latest']['alpha'], 3), alpha_lo=round(rel['students_latest']['lo'], 3),
                     alpha_hi=round(rel['students_latest']['hi'], 3), alpha_r1=round(rel['R1']['alpha'], 3),
                     alpha_r2=round(rel['R2']['alpha'], 3), retest=round(R['test_retest'][k], 3),
                     r1_mean=round(cross[k]['r1'], 3), r2_mean=round(cross[k]['r2'], 3), cross_delta=round(cross[k]['cliffs'], 3),
                     paired_r1=round(p['r1'], 3), paired_r2=round(p['r2'], 3), diff=round(p['mean_diff'], 3),
                     ci_lo=round(p['ci_lo'], 3), ci_hi=round(p['ci_hi'], 3), p=round(p['wilcoxon_p'], 4),
                     holm_p=round(p['holm_p'], 4), up=p['up'], down=p['down'], same=p['same'],
                     rtm_expected=round(R['rtm'][k]['expected_shift'], 3),
                     base_delta=round(base[k]['cliffs'], 3), base_holm=round(base[k]['holm_p'], 4),
                     r1only_mean=round(late[k]['r1only'], 3), r2only_mean=round(late[k]['r2only'], 3)))
json.dump(rows, open('outputs/survey/tables/scales.json', 'w'), indent=0)

# ---------- cohorts (long) ----------
coh = []
for k in SC:
    s = R['scales'][k]
    for i, (key, name) in enumerate([('R1only', 'Round 1 only'), ('pairedR1', 'Both rounds — R1'),
                                      ('pairedR2', 'Both rounds — R2'), ('R2only', 'Round 2 only')]):
        coh.append(dict(id=f'{k}_{key}', scale=k, label=LAB[k], cohort=name, order=i,
                        n=s[key]['n'], mean=round(s[key]['mean'], 3), sd=round(s[key]['sd'], 3)))
json.dump(coh, open('outputs/survey/tables/cohorts.json', 'w'), indent=0)

# ---------- paired students (long) ----------
P1 = d[(d['round'] == 'R1') & (d.grp == 'paired')].set_index('pid').sort_index()
P2 = d[(d['round'] == 'R2') & (d.grp == 'paired')].set_index('pid').sort_index()
order = list((P2['OV'] - P1['OV']).sort_values().index)
alias = {pid: f'P{i+1:02d}' for i, pid in enumerate(order)}
pr = []
for pid in order:
    for k in ['OV', 'DEEP', 'SR', 'CT', 'LG', 'AC']:
        pr.append(dict(id=f'{alias[pid]}_{k}', student=alias[pid], scale=k, label=LAB[k],
                       r1=round(float(P1.loc[pid, k]), 3), r2=round(float(P2.loc[pid, k]), 3)))
json.dump(pr, open('outputs/survey/tables/paired_students.json', 'w'), indent=0)

# ---------- items (long, per round and student-level) ----------
BLOCK = {'CT': 'Critical thinking (self-description)', 'SR': 'Self-regulation (self-description)',
         'LA': 'Approach during the assignment', 'LG': 'Perceived learning gain',
         'AC': 'Contribution of course activities', 'OV': 'Assignment & tools'}
DEEPSET = {'LA1', 'LA3', 'LA5', 'LA7', 'LA9'}
it = []
for row in R['items']:
    c = row['code']
    kind = 'deep' if c in DEEPSET else ('surface' if c.startswith('LA') else '')
    for nm, lab in [('R1', 'Round 1'), ('R2', 'Round 2'), ('S', 'Students (latest)')]:
        x = row[nm]
        it.append(dict(id=f'{c}_{nm}', code=c, text=row['text'], block=BLOCK[c[:2]], kind=kind, scale_type=row['scale'],
                       sample=lab, n=x['n'], mean=round(x['mean'], 3), d1=x['dist'][0], d2=x['dist'][1], d3=x['dist'][2],
                       d4=x['dist'][3], d5=x['dist'][4], pct_agree=round(x['pct4'], 1), pct_disagree=round(x['pct12'], 1),
                       agree_lo=round(x['pct4_lo'], 1), agree_hi=round(x['pct4_hi'], 1)))
json.dump(it, open('outputs/survey/tables/items.json', 'w'), indent=0)

# ---------- correlations with OV ----------
ITX = R['item_text']
corr = []
def add(key, xlab, ylab, group, res):
    for nm, lab in [('R1', 'Round 1 (n = 30)'), ('R2', 'Round 2 (n = 25)'), ('S', 'Students (n = 42)')]:
        r = res[nm]
        corr.append(dict(id=f'{key}_{nm}', key=key, x=xlab, y=ylab, group=group, sample=lab,
                         rho=round(r['rho'], 3), lo=round(r['lo'], 3), hi=round(r['hi'], 3), p=round(r['p'], 4)))
cmap = {(c['x'], c['y']): c for c in R['correlations']}
add('DEEP_OV', 'Deep approach scale (5 items)', 'OV', 'Deep approach', cmap[('DEEP', 'OV')])
add('DEEPc_OV', 'Deep strategies only (LA1, LA5, LA9)', 'OV', 'Deep approach', cmap[('DEEPc', 'OV')])
for itm, lab in [('LA7', 'LA7 personal satisfaction from the assignment'), ('LA3', 'LA3 interest in the group’s topic'),
                 ('LA5', 'LA5 understand concepts thoroughly'), ('LA1', 'LA1 relate to previous knowledge'),
                 ('LA9', 'LA9 see how viewpoints co-exist')]:
    add(f'{itm}_OV', lab, 'OV', 'Deep-approach items', R['deep_items_vs_OV'][itm])
add('SR_OV', 'Self-regulation', 'OV', 'Other scales', cmap[('SR', 'OV')])
add('CT_OV', 'Critical thinking', 'OV', 'Other scales', cmap[('CT', 'OV')])
add('LG_OV', 'Perceived learning gain', 'OV', 'Other scales', cmap[('LG', 'OV')])
add('AC_OV', 'Course-activity contribution', 'OV', 'Other scales', cmap[('AC', 'OV')])
add('LA10_OV2', 'LA10 overwhelmed by nuance → OV2 changed my thinking', 'OV2', 'Exploratory', R['exploratory_LA10_OV2'])
json.dump(corr, open('outputs/survey/tables/correlations.json', 'w'), indent=0)

# ---------- OV agreement (student level) ----------
ov = []
for o in ['OV1', 'OV2', 'OV3']:
    x = R['ov_student'][o]
    ov.append(dict(item=o, text=ITX[o], n=x['n'], agree=x['agree'], neutral=x['neutral'], disagree=x['disagree'],
                   pct=round(x['agree'] / x['n'] * 100, 1), lo=round(x['agree_ci'][0], 1), hi=round(x['agree_ci'][1], 1),
                   agree_first=x['agree_first'], pct_first=round(x['agree_first'] / x['n'] * 100, 1)))
json.dump(ov, open('outputs/survey/tables/ov_agreement.json', 'w'), indent=0)

