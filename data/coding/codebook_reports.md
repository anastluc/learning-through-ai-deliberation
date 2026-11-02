# Codebook: group reports (`report_*.csv`)

Coded 17 October 2026 by a single AI coder (Claude) from the 16 group reports (group G04 submitted none).
Provisional: a second, human coder has not yet coded the reports. The draft chapter's earlier coding is kept
in the `draft_*` columns of `report_coding_matrix.csv` and `draft_score` in `report_rubric_scores.csv` for comparison.

## Unit and attributes

Unit = a passage of a report. A report *has* a code when at least one passage is coded (`report_coding_matrix.csv`:
`clear` if any passage states the content explicitly, `weak` if only implied, partial or borderline).
Each passage (`report_coded_passages.csv`) records the PDF page, a short quotation, the strength, the coder's note and
the part of the loop it is about (`tool`): BCause, BCause-AI, DR, Video, General (BCause-AI = synopsis, analytics/cluster maps, conflict detection; DR = Democratic Reflection live session/dashboard; Video = AI-generated video).

AIM is a supplementary code added to test the chapter's claims about the visibility of the AI features.

## Codes

| Code | Family | Name | Definition |
|---|---|---|---|
| PAR | A Move 1 – interaction on BCause | Parallel monologues / defensive posting early on | The report says participants (incl. the group itself) posted their own positions without engaging others, restated their own claims, replied only to defend, or that early participation was sparse. |
| BIN | A Move 1 – interaction on BCause | Pro/con structure constrains open questions or in-between positions | The report says the binary pro/con (support/oppose) structure of BCause hindered open questions, intermediate positions or compromise, or pushed participants into opposing camps. |
| ECH | A Move 1 – interaction on BCause | Echo chamber or dominant position visible | The report says the discussion or map showed one-sided dominance, echo chambers, or one topic/position crowding out others. |
| LNG | A Move 1 – interaction on BCause | Long posts slowed exchange | The report says the length or density of posts made reading and replying harder. |
| FAC | A Move 1 – interaction on BCause | Facilitator prompts changed the course of the debate | The report attributes a change in the direction or level of interaction of the debate to facilitator prompts or questions (facilitator groups describing their own prompts included). |
| PART | A Move 1 – interaction on BCause | Participation fell or was uneven | The report says participation declined over time or was uneven across groups, members or topics. |
| RTN | B Role | Role in tension with own views | The report describes a conflict between members’ own views (or a facilitator’s own opinions) and the position the role required. |
| RLE | B Role | Role grounded in lived experience or primary research | The group built its role on members’ own current situation or on primary data it collected (interviews, surveys). Future or hypothetical situations do not count. |
| POS | C Learning from diversity | Position changed in response to another group | The report names a specific change in the group’s own position or proposal and attributes it to another group’s contribution. Generic statements (“we learned from others”) and changes in argumentative style only (see EVI/EMO) are not coded. |
| STE | C Learning from diversity | Stereotype of a role broken | The report explicitly names a stereotype, archetype or reputation of a stakeholder role (another role or the group’s own, as seen by others) and describes it being challenged in the deliberation. |
| PSD | C Learning from diversity | Agreement on the problem, disagreement on solutions | The report states that participants converged on the diagnosis but diverged on solutions. |
| EVI | D Argument and evidence | Shift toward documented evidence | The report says the group (or, for facilitators, the participants) moved toward data, sources or documented evidence during the deliberation. |
| EMO | D Argument and evidence | Shift toward emotional or relatable framing | The report says the group moved toward narrative, emotional, empathetic or relatable framing in order to persuade. |
| EMD | D Argument and evidence | Observed that emotion drove engagement more than data | The report observes that emotional or experiential contributions drew more uptake or persuasion than data-based ones. |
| DRD | E Reading of Democratic Reflection | DR read as a diagnosis that changed strategy | The report says the DR results changed how the group argued or acted afterwards. |
| DRC | E Reading of Democratic Reflection | DR read as confirming existing consensus | The report reads the DR results as confirming agreement already present on BCause. |
| DRN | E Reading of Democratic Reflection | DR read as having no clear direction / not used further | The report says the DR results gave no clear direction or were not used further. |
| DRS | E Reading of Democratic Reflection | DR judged shallow without BCause | The report judges the live reactions superficial unless paired with the asynchronous argument map. |
| DRB | E Reading of Democratic Reflection | DR helped step back to reasons | The report says the DR session helped participants step back and reflect on the reasons behind positions. |
| DRR | E Reading of Democratic Reflection | DR card category read as rejection (dashboard valence) | The report reads a DR card category as rejection/approval on the basis of the dashboard’s positive/negative labels where the cards were two opposing stances (e.g. the parking “solutions” pair). |
| INS | F Limits and action | No institutional audience / simulation limits | The report says that the absence of real decision-makers or stakes, or the simulated nature of the exercise, limited the deliberation. |
| DIG | F Limits and action | Digital divide or missing voices | The report says some people would be excluded by the digital format, or that relevant voices were absent. |
| RED | F Limits and action | Proposed platform redesign | The report proposes concrete changes to BCause or Democratic Reflection. Clear when part of the envisaged action or a dedicated section; weak when a passing suggestion. |
| AIM | S Supplementary (added in this re-coding) | Mentions an AI feature of the tools | The report mentions or uses an AI feature: BCause synopsis/summary, analytics or cluster maps, conflict detection, the AI-generated video, or the DR theme analysis. The note says which feature and whether the report recognises it as AI. |

## Rubric (0–3 per criterion)

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **R1 Role coherence** | Not addressed | Role asserted, no reflection | Role described with examples of keeping or adapting it | Critical reflection on tensions within the role, with specific episodes |
| **R2 Learning from diversity** | Absent | Generic statements about other views | Specific opposing positions engaged with | A change in the group’s understanding or position attributed to others, with specifics |
| **R3 Argument construction** | Absent | Arguing described in general | Specific strategies and types of evidence | Reflective account of how arguments were built, defended and revised, incl. counter-arguments (for facilitators: observed in others) |
| **R4 Action orientation** | No action | Vague intention | Concrete action addressing diverse roles or institutions | Concrete, feasible action addressing diverse roles and institutions, and how conflicts are handled |
| **R5 Reflection on the tools** | None | Descriptive | Evaluates strengths and limits | Evaluates with evidence from platform data and draws design implications |
| **R6 Use of literature** | None | Few or grey sources only | Several scholarly sources | Scholarly sources used to frame the reflection and the action |

R1–R4 follow the four reflection dimensions of the course's report template; R5–R6 were added for the tools and the literature.

### Decision rules (fixed before scoring)

- Score the highest level for which the report gives explicit evidence; when between two levels, take the lower.
- R1/R3 for facilitator groups refer to the facilitator role and to arguments observed in others.
- R2 = 3 requires a change attributed to a named other group or a specific contribution, not to “others” in general.
- R3 = 3 requires an account of revision AND of at least one counter-argument met in the debate.
- R4 = 3 requires (a) concrete measures, (b) named institutions with roles, and (c) an explicit account of how conflicting interests are handled. An action that only changes the group’s own argumentation scores at most 2.
- R5 = 3 requires evidence drawn from platform outputs (counts, maps, dashboards, logs) AND design implications.
- R6 = 3 requires scholarly sources framing both the reflection on the deliberation and the action; one scholarly source among grey sources scores 1.

## Claim checks

`report_claim_checks.csv` lists claims in the reports about what happened on the platforms, checked against the BCause
and Democratic Reflection logs. `result` is one of: consistent, partly consistent, not supported, cannot be verified,
interpretation beyond the data, not checked.
