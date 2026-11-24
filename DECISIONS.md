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

**Changed on the same day, after checking GitHub (my choice, after the AI assistant pointed out the problem).** On a computer, GitHub then showed the two summary charts one below the other at full width (911 pixels each), so the summary page became very long. Now each chart is 440 pixels wide, so that the two charts are side by side on a computer, about as before, and one below the other on a phone, where GitHub shrinks each chart to the width of the screen. The PDF still did not change.

**Changed again on the same day, after checking more window widths (my choice, after the AI assistant pointed out the problem).** In a window 1,280 pixels wide, GitHub showed the list of files on the left, so the text of the page was only 846 pixels wide, and the two 440-pixel charts were one below the other there. Now each chart is 410 pixels wide: the two charts and the space between them need 824 pixels. This was tested on GitHub's page before the change: the charts were side by side in windows 1,280 and 1,440 pixels wide. In a narrower window with the list of files open, they are still one below the other (for example 1,200 pixels, where the text is 766 pixels wide). The PDF still did not change.

## D28 · 2026-11-19 · Correction: where the other players were is known at each shot

**What was found.** While looking for the next analysis, the AI assistant counted what StatsBomb's event data contains. For almost every shot, it also records where the players were at the moment of the shot (StatsBomb's "freeze frame"; not always every player). So the limit written in the README, the one-page summaries and section 8 of PLAN.md ("the data shows what happened on the ball, not where the other players were") was wrong. No result changes: the analysis did not use these positions.

**Options**
- Correct the sentence now.
- Correct it later, together with the next analysis, which may use these positions.

**Choice:** Correct it now.

**Reason:** The pages are public, and a reader who knows StatsBomb's data would notice the mistake. The new sentence says that the data shows where the other players were only when a shot was taken.

Choices made by the AI assistant, listed here for my review:
- The new wording, in English and Japanese. The one-page summaries use a short form of it, so that they still fit on one page.

## D29 · 2026-11-19 · One level deeper: why were the chances weak? (M7)

**What happened.** After M5, I asked the AI assistant for ideas that would take the project to a higher level. It first counted what the data contains, league-wide and without looking at any team: the positions of the players at the moment of almost every shot (the freeze frame, D28), the same season of four other European leagues, and many defending events.

**Options**
1. Use the positions at the moment of each shot to explain why the chances against Juventus were weak (about 8–10 hours).
2. Build my own xG model, to check that the results do not depend on StatsBomb's model (about 10–12 hours, and a new library).
3. Compare the best defences of the five big European leagues of 2015/16 (about 15–20 hours, and about five times the data).

Also considered: pressing (where the ball was won back), and an interactive dashboard.

**Choice:** 1, as a new milestone, M7.

**Reason:** The project so far shows what was special about Juventus's defence (the weakest chances in the league), not why. Option 1 answers why, with data that the project already has, in the time available.

**When.** Options: M7 first (rules by 2026-11-22, results by 2026-11-29), then M6 from 2026-11-30 · M6 first, and M7 in December–January · both at the same time.

**Choice:** M7 first. M6 keeps its deadline (2026-12-13, D26), so it has two weeks instead of three. If M7 is not finished by 2026-11-29, M6 starts anyway.

**Reason:** The talk track can then include the answer from the start, and January stays free for my other commitments.

## D30 · 2026-11-19 · Rules of the second question, fixed before any result (M7)

**Options**
- How to answer the question: split the gap into "where" and "how", and count the defenders in the way · only count the defenders in the way and the space of the shooter (this cannot say how much of the gap each reason explains).
- How to judge each part: compare Juventus with random sets of team-matches, supported if fewer than 5% are as extreme · supported only if Juventus is 1st of the 20 teams.
- Frames with few players: use all of them, and check the result without the frames with fewer than 8 players · leave those frames out · use all of them, without a check.

**Choice:** Split the gap into "where" and "how", and count the defenders in the way. Judge each part against random sets of team-matches. Use all frames, with the check. The rules are in PLAN.md section 6b.

**Reason:** The split shows how much of the weak chances came from where the opponents shot, and how much from how hard their shots were, like breaking a business result into its drivers. Random sets of matches answer whether a difference could be chance, as the replays did in D17; a rank cannot. A frame with few players may show a fast counter-attack with few defenders back, so leaving those frames out would bias the result; the check shows whether they matter.

**My expectation**, written before any result: the where part and the how part are about the same size.

Choices made by the AI assistant, listed here for my review:
- The zones: 10 groups of the same size by distance, and 3 by angle inside each, made from the shots of all 20 teams.
- The goalkeeper is not counted as a defender in the way. The goalkeeper's position belongs to the goalkeeper's own play, which the first hypothesis keeps apart from how the team defended.
- Direct free kicks are left out of "defenders in the way", because the wall would count as defenders in the way.
- The distance to the nearest defender is shown, but not judged, so that there are no more tests.
- A random set is made of whole team-matches, so that the shots of one match stay together. The same random sets are used for all three parts and for the check.
- In the check, the zones stay the same, and the expected numbers are calculated again without the frames with fewer than 8 players.
- "About the same size" in my expectation means that each part is between a third and two thirds of the gap.
- The code stops if a non-penalty shot has no location or no freeze frame.

**Changed before the rules were committed (my choice, after the AI assistant pointed out a flaw in its own proposal).** The first version compared Juventus with random sets of 38 team-matches. But Juventus conceded fewer shots per match than the average team, so such a set has more shots than Juventus conceded, and its average varies less: Juventus's value would look less like chance than it is, and a part would be "supported" too easily. Now each random set is filled with whole team-matches until it has at least as many shots as Juventus conceded.

