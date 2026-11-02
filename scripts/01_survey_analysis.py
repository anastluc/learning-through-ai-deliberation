"""Re-analysis of the Smart Cities module learning survey (two rounds).

Design decisions (stated up front so they can be challenged):
- Unit of analysis is the STUDENT, not the response. 13 students answered twice, so
  pooling the 55 responses double-counts them and makes R1-vs-R2 tests non-independent.
- Three mutually exclusive response groups: R1-only, both rounds (paired), R2-only.
- Within-person change is tested only on the paired group (Wilcoxon signed-rank,
  Holm-corrected across the 7 scales). Cross-sectional round means are descriptive.
- Correlations are computed separately in each round (independent samples) so the
  second round acts as a replication of the first.
- Negatively worded items are NOT reverse-coded; they form a separate scale.

Input: data/raw_pseudonymised/survey/. Output: outputs/survey/survey_results.json and survey_clean_long.csv.
Timestamps in the shared files are truncated to the hour, so the within-round timing figures differ slightly
from those computed on the original exports.
"""
import json, os, re
import numpy as np, pandas as pd
from scipy import stats

rng = np.random.default_rng(20261017)
B = 5000

IN = 'data/raw_pseudonymised/survey'
OUT = 'outputs/survey'
os.makedirs(OUT, exist_ok=True)
R1 = pd.read_csv(f'{IN}/survey_round1.csv')
R2 = pd.read_csv(f'{IN}/survey_round2.csv')
assert list(R1.columns) == list(R2.columns)

TRUTH = {'Not at all true for me': 1, 'Slightly true for me': 2, 'Moderately true for me': 3,
         'Mostly true for me': 4, 'Very true for me': 5}
GAIN = {'No gain': 1, 'Small gain': 2, 'Moderate gain': 3, 'Good gain': 4, 'Great gain': 5}

codes = ([f'CT{i}' for i in range(1, 6)] + [f'SR{i}' for i in range(1, 6)] +
         [f'LA{i}' for i in range(1, 11)] + [f'LG{i}' for i in range(1, 9)] +
         [f'AC{i}' for i in range(1, 6)] + [f'OV{i}' for i in range(1, 4)])
item_cols = list(R1.columns[2:])
assert len(item_cols) == 36
def short(c):
    m = re.findall(r'\[([^\]]+)\]', c)
    return m[-1].strip() if m else c
ITEMS = {code: short(c) for code, c in zip(codes, item_cols)}

def recode(df, rnd):
    out = pd.DataFrame()
    out['pid'] = df['respondent_id']
    out['ts'] = pd.to_datetime(df['timestamp_hour'], format='%Y-%m-%d %H:%M')
    out['round'] = rnd
    for code, col in zip(codes, item_cols):
        m = GAIN if code.startswith(('LG', 'AC')) else TRUTH
        v = df[col].map(m)
        bad = df[col].notna() & v.isna()
        assert not bad.any(), (code, df[col][bad].unique())
        out[code] = v
    out = out[out[codes].notna().any(axis=1)].copy()
    return out

d1, d2 = recode(R1, 'R1'), recode(R2, 'R2')
assert d1[codes].notna().all().all() and d2[codes].notna().all().all()
both = set(d1.pid) & set(d2.pid)
d1['grp'] = np.where(d1.pid.isin(both), 'paired', 'R1-only')
d2['grp'] = np.where(d2.pid.isin(both), 'paired', 'R2-only')

SCALES = {
    'CT': ('Critical thinking (self-description)', ['CT1', 'CT2', 'CT3', 'CT4', 'CT5']),
    'SR': ('Self-regulation (self-description)', ['SR1', 'SR2', 'SR3', 'SR4', 'SR5']),
    'DEEP': ('Deep / engaged approach', ['LA1', 'LA3', 'LA5', 'LA7', 'LA9']),
    'SURF': ('Surface / strain approach', ['LA2', 'LA4', 'LA6', 'LA8', 'LA10']),
    'LG': ('Perceived learning gain', [f'LG{i}' for i in range(1, 9)]),
    'AC': ('Perceived contribution of course activities', [f'AC{i}' for i in range(1, 6)]),
    'OV': ('Overall rating of the deliberation assignment and tools', ['OV1', 'OV2', 'OV3']),
}
# Deep approach without the two items that evaluate the assignment itself (overlap with OV)
DEEP_CORE = ['LA1', 'LA5', 'LA9']

