# Plan: Why did Juventus concede so few goals? (Serie A 2015/16)

**Status:** approved on 2026-11-18 (D9) · **Last updated:** 2026-11-19
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
- **One level deeper (M7, D29):** Juventus allowed the weakest chances. Why? Either the opponents shot from places where shots rarely go in (**where**), or, from the same places, their shots were harder to score, for example because more defenders were in the way (**how**). The rules are in section 6b.

> **xG (expected goals):** for each shot, the probability that it becomes a goal, from StatsBomb's model (based on many similar past shots). A team's **xG conceded** is the sum over all the shots it faced.

## 3. Scope

- **In:** Serie A 2015/16 (all 20 teams, for comparison); StatsBomb open event data, including the positions of the players at the moment of each shot ("freeze frame", M7); Python (pandas, numpy, matplotlib, pytest for a few tests, and Python-Markdown for the PDF summaries).
- **Out, for now:** other seasons and leagues; player-position ("360") data, which this season does not have; machine learning; a web app (maybe in January, only if there is time and I agree).

## 4. Deliverables

- Numbered scripts in `src/` (`01_download`, `02_checks`, `03_metrics`, `04_charts`, `05_report`, `06_pdf`), all run by **one command** (`run_all.py`).
- `results/`: a results table written by the scripts. **Every number in the README and in the one-page summary comes from this table.** No number is typed by hand.
- 3 charts: one message each, the title states the finding, labelled axes with units, readable on a phone. Chart text is in English; the Japanese summary uses the same charts (proposal). Chosen in D21: (1) how many chances each team allowed and how good they were, (2) goals minus xG for all 20 teams, (3) the replays of Juventus's season. Each chart carries the StatsBomb logo (D22). Written to `results/charts/`.
- `README.md` (English): the story, the charts, data checks, limitations, how to rerun, how this was built (AI note, see D7), and data credit to StatsBomb with their logo. Written by `src/05_report.py` from a template in `templates/`, with every number filled in from `results/` (D23).
- One-page summary in English and Japanese (`docs/summary_en.md`, `docs/summary_ja.md`; Markdown, also exported as PDF). Written the same way as the README (D23), and printed to one A4 page each by `src/06_pdf.py` (D25).
- Reproducible: `requirements.txt`, a fixed random seed, the original data files cached locally (**not** committed to git) with a fingerprint of each file, so anyone can check that they have the same data (D12).
- A few small automatic tests for the key calculations (D11).
- M7 (D29): the results of section 6b in `results/`, at least one more chart (chosen after the results, as in D21), and the README and the one-page summaries updated. Each summary must still fit on one page.

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

## 6b. Rules of the second question (fixed on 2026-11-19, before any result was calculated)

These rules were fixed before any number of this section was calculated for any team (D30). Before that, only league-wide counts were looked at: how many shots have a freeze frame, and how many players the frames show (used for the check at the end). The promise of section 6 holds here too: if a rule turns out to be wrong after we see the results, we keep the planned version, show the new version next to it, and log the reason in DECISIONS.md.

**Shots.** All non-penalty shots of the season, as in section 6. The code checks that every one of them has a location and a freeze frame, and stops if one does not.

**Where the shot was taken.** StatsBomb's pitch is 120 × 80 yards, and every team shoots at the goal at x = 120, between the posts at y = 36 and y = 44.
- *Distance:* from the shot's location to the centre of the goal (x = 120, y = 40).
- *Angle:* the angle between the lines from the shot's location to the two posts. The wider the angle, the wider the goal looks from there.
- *Zones:* the shots of all 20 teams are split into 10 groups of the same size by distance, and each group into 3 groups of the same size by angle: 30 zones with about the same number of shots each.
- *Expected xG of the place:* for each shot, the average xG of all the league's shots in its zone.

**The split**, for every team, over the shots it conceded:
- *Gap* = xG per shot conceded (measure 2 of section 6) − the league's xG per shot.
- *Where part* = the average expected xG of the place − the league's xG per shot. Below zero: the opponents shot from worse places than average.
- *How part* = xG per shot conceded − the average expected xG of the place. Below zero: from the same places, the shots were less likely to go in than average.
- Where part + how part = gap. The share of each part in Juventus's gap is shown, but it does not decide anything.

**Defenders in the way**, from the freeze frame:
- For each shot, the number of players of the conceding team, not counting the goalkeeper, who stand inside the triangle between the ball and the two posts. A player on the edge of the triangle counts.
- *Expected number for the place:* the league's average in the same zone.
- *Extra defenders* = the average, over the shots conceded, of (number − expected number). Above zero: more defenders in the way than usual for shots from the same places.
- Direct free kicks are left out of this measure and of its expected numbers, because the wall would count as defenders in the way.
- Also shown, but not judged: the distance from the ball to the nearest defender (not the goalkeeper), compared in the same way with the league's average for the zone.

