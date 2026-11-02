# Codebook: BCause posts (`bcause_post_codes.csv`)

Coded 19 October 2026 by a single AI coder (Claude). These codes are provisional: no second coder has
coded them yet, so no inter-rater agreement is available. Unit: one post (position or argument) in the
three BCause debates (Olympics, Parking, Housing), 16 March to 18 June 2026. 219 posts; one further post
(H081, 4 July, a non-student account after the module) is excluded.

## Post metadata

| Column | Meaning |
|---|---|
| `post` | Post id: debate letter (H, O, P) + running number in date order |
| `date` | Posting date (Europe/Rome) |
| `debate` | Olympics, Parking or Housing |
| `group` | Group of the author (G01–G17); G01, G14 and G16 are the facilitator groups |
| `author` | Pseudonymous author within the group (`G05 member A`), lettered by first post |
| `kind` | Position (top-level node), Pro argument (BCause "supporting") or Con argument ("opposing") |
| `attached_to` | What the post sits under: a facilitator's question or post, another group's post, the author's own group's post, or top level (a new position) |
| `attached_group` | Group whose post it is attached to |
| `nested` | Yes if posted as a reply to another argument rather than under a position |
| `words` | Word count of the post |
| `note` | Coder's note (names of students replaced by group labels) |

The full text of the posts is not part of the shared data (see `data/README.md`).

## Codes for debating-group posts

| Column | Code | Levels |
|---|---|---|
| `role_voice` | RV | Explicit role voice (speaks as the role) · Role-consistent (content fits the role, no explicit voice) · Not role-identifiable · Out of role |
| `engagement` | EN | None (stand-alone, or answers a facilitator prompt only) · Generic (refers to others in general: "as mentioned by our peers") · Specific (agrees with, extends or contests an identifiable argument of another group) · Integrates (concedes another group's specific point and changes or combines its own proposal with it) |
| `engages` | — | Groups engaged at Specific or Integrates |
| `reasons` | RS | Yes = gives reasons; No = bare assertion or question |
| `evidence` | EV | None · Unsourced facts (specific facts, figures or cases without a traceable source) · Sourced (named or traceable source) |
| `counter_view` | CA | Yes = acknowledges or answers a counter-view, or states a limit of its own position |
| `proposal` | PR | None · Direction (general direction) · Concrete (concrete measure) · Concrete + actors + conflicts (concrete measure, who implements it, and how conflicting interests or costs are handled) |

## Codes for facilitator posts (`facilitation`)

Trade-off question · Open question · Leading question (presupposes an answer) · Statement for reflection ·
Synthesis (connects contributions) · Follow-up to a post (follow-up or challenge to a specific post) ·
Options toward a decision · Information input · Argues a position. Facilitator posts also carry `evidence`.

## From post codes to group scores (`bcause_group_scores.csv`)

The report rubric (C1–C6, see `codebook_reports.md`) was applied to each group's posts with fixed rules.
C5 (reflection on the tools) has no equivalent in posts. `scripts/03_bcause_scores.py` recomputes every
column of the group table from the post codes.

**Debating groups (B1–B6, as specified)**

- B1 Role coherence: 3 if at least half the posts are role-voiced or role-consistent, none is out of role, and at least one role-voiced post answers a counter-view; 2 if at least half are role-voiced/consistent and at most one is out of role; else 1.
- B2 Learning from diversity: highest engagement level reached by any post (0–3).
- B3 Argument construction: 3 if reasons in ≥75% of posts, facts or sources in ≥1/3 and counter-views in ≥25%; 2 if reasons in ≥50% and (facts ≥15% or counter-views ≥15%); else 1.
- B4 Action orientation: highest proposal level reached by any post (0–3).
- B6 Sources: 3 if ≥3 sourced posts; 2 if ≥1; 1 if any unsourced facts; else 0.

**Stricter variant (S1–S6)**: S1 = 2 when B1 = 3 but under a third of posts are explicitly role-voiced;
S2 = 3 if ≥2 integrating posts, 2 if ≥2 specific-or-integrating posts, 1 if any engagement; S3 thresholds
85% / 43% / 35% (3) and 60% / 25% / 25% (2); S4 = 3 if ≥2 full proposals, 2 if ≥2 concrete-or-full, 1 if any
proposal; S6 = 3 if ≥3 sourced posts and they are ≥20% of posts.

**Facilitator groups (B1–B6)**: B1 3 if no leading questions or argued positions and ≥1 synthesis or options
post, 2 if at most two leading/argued posts, else 1; B2 3 if ≥2 synthesis/options and ≥2 follow-ups, 2 if
any of either, else 1; B3 3 if a trade-off or options post, an information input and a follow-up, 2 if a
trade-off/options post or a follow-up, else 1; B4 3 if an options post and a follow-up, 2 if an options post
or a question that asks for measures (judged from the text), else 1; B6 as for debating groups.

`R1`–`R6` and `R_total` (C1–C4 + C6) in the group table are the report rubric scores from
`report_rubric_scores.csv`.