for d in (d1, d2):
    for k, (_, its) in SCALES.items():
        d[k] = d[its].mean(axis=1)
    d['DEEPc'] = d[DEEP_CORE].mean(axis=1)
    d['allmean'] = d[codes].mean(axis=1)
    d['sd_all'] = d[codes].std(axis=1, ddof=1)

R = {'meta': {}, 'quality': {}}
R['meta'] = dict(r1_rows=len(R1), r2_rows=len(R2), r1_valid=len(d1), r2_valid=len(d2),
                 paired=len(both), r1_only=int((d1.grp == 'R1-only').sum()),
                 r2_only=int((d2.grp == 'R2-only').sum()),
                 students=len(set(d1.pid) | set(d2.pid)),
                 r1_dates=[str(d1.ts.min()), str(d1.ts.max())],
                 r2_dates=[str(d2.ts.min()), str(d2.ts.max())])

# ---------- data quality ----------
allr = pd.concat([d1, d2])
R['quality']['straightliners'] = int((allr.sd_all == 0).sum())
R['quality']['low_variance_lt_0.5'] = int((allr.sd_all < 0.5).sum())
# logically inconsistent pairs: memorise (LA2>=4) AND understand thoroughly (LA5>=4)
R['quality']['LA2hi_and_LA5hi'] = int(((allr.LA2 >= 4) & (allr.LA5 >= 4)).sum())
R['quality']['LA4hi_and_LA3hi'] = int(((allr.LA4 >= 4) & (allr.LA3 >= 4)).sum())

# ---------- helpers ----------
def alpha(df):
    k = df.shape[1]
    return k / (k - 1) * (1 - df.var(ddof=1).sum() / df.sum(axis=1).var(ddof=1))

def alpha_ci(df):
    a = alpha(df)
    n = len(df)
    bs = [alpha(df.iloc[rng.integers(0, n, n)]) for _ in range(2000)]
    return a, np.percentile(bs, 2.5), np.percentile(bs, 97.5)

def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h

def spearman_ci(x, y):
    x, y = np.asarray(x), np.asarray(y)
    rho, p = stats.spearmanr(x, y)
    n = len(x)
    bs = []
    for _ in range(B):
        i = rng.integers(0, n, n)
        if np.std(x[i]) == 0 or np.std(y[i]) == 0: continue
        bs.append(stats.spearmanr(x[i], y[i])[0])
    return dict(rho=float(rho), p=float(p), lo=float(np.percentile(bs, 2.5)),
                hi=float(np.percentile(bs, 97.5)), n=int(n))

def holm(ps):
    ps = np.asarray(ps, float); m = len(ps); o = np.argsort(ps)
    adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1, run)
    return adj

def cliffs(a, b):
    a, b = np.asarray(a), np.asarray(b)
    gt = sum((x > y) for x in a for y in b); lt = sum((x < y) for x in a for y in b)
    return (gt - lt) / (len(a) * len(b))

# Student-level frame: one row per student, latest response (sensitivity: first response)
stud_latest = pd.concat([d1[d1.grp == 'R1-only'], d2])
stud_first = pd.concat([d1, d2[d2.grp == 'R2-only']])
assert stud_latest.pid.is_unique and stud_first.pid.is_unique

# ---------- reliability ----------
R['reliability'] = {}
for k, (lab, its) in SCALES.items():
    row = {'label': lab, 'items': its}
    for nm, d in [('R1', d1), ('R2', d2), ('students_latest', stud_latest)]:
        a, lo, hi = alpha_ci(d[its])
        row[nm] = dict(alpha=float(a), lo=float(lo), hi=float(hi), n=len(d))
    # alpha if item deleted & item-rest on student-level frame
    d = stud_latest
    row['item_stats'] = []
    for it in its:
        rest = [x for x in its if x != it]
        r_ir = stats.pearsonr(d[it], d[rest].mean(axis=1))[0] if len(rest) else np.nan
        row['item_stats'].append(dict(item=it, alpha_if_deleted=float(alpha(d[rest])) if len(rest) > 1 else None,
                                      item_rest_r=float(r_ir)))
    R['reliability'][k] = row
a, lo, hi = alpha_ci(stud_latest[DEEP_CORE])
R['reliability']['DEEPc'] = dict(label='Deep approach, core strategy items (LA1, LA5, LA9)', items=DEEP_CORE,
                                 students_latest=dict(alpha=float(a), lo=float(lo), hi=float(hi), n=len(stud_latest)))