**How each part is judged.** Only Juventus is tested, as in section 6.
- Juventus's value is compared with 10,000 random sets of team-matches (fixed random seed). A team-match is the shots that one team conceded in one match, so 380 matches give 760 team-matches. Each random set takes whole team-matches from all 760, in a random order and each at most once, until it has at least as many shots as Juventus conceded. So a random set has about as many shots as Juventus, and the shots of one match stay together. Its value is calculated in the same way as Juventus's. The same random sets are used for all three parts and for the check below. (The number of shots matters: an average over more shots varies less, so random sets with more shots than Juventus would make Juventus's value look less like chance than it is.)
- "Where": supported if fewer than 5% of the random sets have a where part as low as Juventus's, or lower.
- "How": supported if fewer than 5% of the random sets have a how part as low as Juventus's, or lower.
- "Defenders in the way": supported if fewer than 5% of the random sets have as many extra defenders as Juventus, or more.
- Otherwise the part is not supported, and we say so. Juventus's rank among the 20 teams is shown for each part, but it does not decide the result.

**Check: frames with few players.** A freeze frame shows only the players in the video, so a defender may be missing. But a frame with few players may also show a fast counter-attack, with few defenders back. So all frames are used, and "defenders in the way" is calculated again, in the same way, without the frames that show fewer than 8 players. The zones stay the same, and the expected numbers are calculated again from the league's shots that are left. If the judgement changes (from supported to not supported, or the other way), both results are shown, and we say that the result depends on these frames.

## 7. Milestones

Time budget: about 10 hours per week. Extra time is used to finish **earlier**, not to add scope (M7 was added by my own decision, D29).

| # | Milestone | Output | Target | Status |
|---|---|---|---|---|
| M0 | Kickoff and plan | PLAN.md, DECISIONS.md | 2026-11-18 | done |
| M1 | Setup | local git repo, virtual environment, `requirements.txt`, `.gitignore`; git name and email for public commits; StatsBomb user agreement read and its requests listed | 2026-11-22 | done (2026-11-18) |
| M2 | Data and checks | registration with StatsBomb first (by me, see `docs/statsbomb_terms.md`); data downloaded and cached locally; data checks script and its results | 2026-11-29 | done (2026-11-18): all checks passed, see `results/data_checks.csv` |
| M3 | Metrics | O1–O4 decided first; shots, xG and goals − xG for all 20 teams | 2026-12-06 | done (2026-11-18): rules committed first (D20), then the results: `results/hypothesis_tests.csv` |
| M4 | Charts and results table → **MVP** | 3 charts and the results table, from one command | 2026-12-13 | done (2026-11-18): `results/charts/` and `results/*.csv`, all from `run_all.py` |
| M5 | Write-up and publish | README; one-page summary (EN/JA); make the GitHub repository public **only after my explicit OK** (it is private until then, D16) | about 2026-12-20 | done (2026-11-18): README, one-page summaries and their PDFs, all written by `run_all.py` (D23–D25); the repository is public (D16) |
| M6 | Polish and talk track | 1-minute (Japanese and English) and 5-minute explanations; likely questions and answers; a link from the project to each kind of job I apply for; 3 practice interviews; a 10-second test of chart 1 with real readers (D26). The talk track itself is kept private | 2026-12-13 (was 2027-01-31, D26) | in progress (2026-11-18); paused until 2026-11-30 for M7 (D29) |
| M7 | Why were the chances weak? (one level deeper) | rules fixed first (section 6b, D30); the split into "where" and "how" and the defenders in the way, for all 20 teams, with the check; at least one chart; README and one-page summaries updated | 2026-11-29 (D29) | in progress (2026-11-19): rules fixed |
| — | February 2027 | no new work (freeze) | — | — |

## 8. Risks and limitations

- **One season, one data provider.** xG comes from StatsBomb's model, not ours.
- **Goalkeeper skill vs. luck cannot be fully separated.** xG measures the chance at the moment of the shot, not how well the shot was struck.
- **No big gap is not proof of no luck.** If goals conceded are close to xG, it only means the gap is within what chance can explain.
- **Possession** may explain fewer shots conceded (O2).
- **Event data only:** we see the players without the ball only when a shot is taken (StatsBomb's "freeze frame", not always every player). Corrected on 2026-11-19 (D28).
- **Three more tests (M7).** Each of the three parts in section 6b is judged at 5%, so the chance that at least one of them is "supported" by luck alone can be up to 15% (3 × 5%).
- **What "how" means (M7).** The how part includes everything that is not the place: the defenders, pressure, the body part, the type of shot and the goalkeeper's position. StatsBomb's xG may already use some of the positions in the freeze frame. The zones use only distance and angle, so small differences of place inside a zone also end up in the how part.
- **Data terms:** the data is provided "as is" and StatsBomb can stop the service at any time. Raw data must not be shared (see `docs/statsbomb_terms.md`).
- **Explaining AI-written code:** each step ends with a short walk-through of the key lines, so I can explain every calculation.
- **Time:** other commitments in January–February come first, so the MVP is small and planned for mid-December.

## 9. How we work

- Small steps. Each step ends with a 3-line summary, what the output means, and a walk-through of the key lines.
- I decide the theme, the scope and the deliverables. Pushing to GitHub, making the repo public and deleting files need my explicit OK.
- Every decision goes into DECISIONS.md.
