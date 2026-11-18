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