# ---------- general factor (halo / acquiescence check) ----------
for nm, d in [('students_latest', stud_latest), ('R1', d1), ('R2', d2)]:
    C = d[codes].corr(method='spearman').values
    ev = np.sort(np.linalg.eigvalsh(C))[::-1]
    R.setdefault('general_factor', {})[nm] = dict(first_eig=float(ev[0]), share=float(ev[0] / ev.sum()),
                                                  second_eig=float(ev[1]), n=len(d))
# among positively worded non-OV items only
pos = [c for c in codes if c not in ('LA2', 'LA4', 'LA6', 'LA8', 'LA10')]
C = stud_latest[pos].corr(method='spearman').values
R['general_factor']['positive_items_mean_r'] = float(C[np.triu_indices_from(C, 1)].mean())

# ---------- descriptives per item ----------
R['items'] = []
for c in codes:
    row = dict(code=c, text=ITEMS[c], scale='gain' if c.startswith(('LG', 'AC')) else 'truth')
    for nm, d in [('R1', d1), ('R2', d2), ('S', stud_latest)]:
        v = d[c]; n = len(v); k = int((v >= 4).sum())
        lo, hi = wilson(k, n)
        row[nm] = dict(n=n, mean=float(v.mean()), sd=float(v.std(ddof=1)), median=float(v.median()),
                       pct4=float(k / n * 100), pct4_lo=float(lo * 100), pct4_hi=float(hi * 100),
                       pct12=float((v <= 2).sum() / n * 100),
                       dist=[int((v == s).sum()) for s in range(1, 6)])
    R['items'].append(row)

# ---------- scale descriptives by response group ----------
R['scales'] = {}
for k, (lab, its) in SCALES.items():
    row = {'label': lab}
    for nm, d in [('R1', d1), ('R2', d2), ('S', stud_latest),
                  ('R1only', d1[d1.grp == 'R1-only']), ('pairedR1', d1[d1.grp == 'paired']),
                  ('pairedR2', d2[d2.grp == 'paired']), ('R2only', d2[d2.grp == 'R2-only'])]:
        v = d[k]
        row[nm] = dict(n=len(v), mean=float(v.mean()), sd=float(v.std(ddof=1)), median=float(v.median()))
    R['scales'][k] = row

# ---------- paired change (13 students) ----------
P1 = d1[d1.grp == 'paired'].set_index('pid').sort_index()
P2 = d2[d2.grp == 'paired'].set_index('pid').sort_index()
assert list(P1.index) == list(P2.index)
paired = []
for k in SCALES:
    # Differences are rounded so that equal changes compare equal. Without rounding, floating-point noise in
    # means of 3-8 items breaks tied differences at random and scipy uses the exact no-ties null distribution.
    # The October 2026 chapter draft was computed without rounding (see data/README.md, "Known issues").
    diff = np.round((P2[k] - P1[k]).values, 8)
    w = stats.wilcoxon(diff, zero_method='wilcox', method='auto')
    # exact sign test
    up, down = int((diff > 0).sum()), int((diff < 0).sum())
    sign_p = stats.binomtest(up, up + down).pvalue if up + down else 1.0
    bs = [diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(B)]
    # matched-pairs rank-biserial
    nz = diff[diff != 0]; rk = stats.rankdata(np.abs(nz))
    rrb = (rk[nz > 0].sum() - rk[nz < 0].sum()) / rk.sum() if len(nz) else 0
    dz = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) > 0 else np.nan
    paired.append(dict(scale=k, n=len(diff), r1=float(P1[k].mean()), r2=float(P2[k].mean()),
                       mean_diff=float(diff.mean()), median_diff=float(np.median(diff)),
                       ci_lo=float(np.percentile(bs, 2.5)), ci_hi=float(np.percentile(bs, 97.5)),
                       wilcoxon_p=float(w.pvalue), up=up, down=down, same=int((diff == 0).sum()),
                       sign_p=float(sign_p), rank_biserial=float(rrb), dz=float(dz),
                       per_student=[[float(a), float(b)] for a, b in zip(P1[k], P2[k])]))
adj = holm([p['wilcoxon_p'] for p in paired])
for p, a in zip(paired, adj): p['holm_p'] = float(a)
R['paired'] = paired

# Test-retest (stability) among the 13: Spearman R1 vs R2 per scale
R['test_retest'] = {k: float(stats.spearmanr(P1[k], P2[k])[0]) for k in SCALES}

# regression-to-the-mean estimate: expected shift = (1 - r_tt) * (cohort R1 mean - paired R1 mean)
R['rtm'] = {}
for k in SCALES:
    rtt = R['test_retest'][k]
    exp = (1 - max(rtt, 0)) * (d1[k].mean() - P1[k].mean())
    R['rtm'][k] = dict(cohort_r1=float(d1[k].mean()), paired_r1=float(P1[k].mean()),
                       rtt=float(rtt), expected_shift=float(exp))

