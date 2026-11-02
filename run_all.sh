#!/usr/bin/env bash
# Regenerate all tables and figures in outputs/ from the shared data. Run from the repository root.
set -euo pipefail
python scripts/01_survey_analysis.py
python scripts/02_survey_tables.py
python scripts/03_bcause_scores.py
python scripts/04_dr_analysis.py
python scripts/05_make_figures.py
echo "Done: see outputs/"