## D31 · 2026-11-19 · Details of the second question, decided while writing the code (M7)

The rules of PLAN.md section 6b were published before any of their numbers was calculated (D30). While writing the code, the AI assistant made the following choices, which the rules did not fix. All of them were made before the first results were calculated, and they are listed here for my review.
- The distance to the nearest defender is compared "in the same way" as the defenders in the way, so direct free kicks are left out of it too.
- Ranks: 1st is the value that helps the defence most, that is, the lowest where part, how part and distance to the nearest defender, and the most extra defenders in the way.
- The zones are cut at the values, so two shots at the same distance, or at the same angle in one distance group, are always in the same zone. So the zones have about the same number of shots, not exactly the same.
- A team-match in which a team conceded no shot is still one of the 760 team-matches.
- The random sets use the same fixed random seed as the replays (D17).
- The last team-match of a random set usually goes past Juventus's number of shots, so a random set has a few more shots than Juventus. This makes the comparison very slightly less strict. In `results/where_how_tests.csv`, every part is far from the 5% line, so this does not change any judgement.
- The code stops if a team's shots or xG per shot differ from step 3, which reads the same data in another way.
- The code is in `src/where_how.py` (tested in `tests/test_where_how.py`) and `src/03b_where_how.py`, which `run_all.py` runs between steps 3 and 4. The other scripts keep their names, because this file refers to them.

**A check outside the repository.** The AI assistant also counted the key numbers again with other methods: the zones with another tool, the defenders in the way with another way of testing whether a point is inside a triangle, and Juventus's parts straight from its shots. All of them matched. The first version of that check had its own mistake, for the one shot taken from the goal line outside the posts; the project's code was right.

## D32 · 2026-11-19 · The chart of the second question (M7)

Chosen after the results, as in D21.

**Options**
- A. a bridge chart: from the league's xG per shot to Juventus's, in two steps (where, then how)
- B. a scatter plot of the 20 teams, with the where part across and the how part up
- C. a bar chart of the extra defenders in the way, for the 20 teams
- For the defenders in the way (not supported): say it in the text of the README and the summaries · also draw chart C in the README

**Choice:** A, and the defenders in the way in the text only.

**Reason:** A shows the main result in one picture: Juventus's gap from the league splits into two parts of about the same size. Breaking a number into its drivers is a common way to explain a result. B compares the teams, but its axes ("the where part", "the how part") are hard to read for someone who does not know the method. C shows only the part that was not supported. With one chart, each summary can still fit on one page.

Choices made by the AI assistant, listed here for my review:
- The chart is `results/charts/4_where_how.png`. Grey is the league; orange is Juventus and its two parts. These are the two colours of the other charts, so no new colour was needed.
- The title uses the words of my expectation, "about the same size" (D30). The subtitle says that each part was the lowest of the 20 teams and unlikely to be chance, because the chart itself shows only Juventus. As for the other charts, the script stops if one of these results changes.
- `results/where_how_tests.csv` now also has the league's xG per shot (shown, not judged), so every number on the chart is read from the results tables. Nothing else in the tables changed.
- The value of each step is at the end it moves to (on the left of the bar), and each total is at the end of its bar. In the sketch I chose from, the values of the steps were on the right.

## D33 · 2026-11-23 · The second question in the README and the one-page summaries (M7)

**Options** for the one-page summaries, which must still fit on one page (before this change, about 4 more lines of English and 3 of Japanese fitted):
- A. put chart 4 in place of chart 3 (the replays): charts 1 and 4 side by side. Chart 3 stays in the README, and the summaries still give its result in words
- B. words only: charts 1 and 3 as before, and chart 4 only in the README
- C. charts 1, 3 and 4 side by side (each smaller, so the text on the charts is very small in print)

For the README: a new section after "What I found" · one more paragraph in "What I found", with chart 4 next to the other charts.

**Choice:** A, and a new section in the README.

**Reason:** The two charts of a summary now tell one story: Juventus allowed the weakest chances (chart 1), and why they were weak (chart 4). The result of the replays is still in the text, and its chart is in the README. A section of its own shows that the second question had its own rules, fixed before its results.

Choices made by the AI assistant, listed here for my review:
- Each summary gets one more point under "What the data shows" and one more sentence under "Limits": what "how" means (everything that is not the place, so not only how Juventus defended). The README gets the new section, one more sentence in "Short answer" and in "So what", and two more limitations: what "how" means, and the chance that one of the new tests is supported by luck alone (the most it can be, from the rules).
- To keep the Japanese summary on one page, it is shorter in two places: the note on xG no longer says that xG comes from StatsBomb's model (the limits still say so), and the data checks give one example instead of two. The new point in the English summary was written short for the same reason.
- The Japanese limits said 「運がなかった」, which can be read as "they were unlucky". It now says 「運が関係なかった」 ("luck played no part"), the meaning of the English summary.
- `src/05_report.py` reads every number of the new text from `results/where_how_tests.csv`, `results/where_how_teams.csv` and `src/config.py`. As for the first question, it stops if a result that the text describes changes.
- Room left at the bottom of each page, measured by printing with Edge on my computer: about 3 mm in English and 6 mm in Japanese. On a computer with other fonts, a summary may not fit; the PDF step then stops and says so.
