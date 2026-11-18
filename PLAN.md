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
  1. Shots conceded per match, for all 20 teams.
  2. xG conceded per match, for all 20 teams.
  3. Goals conceded vs. xG conceded. The rule for "far fewer goals than xG" is fixed **before** we look at the results (section 6, O1).
- **Implication:** written after the results.
  - If the hypothesis holds: judge a defence by the chances it allows, not only by its goals conceded.
  - If it fails: even a great number can hide luck, so check what drives it.

> **xG (expected goals):** for each shot, the probability that it becomes a goal, from StatsBomb's model (based on many similar past shots). A team's **xG conceded** is the sum over all the shots it faced.

## 3. Scope

- **In:** Serie A 2015/16 (all 20 teams, for comparison); StatsBomb open event data; Python (pandas, statsbombpy, mplsoccer, matplotlib).
- **Out, for now:** other seasons and leagues; player-position ("360") data, which this season does not have; machine learning; a web app (maybe in January, only if there is time and I agree).

## 4. Deliverables

- Numbered scripts in `src/` (`01_download`, `02_checks`, `03_metrics`, `04_charts`), all run by **one command**.
- `results/`: a results table written by the scripts. **Every number in the README and in the one-page summary comes from this table.** No number is typed by hand.
- 3 charts: one message each, the title states the finding, labelled axes with units, readable on a phone. Chart text is in English; the Japanese summary uses the same charts (proposal).
- `README.md` (English): the story, the charts, data checks, limitations, how to rerun, how this was built (AI note, see D7), and data credit to StatsBomb with their logo.
- One-page summary in English and Japanese (Markdown, also exported as PDF).
- Reproducible: `requirements.txt`, a fixed random seed, raw data cached locally and **not** committed to git.

## 5. Data checks (proposed; to confirm at M2)

1. Find "Serie A 2015/2016" in `competitions.json` by name. Do not hard-code the ids.
2. 380 matches, 20 teams, 38 matches per team.
3. Every match has an events file, and no match appears twice.
4. Goals counted from the events (shots with outcome "Goal", plus own goals) = the final score, in every match.
5. The league table rebuilt from the match scores = the official final table, typed in from a public source (the source URL is saved with it). Because it is typed by hand, the typed table is checked too (for example, total goals scored = total goals conceded).
6. Every shot has an xG value between 0 and 1.
7. Juventus's goals conceded from the events = the official figure from check 5.

If a check fails, we stop, find the reason and write it down in DECISIONS.md before moving on. No silent fixes.

## 6. Open decisions (settle before M3, before looking at any goals-vs-xG result)

| # | Decision | Options | Recommendation |
|---|---|---|---|
| O1 | Rule for "far fewer goals than xG" | (i) only the rank of "goals − xG" among the 20 teams · (ii) replay the season 10,000 times, letting each shot score with probability = its xG; "far fewer" if fewer than 5% of the replays end with this many goals or fewer (fixed seed), plus the rank chart | (ii): it tells us whether the gap could be chance |
| O2 | Possession (another explanation: a team that keeps the ball faces fewer shots) | add "shots conceded per opponent possession" · only mention it as a limitation | add it (about +2 h) |
| O3 | Penalties | include them · leave them out of both goals and xG | leave them out in the main test, and show the result with penalties as a check |
| O4 | Own goals (not shots, so no xG) | count them in goals conceded · leave them out when comparing with xG | leave them out of the comparison and report them separately |

## 7. Milestones

Time budget: about 10 hours per week. Extra time is used to finish **earlier**, not to add scope.

| # | Milestone | Output | Target | Status |
|---|---|---|---|---|
| M0 | Kickoff and plan | PLAN.md, DECISIONS.md | 2026-11-18 | done |
| M1 | Setup | local git repo, virtual environment, `requirements.txt`, `.gitignore`; git name and email for public commits; StatsBomb user agreement read and its requests listed | 2026-11-22 | done (2026-11-18) |
| M2 | Data and checks | registration with StatsBomb first (by me, see `docs/statsbomb_terms.md`); data downloaded and cached locally; data checks script and its results | 2026-11-29 | not started |
| M3 | Metrics | O1–O4 decided first; shots, xG and goals − xG for all 20 teams | 2026-12-06 | not started |
| M4 | Charts and results table → **MVP** | 3 charts and the results table, from one command | 2026-12-13 | not started |
| M5 | Write-up and publish | README; one-page summary (EN/JA); push to GitHub and make it public **only after my explicit OK** | about 2026-12-20 | not started |
| M6 | Polish and talk track | 1-minute and 5-minute explanations; likely questions and answers | 2027-01-31 | not started |
| — | February 2027 | no new work (freeze) | — | — |

## 8. Risks and limitations

- **One season, one data provider.** xG comes from StatsBomb's model, not ours.
- **Goalkeeper skill vs. luck cannot be fully separated.** xG measures the chance at the moment of the shot, not how well the shot was struck.
- **No big gap is not proof of no luck.** If goals conceded are close to xG, it only means the gap is within what chance can explain.
- **Possession** may explain fewer shots conceded (O2).
- **Event data only:** we do not see players without the ball.
- **Data terms:** the data is provided "as is" and StatsBomb can stop the service at any time. Raw data must not be shared (see `docs/statsbomb_terms.md`).
- **Explaining AI-written code:** each step ends with a short walk-through of the key lines, so I can explain every calculation.
- **Time:** other commitments in January–February come first, so the MVP is small and planned for mid-December.

## 9. How we work

- Small steps. Each step ends with a 3-line summary, what the output means, and a walk-through of the key lines.
- I decide the theme, the scope and the deliverables. Pushing to GitHub, making the repo public and deleting files need my explicit OK.
- Every decision goes into DECISIONS.md.
