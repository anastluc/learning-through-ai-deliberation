# Data

All files are pseudonymised. No names, e-mail addresses, platform account ids or free-text answers of
students are included. Ids are consistent across sources: the same student has the same `S..` id in the
survey and (where their e-mail was recorded) in the Democratic Reflection files.

## `raw_pseudonymised/`

### `survey/survey_round1.csv`, `survey_round2.csv`
Smart Cities Module Learning Survey (Google Forms), round 1 (11–12 May 2026) and round 2 (10–24 June 2026).

| Column | Content |
|---|---|
| `respondent_id` | Pseudonymous student id (`S01` …), the same in both rounds |
| `timestamp_hour` | Submission time, truncated to the hour |
| 36 item columns | Original question headers and answer labels; item codes and scales in `reference/survey_codebook.csv` |

Round 1 has 31 rows, one of them blank (30 valid); round 2 has 25. 13 students answered both rounds (42 students).

### `democratic_reflection/experiment_<id>_cards.csv`
Reaction cards played during the AI-generated videos in the live session of 4 May 2026.
868 = Olympics, 869 = Housing, 870 = Parking.

| Column | Content |
|---|---|
| `timestamp`, `session_start`, `experiment_start` | Unix time (s) |
| `card` | `cKsN`: dimension K (1–5), side N (1 = first card of the pair, 2 = second); wording in `reference/dr_card_wording.csv` |
| `gradation` | Intensity; always 1 (not used by the platform in this session) |
| `hour`, `minute`, `second`, `video_time_s` | Position in the session clock. For 868 the video starts at 1250 s |
| `participant_id` | Pseudonymous platform account (`OLY-P01` …); one student may have rejoined under a new account |
| `participant_role` | PARTICIPANT or TESTER |
| `survey_respondent_id` | Survey id when the account's e-mail matched a survey respondent, else empty |

### `democratic_reflection/experiment_<id>_participants.csv`
Registered accounts with role, completion status and the platform's step log. `experiment_<id>_surveys.csv`
is the (empty) in-platform post-survey export, kept to document that no post-surveys were returned.

### `bcause/`
Empty on purpose. The BCause export (Firebase JSON per debate) holds display names that are students' real
names, account ids and profile-picture links, and the full text of every post. It is not shared. The posts are
represented by the post-level table `coding/bcause_post_codes.csv` (metadata and codes, no text). Researchers
who need the text can ask the authors; access depends on the students' consent.

## `coding/`

| File | Content |
|---|---|
| `bcause_post_codes.csv` | 219 BCause posts: date, debate, group, pseudonymous author, post type, what it was attached to, word count, and codes (role voice, engagement, reasons, evidence, counter-view, proposal; facilitation type for facilitator posts). Codebook: `codebook_bcause_posts.md` |
| `bcause_group_scores.csv` | One row per group: platform rubric scores (B, S), report rubric scores (R), post shares, attachment counts, and BCause reflection-button and heart counts |
| `report_coded_passages.csv` | 133 coded passages from the 16 group reports, with page, short quotation, strength, tool and coder note |
| `report_coding_matrix.csv` | Report × code (clear/weak), plus the draft chapter's provisional codes (`draft_*`) |
| `report_rubric_scores.csv` | Rubric R1–R6 per report with rationale, evidence pages and quotations, plus the draft score |
| `report_claim_checks.csv` | Claims in the reports about the platforms, checked against the logs |
| `codebook_reports.md` | The 23 + 1 report codes, the rubric anchors and decision rules |
| `dr_video_units.csv` | The three AI-generated videos segmented into argument units: timing, function, provenance in BCause (source groups and posts), and the cards played during each unit with over-representation tests |

All coding was done by one AI coder. Treat it as provisional until a second coder has coded a sample and
agreement is reported.

## `reference/`

`survey_codebook.csv` (item codes, sections, scales, response labels), `dr_card_wording.csv` (card code →
dimension and wording, per session).

## What is not included, and why

- Survey e-mail addresses and exact timestamps; DR names, e-mails and external ids; the browser date string.
- BCause export and post text (see above).
- The 16 student group reports (PDF) and their extracted text: they are student coursework with names.
  Short quotations used as coding evidence are in the coding files.
- The linkage of survey respondents to groups, which was made by matching names; it cannot be shared.
- Course materials (syllabus, assignment guidelines, report template) and the AI-generated videos.
- The re-identification key (written to `private/` by `scripts/00_pseudonymise.py`, never committed).

## Known issues

- **Survey: tied differences in the paired Wilcoxon tests.** Scale scores are means of 3–8 items, so equal
  changes (e.g. +0.333) differ by floating-point noise unless rounded. The October 2026 chapter draft did not
  round, so ties were broken at random and scipy used the exact no-ties null. `01_survey_analysis.py` now
  rounds the differences. Effect: OV (rating of the assignment and tools) Holm p = .041 instead of .021, and
  the deep-approach rise (+0.29) also survives Holm correction (p = .041, previously .059). The sensitivity test
  without the two near-constant respondents gives OV p = .012 (draft: .008). Bootstrap CIs can differ in the
  second decimal across library versions.
- **Survey timestamps** are truncated to the hour; within-round timing figures differ slightly from the
  originals (median response day in round 2: 5.0 vs 0.8 for repeat vs round-2-only respondents, as in the draft).
- **DR Olympics session**: 10 cards were played before the video started (before 1250 s) and are excluded.
- **BCause post codes**: three codes in the coder's working file were revised before the group table was made
  (H022, H070, O122); the shared table has the revised codes and reproduces the group table exactly.
