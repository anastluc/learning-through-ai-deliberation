"""Turn the original exports into the pseudonymised files in data/raw_pseudonymised/.

This script documents how the shared files were made. It needs the ORIGINAL exports, which are
not in this repository, and it writes the re-identification key to private/ (git-ignored).
Run from the repository root:

    python scripts/00_pseudonymise.py --orig /path/to/original_exports

Expected layout of --orig:
    survey/R1.csv, survey/R2.csv                 Google Forms exports, rounds 1 and 2
    dr/experiment_<id>_{cards,participants,surveys}_data.csv   Democratic Reflection exports (868, 869, 870)

What is removed or replaced
    Survey    e-mail address -> respondent id (S01, S02, ...); timestamp truncated to the hour.
    DR cards  e-mail, userExternalID and the browser date string are dropped; userID -> participant id
              (OLY-P01 ...); when the e-mail matches a survey respondent the respondent id is kept so the
              two sources can still be linked.
    DR participants  first name, last name, e-mail and externalId are dropped; id -> participant id.

The same e-mail always gets the same respondent id across the survey and the DR files. Ids are assigned
in order of first appearance (survey round 1 by time, then round 2, then DR files).
The BCause export is not processed here: see data/README.md.
"""
import argparse, csv, os
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument('--orig', required=True)
ap.add_argument('--out', default='data/raw_pseudonymised')
ap.add_argument('--key', default='private/pseudonym_key.csv')
a = ap.parse_args()

TOPIC = {868: 'Olympics', 869: 'Housing', 870: 'Parking'}
os.makedirs(f'{a.out}/survey', exist_ok=True)
os.makedirs(f'{a.out}/democratic_reflection', exist_ok=True)
os.makedirs(os.path.dirname(a.key), exist_ok=True)

key = {}  # normalised e-mail -> respondent id


def rid(email):
    if not isinstance(email, str) or not email.strip():
        return ''
    e = email.strip().lower()
    if e not in key:
        key[e] = f'S{len(key) + 1:02d}'
    return key[e]


# ------------------------------------------------------------------ survey
for rnd in ('R1', 'R2'):
    d = pd.read_csv(f'{a.orig}/survey/{rnd}.csv')
    ts = pd.to_datetime(d['Timestamp'], format='%d/%m/%Y %H:%M:%S')
    d = d.assign(_ts=ts).sort_values('_ts', kind='stable')
    out = d.drop(columns=['Timestamp', 'Email address', '_ts'])
    out.insert(0, 'respondent_id', [rid(e) for e in d['Email address']])
    out.insert(1, 'timestamp_hour', d['_ts'].dt.strftime('%Y-%m-%d %H:00'))
    out.to_csv(f'{a.out}/survey/survey_round{rnd[1]}.csv', index=False, quoting=csv.QUOTE_MINIMAL)

# ------------------------------------------------------------------ Democratic Reflection
for e, t in TOPIC.items():
    c = pd.read_csv(f'{a.orig}/dr/experiment_{e}_cards_data.csv', sep=';', dtype=str)
    p = pd.read_csv(f'{a.orig}/dr/experiment_{e}_participants_data.csv', sep=';', dtype=str)
    s = pd.read_csv(f'{a.orig}/dr/experiment_{e}_surveys_data.csv', sep=';', dtype=str)
    for df in (c, p, s):
        df.columns = [x.strip('﻿') for x in df.columns]
    # participant ids in order of registration
    pid = {u: f'{t[:3].upper()}-P{i + 1:02d}' for i, u in enumerate(p['id'])}
    for u in c['userID']:
        if u not in pid:
            pid[u] = f'{t[:3].upper()}-P{len(pid) + 1:02d}'
    role = dict(zip(p['id'], p['role']))
    c_out = pd.DataFrame({
        'experiment': e, 'topic': t, 'index': c['Index'],
        'timestamp': c['timestamp'], 'session_start': c['sessionStartTimestamp'],
        'experiment_start': c['experimentStartTimestamp'], 'card': c['card'], 'gradation': c['gradation'],
        'hour': c['hour'], 'minute': c['minute'], 'second': c['second'], 'video_time_s': c['videoTime'],
        'participant_id': c['userID'].map(pid), 'participant_role': c['userID'].map(role).fillna('UNKNOWN'),
        'survey_respondent_id': [rid(x) for x in c['email']],
    })
    c_out.to_csv(f'{a.out}/democratic_reflection/experiment_{e}_cards.csv', index=False)
    p_out = pd.DataFrame({
        'experiment': e, 'topic': t, 'participant_id': p['id'].map(pid), 'role': p['role'], 'status': p['status'],
        'survey_respondent_id': [rid(x) for x in p['email']], 'step_details': p['stepDetails'],
    })
    p_out.to_csv(f'{a.out}/democratic_reflection/experiment_{e}_participants.csv', index=False)
    s_cols = [x for x in s.columns if x not in ('email', 'externalUserID')]
    s[s_cols].to_csv(f'{a.out}/democratic_reflection/experiment_{e}_surveys.csv', index=False)

with open(a.key, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['email', 'respondent_id'])
    for k, v in key.items():
        w.writerow([k, v])
print(f'{len(key)} e-mail addresses pseudonymised; key written to {a.key} (do not commit).')
