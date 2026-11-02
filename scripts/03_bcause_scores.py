"""Group-level BCause scores and indicators from the post-level codes.

Input : data/coding/bcause_post_codes.csv (one row per post, single AI coder, 19 Oct 2026)
        data/coding/bcause_group_scores.csv (the shared group table, used here as a check)
Output: outputs/bcause/group_scores_recomputed.csv, edges.csv, timeline_weekly.csv
Rules : the same fixed rules that produced the shared group table (see data/coding/codebook_bcause_posts.md).
        Facilitator criterion C4 used the post text (does a question ask for measures?), which is not shared,
        so it is copied from the shared table rather than recomputed.
"""
import os, datetime as dt
from collections import Counter
import pandas as pd

OUT = 'outputs/bcause'
os.makedirs(OUT, exist_ok=True)
P = pd.read_csv('data/coding/bcause_post_codes.csv', keep_default_na=False)
SHARED = pd.read_csv('data/coding/bcause_group_scores.csv')

RV = {'Explicit role voice': 'E', 'Role-consistent': 'C', 'Not role-identifiable': 'N', 'Out of role': 'O'}
EN = {'None': 0, 'Generic': 1, 'Specific': 2, 'Integrates': 3}
EV = {'None': 0, 'Unsourced facts': 1, 'Sourced': 2}
PR = {'None': 0, 'Direction': 1, 'Concrete': 2, 'Concrete + actors + conflicts': 3}
FT = {'Trade-off question': 'QT', 'Open question': 'Q', 'Leading question': 'QL', 'Statement for reflection': 'P',
      'Synthesis': 'S', 'Follow-up to a post': 'C', 'Options toward a decision': 'O', 'Information input': 'I',
      'Argues a position': 'A'}
ADDR = {'Facilitator question or post': 'facilitator', 'Another group': 'other group', 'Own group': 'own group',
        'Top level (new position)': 'none'}


def debating(ps):
    n = len(ps)
    rv = Counter(RV[p.role_voice] for p in ps)
    en = [EN[p.engagement] for p in ps]; ev = [EV[p.evidence] for p in ps]; pr = [PR[p.proposal] for p in ps]
    rs = [p.reasons == 'Yes' for p in ps]; ca = [p.counter_view == 'Yes' for p in ps]
    share_role = (rv['E'] + rv['C']) / n
    role_ca = any(RV[p.role_voice] in 'EC' and c for p, c in zip(ps, ca))
    b1 = 3 if share_role >= .5 and rv['O'] == 0 and role_ca else 2 if share_role >= .5 and rv['O'] <= 1 else 1
    s_rs, s_ev1, s_ca = sum(rs) / n, sum(e >= 1 for e in ev) / n, sum(ca) / n
    b3 = 3 if s_rs >= .75 and s_ev1 >= 1 / 3 and s_ca >= .25 else 2 if s_rs >= .5 and (s_ev1 >= .15 or s_ca >= .15) else 1
    k = sum(e == 2 for e in ev)
    b6 = 3 if k >= 3 else 2 if k >= 1 else 1 if any(e == 1 for e in ev) else 0
    sc = dict(B1=b1, B2=max(en), B3=b3, B4=max(pr), B6=b6)
    # stricter variant (S1-S6)
    c_en, c_pr = Counter(en), Counter(pr)
    st = dict(S1=2 if (b1 == 3 and rv['E'] / n < 1 / 3) else b1,
              S2=3 if c_en[3] >= 2 else 2 if c_en[3] + c_en[2] >= 2 else 1 if c_en[1] + c_en[2] + c_en[3] >= 1 else 0,
              S3=3 if s_rs >= .85 and s_ev1 >= .43 and s_ca >= .35 else 2 if s_rs >= .6 and (s_ev1 >= .25 or s_ca >= .25) else 1,
              S4=3 if c_pr[3] >= 2 else 2 if c_pr[3] + c_pr[2] >= 2 else 1 if n - c_pr[0] >= 1 else 0,
              S6=3 if k >= 3 and k / n >= .2 else 2 if k >= 1 else 1 if s_ev1 > 0 else 0)
    ind = dict(rv_E=rv['E'], rv_C=rv['C'], rv_N=rv['N'], rv_O=rv['O'], role_share=round(share_role, 3),
               explicit_share=round(rv['E'] / n, 3), engage_share=round(sum(e >= 2 for e in en) / n, 3),
               engage_n=sum(e >= 2 for e in en), integrate_n=sum(e == 3 for e in en), reasons_share=round(s_rs, 3),
               evidence_share=round(s_ev1, 3), sourced_n=k, sourced_share=round(k / n, 3), counter_share=round(s_ca, 3),
               concrete_n=sum(x >= 2 for x in pr), concrete_share=round(sum(x >= 2 for x in pr) / n, 3),
               full_proposal_n=sum(x == 3 for x in pr),
               engaged_groups=', '.join(sorted({t.strip() for p in ps for t in p.engages.split(',') if t.strip()})))
    return sc, st, ind


