# Decisions log

Every important decision in this project: the date, the options I considered, my choice and the reason.
The code is written with an AI coding assistant (Claude Code). The decisions below are mine.

---

## D1 · 2026-11-18 · Theme and question

**Options**
- A. Juventus 2015/16: why did they concede so few goals? (shots and xG conceded, all 20 teams)
- B. AS Roma 2015/16: what changed when Spalletti replaced Garcia in January? (before vs. after)
- C. Napoli 2015/16 under Sarri: what made their passing different? (pass maps, pass networks)
- D. Player positioning, linked to my earlier research. It needs StatsBomb "360" data, which Serie A 2015/16 does not have.

**Choice:** A

**Reason:** It is the clearest question for non-technical readers, it starts with a data check (rebuilding the goals-conceded figure from raw events), and the story works whatever the result is. A quick look at the open data before planning showed a full season for Serie A 2015/2016 (`competition_id` 12, `season_id` 27). The repo's own data checks will confirm the counts (M2).

## D2 · 2026-11-18 · One-page story (draft)

**Choice:** Question → Hypothesis → Verification → Implication, as written in PLAN.md section 2.

**Reason:** The hypothesis can fail, so the test is honest. Two weak points were found after the draft and will be fixed before the analysis: there was no rule for "far fewer goals than xG" (PLAN.md, O1), and possession could also explain fewer shots conceded (O2).

## D3 · 2026-11-18 · Main readers

**Options:** non-technical readers first (for example HR and business consultants) · technical readers first · one type of company first

**Choice:** Non-technical readers first. Technical detail stays in the repo (code, data checks, this log).

**Reason:** Most people who read the one-page summary will not be technical.

## D4 · 2026-11-18 · Time and roles

**Options:** about 4–5 hours per week (enough for the original timeline) · about 10 hours per week

**Choice:** About 10 hours per week. The AI assistant writes most of the code; I decide what to do, check the results and write the interpretation. The extra time is used to finish earlier, not to add scope.

**Reason:** My strength is deciding what to check and explaining it. Risk: I must still be able to explain the key calculations, so every step ends with a short walk-through of the key lines of code.

## D5 · 2026-11-18 · Format of the deliverables

**Options**
- A. Numbered scripts + README: one command reruns everything and writes the results table
- B. Notebook first: one Jupyter notebook with text, code and charts
- C. A + a small web app

**Choice:** A

**Reason:** Every number in the README can be traced back to code, and a rerun gives the same numbers. The order of the scripts (download → checks → metrics → charts) is also the order of the explanation. With B it is harder to guarantee a clean rerun. C costs the most time for little value to non-technical readers; it may be reconsidered in January if there is time.

## D6 · 2026-11-18 · Project folder and repository name

**Options:** a local folder · a folder on Google Drive

**Choice:** A local folder outside cloud sync. Repository name: `juventus-defence-2015-16`.

**Reason:** The raw event data is large (about 1.2 GB, a rough estimate from 8 of the 380 files) and does not need syncing, and git folders on a synced drive can break. GitHub is the backup, and the data can be downloaded again at any time. The name says what the project is about.

## D7 · 2026-11-18 · How the README states the AI assistance

**Options:** name the tool (Claude Code) · write only "an AI coding assistant"

**Choice:** Name the tool. README text:

> **How this was built.** The code was written with an AI coding assistant (Claude Code). The question, hypothesis, data checks, chart choices and interpretation are mine. Every decision is logged in DECISIONS.md, with the options I considered and the reason for my choice.

**Reason:** Being specific is more honest, and this log shows which parts are my work.

## D8 · 2026-11-18 · Language of the documents

**Options:** simple English · Japanese · both

**Choice:** Simple English for PLAN.md, DECISIONS.md, the README, code comments and chart text. The one-page summary is in English and Japanese.

**Reason:** The README is in English, so the decision log it links to should be readable by the same people.

## D9 · 2026-11-18 · Plan and timeline approved

