"""Democratic Reflection live sessions (4 May 2026): card plays during the AI-generated videos.

Input : data/raw_pseudonymised/democratic_reflection/, data/reference/dr_card_wording.csv
Output: outputs/dr/ (overview, cards by wording, dimension balance, per-participant behaviour, 30-s timeline)

Card codes are cKsN: dimension K (1-5), side N (1 = first card of the pair, 2 = second card, which the
DR dashboard displays on its "negative" side). Experiment 868 = Olympics, 869 = Housing, 870 = Parking.
In the Olympics session the video started 1250 s after the session clock; the 10 cards played before
that are excluded as "not during the video" (the chapter's counts: 250 / 299 / 377).
"""
import os
import pandas as pd
from scipy import stats

IN = 'data/raw_pseudonymised/democratic_reflection'
OUT = 'outputs/dr'
os.makedirs(OUT, exist_ok=True)
TOPIC = {868: 'Olympics', 869: 'Housing', 870: 'Parking'}
OFFSET = {868: 1250, 869: 0, 870: 0}
W = pd.read_csv('data/reference/dr_card_wording.csv')

cards, parts = [], []
for e, t in TOPIC.items():
    c = pd.read_csv(f'{IN}/experiment_{e}_cards.csv')
    p = pd.read_csv(f'{IN}/experiment_{e}_participants.csv')
    s = pd.read_csv(f'{IN}/experiment_{e}_surveys.csv')
    c['t_video_s'] = c.video_time_s - OFFSET[e]
    c['during_video'] = c.t_video_s >= 0
    c['dimension_no'] = c.card.str[1].astype(int)
    c['side'] = c.card.str[-1].astype(int)
    p['n_cards'] = p.participant_id.map(c[c.during_video].participant_id.value_counts()).fillna(0).astype(int)
    p['survey_rows'] = len(s)
    cards.append(c); parts.append(p)
C = pd.concat(cards, ignore_index=True).merge(W[['experiment', 'card', 'dimension', 'wording']], on=['experiment', 'card'], how='left')
P = pd.concat(parts, ignore_index=True)
assert C.wording.notna().all()
V = C[C.during_video].copy()
print('cards during the video:', V.groupby('topic').size().to_dict())

# overview
ov = []
for e, t in TOPIC.items():
    v, p = V[V.experiment == e], P[P.experiment == e]
    pp = p[p.role == 'PARTICIPANT']
    per = v.groupby('participant_id').size()
    ov.append(dict(experiment=e, topic=t, registered_participants=len(pp), testers=int((p.role != 'PARTICIPANT').sum()),
                   complete=int((pp.status == 'COMPLETE').sum()), incomplete=int((pp.status == 'INCOMPLETE').sum()),
                   not_started=int((pp.status == 'NOT_STARTED').sum()),
                   cards_raw=int((C.experiment == e).sum()), cards_during_video=len(v), active_participants=v.participant_id.nunique(),
                   cards_per_active_mean=round(per.mean(), 2), cards_per_active_median=per.median(), cards_per_active_max=int(per.max()),
                   first_card_share=round((v.side == 1).mean(), 3),
                   linked_to_survey_respondent=int(v.survey_respondent_id.notna().sum()),
                   video_span_min=round(v.t_video_s.max() / 60, 2), post_surveys_returned=int(p.survey_rows.iloc[0])))
pd.DataFrame(ov).to_csv(f'{OUT}/overview.csv', index=False)

# cards by wording and dimension balance
byw = V.groupby(['topic', 'dimension_no', 'dimension', 'side', 'card', 'wording']).agg(
    cards=('card', 'size'), participants=('participant_id', 'nunique')).reset_index()
byw.to_csv(f'{OUT}/cards_by_wording.csv', index=False)
bal = byw.pivot_table(index=['topic', 'dimension_no', 'dimension'], columns='side', values='cards', fill_value=0).reset_index()
bal.columns = ['topic', 'dimension_no', 'dimension', 'first_card', 'second_card']
bal['total'] = bal.first_card + bal.second_card
bal['first_share'] = (bal.first_card / bal.total).round(3)
bal['binomial_p'] = [stats.binomtest(int(a), int(n)).pvalue for a, n in zip(bal.first_card, bal.total)]
bal.to_csv(f'{OUT}/dimension_balance.csv', index=False)
chi = pd.DataFrame([dict(topic=t, chi2=stats.chisquare(V[V.topic == t].card.value_counts()).statistic,
                         p=stats.chisquare(V[V.topic == t].card.value_counts()).pvalue, df=9) for t in TOPIC.values()])
chi.to_csv(f'{OUT}/uniformity_test.csv', index=False)

# per participant
pp = V.groupby(['topic', 'participant_id']).agg(cards=('card', 'size'), distinct_cards=('card', 'nunique'),
                                                 dimensions_used=('dimension_no', 'nunique'),
                                                 first_share=('side', lambda s: round((s == 1).mean(), 3)),
                                                 first_min=('t_video_s', lambda s: round(s.min() / 60, 2)),
                                                 last_min=('t_video_s', lambda s: round(s.max() / 60, 2))).reset_index()
pp.to_csv(f'{OUT}/per_participant.csv', index=False)

# timeline, 30-second bins of video time
V['bin_30s'] = (V.t_video_s // 30 * 30).astype(int)
tl = V.pivot_table(index='bin_30s', columns='topic', values='card', aggfunc='size', fill_value=0)
tl.to_csv(f'{OUT}/timeline_30s.csv')
V.to_csv(f'{OUT}/cards_during_video.csv', index=False)
print('wrote', OUT)