def facilitators(ps, shared_b4):
    t = Counter(FT[p.facilitation] for p in ps)
    lead, synth = t['QL'] + t['A'], t['S'] + t['O']
    f1 = 3 if lead == 0 and synth >= 1 else 2 if lead <= 2 else 1
    f2 = 3 if synth >= 2 and t['C'] >= 2 else 2 if (synth >= 1 or t['C'] >= 1) else 1
    f3 = 3 if (t['QT'] + t['O'] >= 1 and t['I'] >= 1 and t['C'] >= 1) else 2 if (t['QT'] + t['O'] >= 1 or t['C'] >= 1) else 1
    k = sum(EV[p.evidence] == 2 for p in ps)
    f6 = 3 if k >= 3 else 2 if k >= 1 else 1 if any(EV[p.evidence] == 1 for p in ps) else 0
    sc = dict(B1=f1, B2=f2, B3=f3, B4=int(shared_b4), B6=f6)
    return sc, {f'S{k[1]}': v for k, v in sc.items()}, {**{f'f_{k}': t.get(k, 0) for k in FT.values()}, 'sourced_n': k}


rows = []
for g, gp in P.groupby('group'):
    ps = list(gp.itertuples())
    sh = SHARED.set_index('group').loc[g]
    fac = sh['kind'] == 'Facilitators'
    sc, st, ind = facilitators(ps, sh['B4']) if fac else debating(ps)
    addr = Counter(ADDR[p.attached_to] for p in ps)
    rows.append(dict(group=g, debate=ps[0].debate, posts=len(ps), words=int(gp.words.sum()), first=gp.date.min(), last=gp.date.max(),
                     **sc, B_total=sum(sc.values()), **st, S_total=sum(st.values()),
                     to_facilitator=addr['facilitator'], to_other=addr['other group'], to_own=addr['own group'],
                     top_level=addr['none'], **ind))
R = pd.DataFrame(rows)
R.to_csv(f'{OUT}/group_scores_recomputed.csv', index=False)

# check against the shared table
cols = [c for c in R.columns if c in SHARED.columns and c not in ('group', 'debate')]
A, B = R.set_index('group')[cols], SHARED.set_index('group')[cols]
bad = []
for g in A.index:
    for c in cols:
        a, b = A.at[g, c], B.at[g, c]
        if pd.isna(a) and pd.isna(b):
            continue
        try:
            same = abs(float(a) - float(b)) < 1e-3
        except (TypeError, ValueError):
            same = str(a) == str(b)
        if not same:
            bad.append((g, c, a, b))
print(f'{len(A)} groups, {len(cols)} columns compared; mismatches: {len(bad)}')
for b in bad:
    print('  ', b)

# who took up whose argument (debating groups, engagement Specific or Integrates)
E = []
for p in P.itertuples():
    if p.engagement in ('Specific', 'Integrates'):
        for t in [x.strip() for x in p.engages.split(',') if x.strip()]:
            E.append(dict(debate=p.debate, from_group=p.group, to_group=t,
                          type='integrates' if p.engagement == 'Integrates' else 'engages'))
pd.DataFrame(E).groupby(['debate', 'from_group', 'to_group', 'type']).size().rename('posts').reset_index() \
    .to_csv(f'{OUT}/edges.csv', index=False)

# posts per week (weeks from Monday 16 March 2026)
start = dt.date(2026, 3, 16)
P['week'] = [(dt.date.fromisoformat(d) - start).days // 7 for d in P.date]
P['facilitator'] = P.role_voice == 'Facilitator'
T = P.groupby(['debate', 'week']).agg(group_posts=('facilitator', lambda s: int((~s).sum())),
                                      facilitator_posts=('facilitator', 'sum')).reset_index()
T['week_start'] = [str(start + dt.timedelta(weeks=int(w))) for w in T.week]
T['posts'] = T.group_posts + T.facilitator_posts
T.to_csv(f'{OUT}/timeline_weekly.csv', index=False)
print('wrote', OUT)