# ---------- did repeaters differ from R1-only at baseline? (selection) ----------
base = []
for k in SCALES:
    a = d1[d1.grp == 'paired'][k]; b = d1[d1.grp == 'R1-only'][k]
    u = stats.mannwhitneyu(a, b, alternative='two-sided')
    base.append(dict(scale=k, paired_mean=float(a.mean()), r1only_mean=float(b.mean()),
                     p=float(u.pvalue), cliffs=float(cliffs(a, b)), n_paired=len(a), n_r1only=len(b)))
for b_, a_ in zip(base, holm([b['p'] for b in base])): b_['holm_p'] = float(a_)
R['baseline_selection'] = base

# ---------- R2-only vs paired at R2 (late respondents) and R2-only vs R1-only ----------
late = []
for k in SCALES:
    a = d2[d2.grp == 'R2-only'][k]; b = d2[d2.grp == 'paired'][k]; c = d1[d1.grp == 'R1-only'][k]
    u1 = stats.mannwhitneyu(a, b, alternative='two-sided'); u2 = stats.mannwhitneyu(a, c, alternative='two-sided')
    late.append(dict(scale=k, r2only=float(a.mean()), paired_r2=float(b.mean()), r1only=float(c.mean()),
                     p_vs_paired=float(u1.pvalue), cliffs_vs_paired=float(cliffs(a, b)),
                     p_vs_r1only=float(u2.pvalue), cliffs_vs_r1only=float(cliffs(a, c))))
for l, a1, a2 in zip(late, holm([x['p_vs_paired'] for x in late]), holm([x['p_vs_r1only'] for x in late])):
    l['holm_vs_paired'] = float(a1); l['holm_vs_r1only'] = float(a2)
R['late_respondents'] = late

# response timing within R2: did R2-only answer later than paired?
d2['day'] = (d2.ts - d2.ts.min()).dt.total_seconds() / 86400
R['r2_timing'] = dict(paired_median_day=float(d2[d2.grp == 'paired'].day.median()),
                      r2only_median_day=float(d2[d2.grp == 'R2-only'].day.median()),
                      p=float(stats.mannwhitneyu(d2[d2.grp == 'paired'].day, d2[d2.grp == 'R2-only'].day).pvalue),
                      first_day_counts={g: int(((d2.grp == g) & (d2.day < 1)).sum()) for g in ['paired', 'R2-only']},
                      n={g: int((d2.grp == g).sum()) for g in ['paired', 'R2-only']})
# OV vs response day in R2
R['r2_timing']['rho_day_OV'] = spearman_ci(d2.day, d2.OV)

# ---------- cross-sectional round comparison (descriptive only) ----------
cross = []
for k in SCALES:
    a, b = d1[k], d2[k]
    cross.append(dict(scale=k, r1=float(a.mean()), r2=float(b.mean()), diff=float(b.mean() - a.mean()),
                      cliffs=float(cliffs(b, a))))
R['cross_sectional'] = cross

# ---------- correlations: within each round (replication logic) ----------
pairs = [('DEEP', 'OV'), ('DEEPc', 'OV'), ('SURF', 'OV'), ('CT', 'OV'), ('SR', 'OV'),
         ('LG', 'OV'), ('AC', 'OV'), ('LG', 'AC'), ('CT', 'SR'), ('DEEPc', 'LG')]
R['correlations'] = []
for a_, b_ in pairs:
    row = dict(x=a_, y=b_)
    for nm, d in [('R1', d1), ('R2', d2), ('S', stud_latest), ('S_first', stud_first)]:
        row[nm] = spearman_ci(d[a_], d[b_])
    R['correlations'].append(row)
# Holm within the student-level family
adj = holm([r['S']['p'] for r in R['correlations']])
for r, a in zip(R['correlations'], adj): r['S']['holm_p'] = float(a)

# Partial correlation DEEPc~OV controlling for CT and SR (student level), Spearman via ranks
import statsmodels.api as sm
def partial_spearman(d, x, y, z):
    rk = d[[x, y] + z].rank()
    rx = sm.OLS(rk[x], sm.add_constant(rk[z])).fit().resid
    ry = sm.OLS(rk[y], sm.add_constant(rk[z])).fit().resid
    return stats.pearsonr(rx, ry)
