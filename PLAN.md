# Plan: Why did Juventus concede so few goals? (Serie A 2015/16)

**Status:** approved on 2026-11-18 (D9) · **Last updated:** 2026-11-18
Decisions and their reasons are logged in [DECISIONS.md](DECISIONS.md).

## 1. Goal

Answer **one** football question with data, on **one page**:
Question → Hypothesis → Verification with data → Implication.

- Each chart has one message that anyone can understand in 10 seconds.
- The repo can be explained in 1 minute (non-technical) and in 5 minutes (technical).
- Main readers: non-technical people (for example HR and business consultants). Technical detail stays in the repo.

## 2. The one-page story (draft)

- **Question:** Why did Juventus concede so few goals in Serie A 2015/16?
- **Hypothesis:** Juventus allowed the fewest and weakest chances in the league, and their goals conceded were about what xG predicted. So the main reason was how they defended, not their goalkeeper (Buffon) or luck.
- **Verification:**
  0. Data checks (section 5), including: goals counted from the events match the final scores.
  1. How many chances: shots conceded per match, for all 20 teams.
  2. How good the chances were: xG per shot conceded, and xG conceded per match, for all 20 teams.
  3. Goals conceded vs. xG conceded, with a replay of the season to see whether the gap could be chance.
  All the rules for judging the results are fixed **before** we look at the results (section 6).
- **Implication** (written after the results, D24): Judge a defence by the quality of the chances it allows, not only by how many shots or goals it concedes. Before explaining a headline number, break it into its drivers: Juventus's record came from very few shots and the weakest chances in the league, and luck is not needed to explain it.

> **xG (expected goals):** for each shot, the probability that it becomes a goal, from StatsBomb's model (based on many similar past shots). A team's **xG conceded** is the sum over all the shots it faced.

## 3. Scope

- **In:** Serie A 2015/16 (all 20 teams, for comparison); StatsBomb open event data; Python (pandas, numpy, matplotlib, pytest for a few tests, and Python-Markdown for the PDF summaries).
- **Out, for now:** other seasons and leagues; player-position ("360") data, which this season does not have; machine learning; a web app (maybe in January, only if there is time and I agree).

## 4. Deliverables

- Numbered scripts in `src/` (`01_download`, `02_checks`, `03_metrics`, `04_charts`, `05_report`, `06_pdf`), all run by **one command** (`run_all.py`).
- `results/`: a results table written by the scripts. **Every number in the README and in the one-page summary comes from this table.** No number is typed by hand.
- 3 charts: one message each, the title states the finding, labelled axes with units, readable on a phone. Chart text is in English; the Japanese summary uses the same charts (proposal). Chosen in D21: (1) how many chances each team allowed and how good they were, (2) goals minus xG for all 20 teams, (3) the replays of Juventus's season. Each chart carries the StatsBomb logo (D22). Written to `results/charts/`.
- `README.md` (English): the story, the charts, data checks, limitations, how to rerun, how this was built (AI note, see D7), and data credit to StatsBomb with their logo. Written by `src/05_report.py` from a template in `templates/`, with every number filled in from `results/` (D23).
- One-page summary in English and Japanese (`docs/summary_en.md`, `docs/summary_ja.md`; Markdown, also exported as PDF). Written the same way as the README (D23), and printed to one A4 page each by `src/06_pdf.py` (D25).
- Reproducible: `requirements.txt`, a fixed random seed, the original data files cached locally (**not** committed to git) with a fingerprint of each file, so anyone can check that they have the same data (D12).
- A few small automatic tests for the key calculations (D11).

## 5. Data checks (confirmed on 2026-11-18, D13)

1. Find "Serie A 2015/2016" in `competitions.json` by name. Do not hard-code the ids.
2. 380 matches, 20 teams, 38 matches per team.
3. Every match has an events file, and no match appears twice.
4. Goals counted from the events (shots with outcome "Goal", plus own goals) = the final score, in every match.
5. The league table rebuilt from the match scores = the official final table from the Lega Serie A website. The official table is typed in by hand, so it is checked in two ways: its own totals must add up (for example, total goals scored = total goals conceded), and it must agree with a second copy typed in from RSSSF (D14). The sources and the date they were read are saved with the tables.
6. Every shot has an xG value between 0 and 1.
7. Juventus's goals conceded from the events = the official figure from check 5.

If a check fails, we stop, find the reason and write it down in DECISIONS.md before moving on. No silent fixes.

## 6. Analysis rules (fixed on 2026-11-18, before any result was calculated)

These rules were fixed before any shot, xG or goal number was calculated for the analysis, so the results cannot change them (D17–D20). If a rule turns out to be wrong after we see the results, we keep the planned version, show the new version next to it, and log the reason in DECISIONS.md.

