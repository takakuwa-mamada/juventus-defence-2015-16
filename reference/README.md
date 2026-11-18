# Reference tables

The final Serie A 2015/16 table from two public sources outside StatsBomb. Data checks 5 and 7 compare StatsBomb's data with them (PLAN.md section 5, DECISIONS.md D14).

| File | Source | How to reach the table | Read on |
|---|---|---|---|
| `final_table_legaseriea.csv` | Lega Serie A, the official league website: https://www.legaseriea.it/serie-a/classifica | Choose "2015/2016" in the season menu above the table. The web address does not change when you do this. | 2026-11-18 |
| `final_table_rsssf.csv` | RSSSF (Rec.Sport.Soccer Statistics Foundation), an archive of football results: https://rsssf.org/tablesi/ital2016.html | "Final Table" at the top of the page | 2026-11-18 |

**Columns:** `team` (StatsBomb's spelling, so that the tables can be compared), `name_on_source` (the name as written on the source), `played`, `won`, `drawn`, `lost`, `goals_for`, `goals_against`, `points`. The rows are in the order of the source (final position). Notes on the sources, such as RSSSF's head-to-head notes in brackets, are not copied.

**How the tables were made and checked**

- The numbers were copied from the text of each page by the AI assistant (not from memory), on the date above.
- `src/02_checks.py` checks them every time it runs: the totals of each table must add up (check 5a), and the two tables must agree on every number (check 5b).