**Options:** the first timeline (MVP by 31 Dec, public repo around 10 Jan, polish by about 10 Feb) · an earlier timeline (MVP by 13 Dec, public repo around 20 Dec, polish by 31 Jan, no new work in February)

**Choice:** The earlier timeline, and PLAN.md as written on 2026-11-18.

**Reason:** About 10 hours per week is enough to finish earlier. The repo can then be shown from late December, and other commitments in February come first.

## D10 · 2026-11-18 · Name and email in public commits

**Options:** name: GitHub username · real name · the current computer-wide setting; email: GitHub's no-reply address · my personal address; an AI co-author line in commit messages: yes · no

**Choice:** Real name "Masaki Takakuwa", my personal email address, and a "Co-Authored-By: Claude" line in commit messages.

**Reason:** Interviewers can connect the commits to me, and the co-author line matches how the README states the AI assistance (D7). Trade-off accepted: the email address is visible in the public history.

## D11 · 2026-11-18 · Automatic tests

**Options:** tests for the 3–4 key calculations only (about +2 hours) · tests for almost every function (about +4–5 hours) · no tests, only the data checks

**Choice:** Tests for the key calculations only, for example: "in a small hand-built match with 2 goals from shots and 1 own goal, the code counts 3 goals".

**Reason:** The data checks show that the data agrees with the final scores, but they cannot catch every mistake in a calculation (for example, adding up xG the wrong way). A few small tests, where the right answer is known in advance, show that each key calculation works, and they are easy to explain. Tests for every function would cost more time for little extra value.

## D12 · 2026-11-18 · How the data is downloaded and read

**Options:** save the original JSON files unchanged in `data/raw/` and read them with pandas · use the `statsbombpy` library

**Choice:** Save the original files unchanged, and record a fingerprint of each file (a SHA-256 hash: a short code that changes if even one character of the file changes). `statsbombpy` is no longer used.

**Reason:** The original files stay on my computer, so every rerun uses exactly the same data, even offline, and anyone can check that they have the same files by comparing the fingerprints. It also removes the risk that `statsbombpy` does not work with pandas 3. The cost is a little more code.

## D13 · 2026-11-18 · Data checks confirmed

**Options:** the 7 checks proposed in PLAN.md section 5 · the same without checks 5 and 7 (no comparison with a source outside StatsBomb)

**Choice:** All 7 checks, as written.

**Reason:** Checks 5 and 7 compare StatsBomb with an independent public source. This is the most convincing part of the checks, and it costs only about 1 hour (typing in the final table and checking it).

## D14 · 2026-11-18 · Source of the reference final table (checks 5 and 7)

**Options:** the Lega Serie A website (official) · Wikipedia (a fixed version of the page) · the Lega Serie A website, cross-checked with a second copy from RSSSF (a well-known archive of football results)

**Choice:** The Lega Serie A website, cross-checked with RSSSF.

**Reason:** The league's own table is the strongest reference. A second, independent copy costs about 30 more minutes and makes a typing mistake in the reference even less likely. The league website does not put the season in its address (the season is chosen in a menu), so the steps to reach the table and the date it was read are saved with it.

## D15 · 2026-11-18 · How the data is downloaded and checked (M2 work plan)

**Options:** the work plan as proposed by the AI assistant · changes to it

**Choice:** The plan as proposed. Its main points:
- Every file is downloaded from one fixed version (a commit) of StatsBomb's open-data repository, not from the latest version, so a rerun gets exactly the same files.
- Downloads use Python's built-in tools, with no extra library.
- Check 2 also checks that every team met every other team once at home and once away.
- League tables are compared team by team, not by position, because Serie A breaks ties on points with head-to-head results.
- If any check fails, the run stops before the analysis.

**Reason:** A rerun gives the same files and the same numbers, and each check is easy to explain.

## D16 · 2026-11-18 · GitHub repository: private until M5

**Options:** a private repository now, made public at M5 · a public repository now