pr = partial_spearman(stud_latest, 'DEEPc', 'OV', ['CT', 'SR'])
R['partial_DEEPc_OV_ctrl_CT_SR'] = dict(r=float(pr[0]), p=float(pr[1]), n=len(stud_latest))
pr = partial_spearman(stud_latest, 'DEEPc', 'OV', ['LG'])
R['partial_DEEPc_OV_ctrl_LG'] = dict(r=float(pr[0]), p=float(pr[1]), n=len(stud_latest))

# full scale correlation matrix (student level)
keys = list(SCALES) + ['DEEPc']
R['corr_matrix'] = dict(keys=keys, rho=stud_latest[keys].corr(method='spearman').round(3).values.tolist())

# OV items vs every other item (student level), Spearman
R['ov_item_corr'] = []
for c in codes:
    if c.startswith('OV'): continue
    R['ov_item_corr'].append(dict(code=c, rho=float(stats.spearmanr(stud_latest[c], stud_latest.OV)[0])))

# ---------- tool-specific item OV2: who disagrees? ----------
for o in ['OV1', 'OV2', 'OV3']:
    v = stud_latest[o]; n = len(v)
    R.setdefault('ov_student', {})[o] = dict(n=n, agree=int((v >= 4).sum()), neutral=int((v == 3).sum()),
                                             disagree=int((v <= 2).sum()),
                                             agree_ci=[x * 100 for x in wilson(int((v >= 4).sum()), n)],
                                             mean=float(v.mean()), median=float(v.median()))
    vf = stud_first[o]
    R['ov_student'][o]['agree_first'] = int((vf >= 4).sum())

# ---------- power / minimum detectable effects ----------
from statsmodels.stats.power import TTestIndPower, TTestPower
R['power'] = dict(
    mde_independent_30_25=float(TTestIndPower().solve_power(nobs1=30, ratio=25 / 30, alpha=.05, power=.8)),
    mde_paired_13=float(TTestPower().solve_power(nobs=13, alpha=.05, power=.8)),
    mde_rho_n42=None)
# MDE for correlation with n=42 (Fisher z approx)
from scipy.optimize import brentq
def pw(r, n=42):
    z = np.arctanh(r) * np.sqrt(n - 3); return 1 - stats.norm.cdf(1.96 - z)
R['power']['mde_rho_n42'] = float(brentq(lambda r: pw(r) - .8, .01, .99))
R['power']['mde_rho_n25'] = float(brentq(lambda r: pw(r, 25) - .8, .01, .99))


# ---------- additions used in the chapter text ----------
# items of the deep-approach scale against OV, one row per student
R['deep_items_vs_OV'] = {c: {nm: spearman_ci(d[c], d.OV) for nm, d in [('R1', d1), ('R2', d2), ('S', stud_latest)]}
                         for c in ['LA1', 'LA3', 'LA5', 'LA7', 'LA9']}
# exploratory: feeling overwhelmed by nuance (LA10) vs "deliberation changed how I think" (OV2)
R['exploratory_LA10_OV2'] = {nm: spearman_ci(d.LA10, d.OV2) for nm, d in [('R1', d1), ('R2', d2), ('S', stud_latest)]}
# sensitivity: drop repeat respondents with near-constant answers (item SD < 0.5) in either round
low = set(d1[(d1.grp == 'paired') & (d1.sd_all < 0.5)].pid) | set(d2[(d2.grp == 'paired') & (d2.sd_all < 0.5)].pid)
keep = [p for p in P1.index if p not in low]
R['sensitivity_lowvar'] = dict(excluded=len(low), n=len(keep),
                               OV_p=float(stats.wilcoxon(np.round(P2.loc[keep, 'OV'] - P1.loc[keep, 'OV'], 8)).pvalue),
                               DEEP_p=float(stats.wilcoxon(np.round(P2.loc[keep, 'DEEP'] - P1.loc[keep, 'DEEP'], 8)).pvalue))

R['item_text'] = ITEMS
R['scale_def'] = {k: dict(label=v[0], items=v[1]) for k, v in SCALES.items()}

# per-student scale table for charts (pseudonymised, no emails)
R['students'] = [dict(pid=r.pid, grp=r.grp, rnd=r['round'], **{k: float(r[k]) for k in list(SCALES) + ['DEEPc']})
                 for _, r in pd.concat([d1, d2]).iterrows()]

json.dump(R, open(f'{OUT}/survey_results.json', 'w'), indent=1, default=float)
pd.concat([d1, d2]).to_csv(f'{OUT}/survey_clean_long.csv', index=False)
print('ok')
