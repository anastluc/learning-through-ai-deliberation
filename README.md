# A deliberative loop for AI-supported collective sensemaking — data and code

Data and analysis code for the chapter *A deliberative loop for AI-supported collective sensemaking*
(G. Concilio, L. Anastasiou, F. De Ambrosis, A. De Liddo), submitted to the *Research Handbook on AI and the
Future of Education*.

The study follows the Smart Cities and Urban Innovation module at Politecnico di Milano (spring 2026), where
student groups role-played stakeholders in three Milan controversies (2026 Winter Olympics, short-term
rentals and housing, illegal parking). The deliberative loop had four moves: argument mapping on BCause,
AI-generated video synopses of each debate, a live Democratic Reflection session in which students reacted
to the videos with cards, and a return to BCause.

## Contents

```
data/
  raw_pseudonymised/
    survey/                  learning survey, rounds 1 and 2
    democratic_reflection/   card plays, participants, (empty) post-surveys for sessions 868-870
    bcause/                  intentionally empty: see data/README.md
  coding/                    post-level and group-level BCause codes, report coding, video units, codebooks
  reference/                 survey codebook, DR card wording
scripts/
  00_pseudonymise.py         how the shared files were made from the original exports (needs the originals)
  01_survey_analysis.py      survey re-analysis: reliability, paired change, Holm correction, correlations
  02_survey_tables.py        survey tables used by the figures
  03_bcause_scores.py        group scores from post codes (and a check against the shared group table)
  04_dr_analysis.py          Democratic Reflection: card counts, balance tests, per-participant, timeline
  05_make_figures.py         chapter figures (5-A to 5-G) and the DR timeline
run_all.sh
```

`data/README.md` describes every file, what was removed and why, and known issues.

## Reproducing

Python 3.10 or later.

```
pip install -r requirements.txt
bash run_all.sh            # writes outputs/ (tables and figures); takes about 2 minutes
```

`00_pseudonymise.py` is not run by `run_all.sh`: it documents the pseudonymisation and needs the original
exports, which are not shared.

## Pseudonymisation

E-mail addresses were replaced by ids (`S01` …) consistent across the survey and Democratic Reflection
files; names, external ids and browser date strings were dropped; survey timestamps were truncated to the
hour; student names inside coder notes were replaced by group labels (`[G15 member]`). The BCause export and
the student reports are not shared. The re-identification key is held by the authors.

## Status of the coding

The BCause post codes and the report coding were produced by a single AI coder (Claude, October 2026) and are
provisional. Inter-rater agreement with a human coder has not yet been established.

## Licence

Code: MIT (`LICENSE`). Data and codebooks: CC BY 4.0 (`LICENSE-DATA`).

## Citation

See `CITATION.cff`.