**Choice:** A private repository now. It becomes public at M5, after the README and the StatsBomb logo are in place, and only after my explicit OK.

**Reason:** GitHub keeps a backup and the history from now on. Going public now would need a README with the StatsBomb credit and logo first (the data terms ask for them on published analysis), and my portfolio site lists my latest public repositories automatically, so an unfinished repository would appear there.

**Update (2026-11-18):** the repository was made public on this date, after my explicit OK, once the README, the one-page summaries and the StatsBomb credit and logo were in place (M5).

## D17 · 2026-11-18 · Rule for "far fewer goals than xG" (O1)

Decided before any xG number was calculated for the analysis.

**Options:** replay the season 10,000 times, letting each shot conceded become a goal with a probability equal to its xG (fixed random seed); "far fewer" if fewer than 5% of the replays end with as few goals as Juventus really conceded · only the rank of goals minus xG among the 20 teams

**Choice:** The replay. The rank of the 20 teams is still shown as a picture.

**Reason:** The replay answers the real question: could the gap be just chance? A rank cannot. "We replayed the season 10,000 times" is also easy to explain. Limitation: one season is too short to detect a small gap, so "within chance" does not prove that there was no luck.

## D18 · 2026-11-18 · Penalties and own goals in the comparison with xG (O3, O4)

**Options:** leave both out (results with penalties shown as a check, own goals counted separately) · keep penalties and leave out own goals · keep both

**Choice:** Leave both out of the main comparison. Results with penalties are shown as a check, and own goals are counted separately.

**Reason:** A penalty is a rare, very high-xG chance, so a few kicks could decide the result; analysts often leave penalties out of xG for this reason. Own goals are not shots and have no xG, so counting them as goals would make the comparison unfair.

## D19 · 2026-11-18 · Possession as another explanation (O2)

**Options:** add shots and xG conceded per 100 opponent possessions as a check · only mention possession as a limitation

**Choice:** Add them as a check. The main numbers stay per match.

**Reason:** "Did they concede few shots only because they kept the ball?" is the most likely question about this analysis, and the check answers it with numbers. Cost: about 2 hours, and a short explanation of how possessions are counted.

## D20 · 2026-11-18 · Analysis rules confirmed before any result

**Options** for the first part of the hypothesis ("the fewest and weakest chances"): supported only if Juventus is 1st of the 20 teams · supported if Juventus is in the top 3

**Choice:** Only if Juventus is 1st. The whole of PLAN.md section 6 is confirmed, including these proposals by the AI assistant:
- add xG per shot conceded, to test "the weakest chances" (the first plan had no measure of the quality of each chance);
- leave penalties out of all the main numbers, not only out of the comparison with xG;
- test Juventus only; the other 19 teams are the comparison;
- possession: "does not explain the low numbers" only if Juventus is also 1st on both per-possession measures;
- if a rule must change after the results are seen, show the result of the planned rule too, and log the reason here.

**Reason:** The hypothesis says "the fewest" and "the weakest", so only first place matches its words. Fixing every rule before calculating means that the results cannot shape the rules.

## D21 · 2026-11-18 · The three charts (M4)

**Options**
- A. (1) a scatter plot of shots conceded per match against xG per shot conceded; (2) goals minus xG for all 20 teams; (3) the 10,000 replays of Juventus's season
- B. bar charts of (1) shots conceded per match and (2) xG per shot conceded; (3) the replays
- C. as A, but (1) is a map of where the shots against Juventus and Napoli came from

**Choice:** A

**Reason:** Chart 1 shows both parts of "the fewest and weakest chances" in one picture. Chart 2 is the picture of all 20 teams promised in D17. C would add a claim that was not fixed before the results (where the shots came from), and more work.

Choices made by the AI assistant, listed here for my review:
- Juventus in orange and the other 19 teams in grey. The two colours were checked for colour-blind readers.
- Each title states the finding, and every number on a chart is read from the results tables. If a result changes, the chart script stops instead of keeping a title that no longer fits.
- The charts ignore personal matplotlib settings and use the font that comes with matplotlib, so they look the same on every computer.
- mplsoccer (for drawing pitches) is not needed, so it was taken out of `requirements.txt`.