**What is compared.** All 20 teams, 38 matches each. "Conceded" means the shots, xG and goals of a team's opponents.
- Penalties are left out of all the main numbers (shots, xG and goals): a penalty is a rare, very high-xG chance, so a few kicks could decide the result. The same numbers with penalties are shown as a check (D18).
- Own goals are not shots and have no xG, so they are left out of the goals compared with xG and counted separately (D18).

**Measures**, for every team:
1. Shots conceded per match.
2. xG per shot conceded: how good the average chance allowed was.
3. xG conceded per match: the number and the quality of the chances together.
4. Goals conceded vs. xG conceded, and goals minus xG.
5. Shots and xG conceded per 100 opponent possessions. A possession is StatsBomb's sequence of play controlled by one team, and every possession counts once, however short (D19).

**How each part of the hypothesis is judged.** Only Juventus is tested; the other 19 teams are the comparison.
- "The fewest chances": Juventus is 1st (lowest) of the 20 teams in measure 1.
- "The weakest chances": Juventus is 1st (lowest) of the 20 teams in measure 2.
- If Juventus is not 1st, we give its rank as it is and say that this part of the hypothesis is not supported. We do not reword the hypothesis afterwards. A tie for first place counts as first, and we say that it is shared.
- "Goals about what xG predicted" (D17): replay the season 10,000 times with a fixed random seed. In each replay, every non-penalty shot that Juventus conceded becomes a goal with a probability equal to its xG. If fewer than 5% of the replays end with as few goals as Juventus really conceded (or fewer), the goals were "far fewer than xG": the keeper or luck also mattered. Otherwise the gap is within what chance can explain, which does not prove that there was no luck (section 8).
- Possession (D19): if Juventus is also 1st on both measures in 5, possession does not explain the low numbers. If not, we give the ranks and say that possession explains part of them.

## 7. Milestones

Time budget: about 10 hours per week. Extra time is used to finish **earlier**, not to add scope.

| # | Milestone | Output | Target | Status |
|---|---|---|---|---|
| M0 | Kickoff and plan | PLAN.md, DECISIONS.md | 2026-11-18 | done |
| M1 | Setup | local git repo, virtual environment, `requirements.txt`, `.gitignore`; git name and email for public commits; StatsBomb user agreement read and its requests listed | 2026-11-22 | done (2026-11-18) |
| M2 | Data and checks | registration with StatsBomb first (by me, see `docs/statsbomb_terms.md`); data downloaded and cached locally; data checks script and its results | 2026-11-29 | done (2026-11-18): all checks passed, see `results/data_checks.csv` |
| M3 | Metrics | O1–O4 decided first; shots, xG and goals − xG for all 20 teams | 2026-12-06 | done (2026-11-18): rules committed first (D20), then the results: `results/hypothesis_tests.csv` |
| M4 | Charts and results table → **MVP** | 3 charts and the results table, from one command | 2026-12-13 | done (2026-11-18): `results/charts/` and `results/*.csv`, all from `run_all.py` |
| M5 | Write-up and publish | README; one-page summary (EN/JA); make the GitHub repository public **only after my explicit OK** (it is private until then, D16) | about 2026-12-20 | done (2026-11-18): README, one-page summaries and their PDFs, all written by `run_all.py` (D23–D25); the repository is public (D16) |
| M6 | Polish and talk track | 1-minute (Japanese and English) and 5-minute explanations; likely questions and answers; a link from the project to each kind of job I apply for; 3 practice interviews; a 10-second test of chart 1 with real readers (D26). The talk track itself is kept private | 2026-12-13 (was 2027-01-31, D26) | in progress (2026-11-18) |
| — | February 2027 | no new work (freeze) | — | — |

## 8. Risks and limitations

- **One season, one data provider.** xG comes from StatsBomb's model, not ours.
- **Goalkeeper skill vs. luck cannot be fully separated.** xG measures the chance at the moment of the shot, not how well the shot was struck.
- **No big gap is not proof of no luck.** If goals conceded are close to xG, it only means the gap is within what chance can explain.
- **Possession** may explain fewer shots conceded (O2).
- **Event data only:** we see the players without the ball only when a shot is taken (StatsBomb's "freeze frame", not always every player). Corrected on 2026-11-19 (D28).
- **Data terms:** the data is provided "as is" and StatsBomb can stop the service at any time. Raw data must not be shared (see `docs/statsbomb_terms.md`).
- **Explaining AI-written code:** each step ends with a short walk-through of the key lines, so I can explain every calculation.
- **Time:** other commitments in January–February come first, so the MVP is small and planned for mid-December.

## 9. How we work

- Small steps. Each step ends with a 3-line summary, what the output means, and a walk-through of the key lines.
- I decide the theme, the scope and the deliverables. Pushing to GitHub, making the repo public and deleting files need my explicit OK.
- Every decision goes into DECISIONS.md.
