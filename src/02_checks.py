"""Step 2: run the data checks (PLAN.md section 5) and write results/data_checks.csv.

Run from the project root:
    .venv\\Scripts\\python src\\02_checks.py

If any check fails, the script ends with an error, so run_all.py stops before the
analysis. The rule for a failure: find the reason and write it in DECISIONS.md
before moving on. No silent fixes.
"""
import sys
from dataclasses import asdict

import pandas as pd

import checks
import sbdata
from config import (
    COMPETITION_NAME,
    MATCHES_PER_TEAM,
    N_TEAMS,
    OFFICIAL_TABLE,
    RESULTS_DIR,
    ROOT,
    SEASON_NAME,
    SECOND_TABLE,
    TEAM,
)


def main() -> int:
    competitions = sbdata.read_json("competitions.json")
    results = [checks.check_season(competitions, COMPETITION_NAME, SEASON_NAME)]
    if not results[0].passed:
        return finish(results)  # without the season's ids, nothing else can be checked

    competition_id, season_id = sbdata.find_season(competitions, COMPETITION_NAME, SEASON_NAME)
    matches = sbdata.matches_table(sbdata.read_json(f"matches/{competition_id}/{season_id}.json"))
    print(f"Reading the events of {len(matches)} matches...", flush=True)
    events, n_events, _ = sbdata.load_events(matches["match_id"].tolist())  # possessions are not checked
    goals = checks.goals_per_match(matches, events)
    official = pd.read_csv(OFFICIAL_TABLE, encoding="utf-8")
    second = pd.read_csv(SECOND_TABLE, encoding="utf-8")

    results += [
        checks.check_fixtures(matches, N_TEAMS),
        checks.check_events_files(matches, n_events),
        checks.check_goals_vs_scores(matches, goals),
        checks.check_references_consistent(official, second, N_TEAMS, MATCHES_PER_TEAM),
        checks.check_sources_agree(official, second),
        checks.check_table_vs_official(checks.league_table(matches), official),
        checks.check_xg_range(events),
        checks.check_team_conceded(matches, goals, official, TEAM),
    ]
    return finish(results)


def finish(results: list[checks.CheckResult]) -> int:
    """Write the results table, print one line per check, and return the exit code."""
    out = RESULTS_DIR / "data_checks.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame([asdict(result) for result in results])
    table.to_csv(out, index=False, encoding="utf-8", lineterminator="\n")

    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'}  {result.check:<3} {result.description}")
        print(f"           {result.detail}")
    failed = sum(not result.passed for result in results)
    print(f"\n{len(results) - failed} of {len(results)} checks passed -> {out.relative_to(ROOT).as_posix()}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
