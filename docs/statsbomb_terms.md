# StatsBomb open data: what the terms ask of this project

Read on 2026-11-18. Sources, both in the open-data repository (https://github.com/statsbomb/open-data):
- `README.md` ("Terms & Conditions")
- `LICENSE.pdf`: "StatsBomb Public Data User Agreement", last updated 8 September 2023

This is my own summary for planning, not legal advice. The original documents are the reference.

| What the terms ask | What this project does |
|---|---|
| Use the data for analysis and research. Analysis and conclusions may be shared publicly. | The project publishes analysis (charts, a small results table, a one-page summary), not the data. |
| Do not distribute, reproduce, sell or give the data to anyone else (agreement 1.2.1 and 7). | Raw data is never committed (`data/` is in `.gitignore`). Only small summary tables (one row per team) are published. Event-level extracts stay on my computer. |
| Do not use the data, or analysis made from it, for commercial purposes (1.2.2). | Nothing is sold. There is no paid product or service. |
| Do not publish anything that might be defamatory or damaging to a person or an organisation (1.2.4). | Neutral, evidence-based wording about players and clubs, for example "fewer goals than xG predicted", not judgements about people. |
| Credit StatsBomb with its logo on any published analysis (1.4), and state the data source as StatsBomb (README). | "Data: StatsBomb" and the StatsBomb logo in the README and in the one-page summary. Proposal for M4: also on each chart, because a chart can be shared on its own. |
| Register name and email at statsbomb.com/resource-centre before using the data (agreement, opening part and 2.2). | Not done yet. I will register before the full download in M2. |
| The data is provided "as is", with no promise of accuracy or completeness (3). | One more reason for the data checks (PLAN.md, section 5). |
| StatsBomb can stop the service at any time (2.1). | Limitation: a rerun needs the data to still be available on GitHub. |