## D22 · 2026-11-18 · StatsBomb logo on every chart

**Options:** the logo and "Data: StatsBomb" on every chart · the logo only in the README and the one-page summary

**Choice:** On every chart.

**Reason:** The user agreement asks for the logo on published analysis (1.4), and a chart can be shared on its own. The logo file comes from the same fixed commit of the open-data repository as the data. Like the data, it is downloaded by `src/01_download.py` and not committed.

## D23 · 2026-11-18 · How the numbers get into the README and the one-page summaries (M5)

**Options**
- A. The text is written by hand, with a placeholder wherever a number goes. `src/05_report.py` fills in every number from the results tables and writes the README and the summaries.
- B. The README is written by hand, with the numbers copied from the tables, and a test compares them.

**Choice:** A

**Reason:** No number in the text is typed by hand, so a rerun can never leave an old number behind. Like the chart script, `05_report.py` stops if a result is no longer the one that the text was written for. The cost: the README is changed in its template, not in `README.md` itself.

Choices made by the AI assistant, listed here for my review:
- The templates are in `templates/`. `05_report.py` writes `README.md`, `docs/summary_en.md` and `docs/summary_ja.md` from them.
- `05_report.py` also stops if a template contains a typed number: a digit outside a placeholder, except in a few names and units that are not results (the season "2015/16", the repository name, "per 100 possessions").
- The one-page summaries name me as the author. My real name is already public in the commits (D10).
- The README shows StatsBomb's logo from the same fixed commit of the open-data repository, because the logo file is not committed (D22).

## D24 · 2026-11-18 · The implication

**Options:** a lesson about football and a lesson for data work (two sentences) · the football lesson only · the data-work lesson only

**Choice:** Both sentences:

> Judge a defence by the quality of the chances it allows, not only by how many shots or goals it concedes.
>
> Before explaining a headline number, break it into its drivers: Juventus's record came from very few shots and the weakest chances in the league, and luck is not needed to explain it.

**Reason:** The first sentence is for readers who know football. The second shows a habit that any data work needs: before explaining a headline number, break it into what drives it.

**Changed on the same day, before anything was published (my choice, after the AI assistant pointed out the problem).** The first wording of the second sentence was "Juventus's record came from the weakest chances, not the fewest shots". It could be read as if the number of shots did not matter, but Juventus allowed the 2nd fewest shots, only 2 more than Napoli in the whole season. The new wording names both drivers. The results and the verdicts did not change.

## D25 · 2026-11-18 · How the one-page summaries become PDFs

**Options**
- A. Add Python-Markdown (a widely used library) to turn each summary into a web page, and print the page with Microsoft Edge or Google Chrome, without opening a window.
- B. No new library: write the text of the summaries in HTML.
- C. No PDF: only the summaries on GitHub, printed by hand when needed.

**Choice:** A

**Reason:** The summaries stay easy to edit as Markdown, and `run_all.py` makes the PDFs like every other output. The version of the library is fixed in `requirements.txt`.

Choices made by the AI assistant, listed here for my review:
- `src/06_pdf.py` stops if a summary does not fit on one A4 page.
- A PDF stores the time when it was printed. A new print is compared with the old PDF without those times, and the old file is kept if nothing else changed, so a rerun does not change the PDFs.
- If neither browser is found, the step is skipped with a message. The Markdown summaries are still written.
- Each print uses a new, empty browser profile, so my own browser (settings, history, sign-ins) is not touched.

## D26 · 2026-11-18 · Talk track and practice for interviews (M6)

**Options**
- A. The minimum: a 1-minute and a 5-minute explanation in Japanese, and about 15 likely questions with answers (about 5 hours).
- B. A, plus a short link from the project to each kind of job I apply for, and the 1-minute explanation in English (about 8 hours).
- C. B, plus 3 practice interviews with the AI assistant as the interviewer (2 in Japanese, 1 in English), and a 10-second test of chart 1 with 1–2 people who do not work with data (about 12 hours).

Who writes first: the AI assistant writes an outline (the order of the points and the numbers to use), and I write the sentences in my own words · the AI assistant writes a full draft and I edit it · I write everything and the AI assistant only checks it.

Deadline: 2026-12-13 · the 1-minute explanation and the main answers by 2026-12-06, the rest by 2027-01-31 · 2027-01-31 (the first plan).

**Choice:** C. The AI assistant writes the outline, and I write the sentences. Deadline 2026-12-13.

**Reason:** In an interview, what counts is whether I can say it in my own words, and only practice shows where I get stuck: for example, "Did you write the code yourself?" (the README says that an AI assistant wrote it, D7). Writing the sentences myself also shows what I do not understand yet. I need the talk track earlier than the first plan's date, and M5 finished about a month early, so the time is there now, before my other commitments in January and February. The 10-second test checks a goal in section 1 of PLAN.md (each chart can be understood in 10 seconds), which no real reader has tested yet. This adds to the first plan for M6, but it uses the time saved, and the deadline moves earlier, not later.

Choices made by the AI assistant, listed here for my review:
- The talk track is not in this repository. It names the companies I apply to, so it stays in a folder that git ignores.
- The talk track uses only numbers that are also in the README, so a reader can check every number I say in an interview.
- Order: the 1-minute explanation first (it is needed in any interview), then the likely questions, then the 5-minute explanation and the job links, and last the practice interviews and the 10-second test.

**Changed on the same day (my choice).** The AI assistant writes a first draft of each text, and I correct it. The AI assistant pointed out the risk: a text that is not in my own words can sound learned by heart. The practice interviews check that I can say the points in my own words, without reading.

## D27 · 2026-11-18 · Charts on a phone, and the rules of the 10-second test (M6)

**What was checked.** The public pages were opened 375 pixels wide, like a small phone. In the README, GitHub shows each chart 309 pixels wide, so the text of a chart is 7 to 13 pixels high (the README's own text is 16): small, but readable without zooming. This is a little smaller than `src/04_charts.py` expected (about 340 pixels). In the one-page summaries, the two charts were side by side, each 151 pixels wide, with text of 3.5 to 6.3 pixels: not readable without zooming.

**Options**
- README charts: keep them as they are · make the text larger and draw the charts again.
- Summary charts: on GitHub, show them one below the other at full width, and keep them side by side in the PDF · keep them as they are (the PDF is the main form of the summary, and on GitHub a chart can be tapped to open it).

**Choice:** Keep the README charts. Show the summary charts one below the other on GitHub, and keep them side by side in the PDF.

**Reason:** Interviewers will mostly see the README on a computer or the summary on paper, and the README charts can be read on a phone. The summary charts could not be read on a phone at all, and the fix does not change the PDF: the new print is the same as the old one, except for the time it was printed.

Choices made by the AI assistant, listed here for my review:
- The summaries now show the charts as Markdown pictures. `src/06_pdf.py` makes them 49% wide when it prints, so the PDF did not change.
- The comment in `src/04_charts.py` now gives the measured width (309 pixels) instead of the expected one. The charts did not change.

**Rules of the 10-second test, fixed before the test (D26).** 1–2 people who do not work with data, have not seen the chart and can read simple English look at chart 1 for 10 seconds. Then, without looking, they say in a few words what it shows.
- Pass: they say, in any words, that the shots Juventus allowed were the least likely to go in (the weakest chances).
- Partly: they only say that Juventus stands out or defends well, without the quality of the shots.
- Fail: they cannot say, or they read it wrongly (for example, "Juventus faced the fewest shots": they faced the 2nd fewest).

If anyone does not pass, I decide whether to change the title or the axis names, and the change is logged here. The names of the people are not written down.
