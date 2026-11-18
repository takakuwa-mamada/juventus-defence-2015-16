"""The key calculations and the data checks (PLAN.md section 5).

These functions only calculate. They do not read files, so the key calculations
can be tested with tiny hand-built examples (tests/test_key_calculations.py).
"""
from dataclasses import dataclass

import pandas as pd

import sbdata

# Columns of a league table, in the usual order.
TABLE_COLUMNS = ["played", "won", "drawn", "lost", "goals_for", "goals_against", "points"]


def goals_per_match(matches: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Count each side's goals in each match from the events, to compare with the final score.

    A team's goals = its shots with outcome "Goal" + its "Own Goal For" events.
    StatsBomb records each own goal twice: "Own Goal For" for the team that gets
    the goal and "Own Goal Against" for the team that concedes it (StatsBomb Open
    Data Events v4.0.0, event types 25 and 20, pages 4-5). Counting only
    "Own Goal For" puts each own goal on the right side, and only once.
    """
    is_goal = ((events["type"] == "Shot") & (events["shot_outcome"] == "Goal")) | (
        events["type"] == "Own Goal For"
    )
    # {(match_id, team): number of goals}. A pair that is missing means 0 goals.
    goals = events[is_goal].groupby(["match_id", "team"]).size().to_dict()

    result = matches[["match_id"]].copy()
    result["home_goals_events"] = [
        goals.get((match_id, team), 0) for match_id, team in zip(matches["match_id"], matches["home_team"])
    ]
    result["away_goals_events"] = [
        goals.get((match_id, team), 0) for match_id, team in zip(matches["match_id"], matches["away_team"])
    ]
    return result


def league_table(matches: pd.DataFrame) -> pd.DataFrame:
    """Build the league table from the final scores: 3 points for a win, 1 for a draw.

    The table is sorted by team name, not by position, because Serie A breaks
    ties on points with head-to-head results. Tables are compared team by team.
    """
    # One row per team per match: first from the home side, then from the away side.
    home = pd.DataFrame(
        {"team": matches["home_team"], "goals_for": matches["home_score"], "goals_against": matches["away_score"]}
    )
    away = pd.DataFrame(
        {"team": matches["away_team"], "goals_for": matches["away_score"], "goals_against": matches["home_score"]}
    )
    rows = pd.concat([home, away], ignore_index=True)
    rows["played"] = 1
    rows["won"] = (rows["goals_for"] > rows["goals_against"]).astype(int)
    rows["drawn"] = (rows["goals_for"] == rows["goals_against"]).astype(int)
    rows["lost"] = (rows["goals_for"] < rows["goals_against"]).astype(int)

    table = rows.groupby("team")[["played", "won", "drawn", "lost", "goals_for", "goals_against"]].sum()
    table["points"] = 3 * table["won"] + table["drawn"]
    return table[TABLE_COLUMNS].sort_index()


def reference_problems(reference: pd.DataFrame, n_teams: int, matches_per_team: int) -> list[str]:
    """Check that a league table typed in by hand adds up, before trusting it.

    Every complete league table follows these rules, so a broken rule points to a
    typing mistake (or to an unusual season, for example one with a points deduction).
    Returns one message per problem. An empty list means no problem was found.
    """
    problems = []
    n_unique = reference["team"].nunique()
    if len(reference) != n_teams or n_unique != n_teams:
        problems.append(f"expected {n_teams} different teams, found {n_unique} in {len(reference)} rows")

    for row in reference.itertuples():
        results = row.won + row.drawn + row.lost
        if not row.played == results == matches_per_team:
            problems.append(
                f"{row.team}: played ({row.played}), won + drawn + lost ({results}) "
                f"and {matches_per_team} should all be equal"
            )
        if row.points != 3 * row.won + row.drawn:
            problems.append(f"{row.team}: points ({row.points}) should be 3 x won + drawn ({3 * row.won + row.drawn})")

    # Every match has one winner and one loser, or two teams with a draw.
    if reference["won"].sum() != reference["lost"].sum():
        problems.append(f"total won ({reference['won'].sum()}) should equal total lost ({reference['lost'].sum()})")
    if reference["drawn"].sum() % 2 != 0:
        problems.append(f"total drawn ({reference['drawn'].sum()}) should be even")
    # Every goal scored by one team is a goal conceded by another.
    if reference["goals_for"].sum() != reference["goals_against"].sum():
        problems.append(
            f"total goals scored ({reference['goals_for'].sum()}) should equal "
            f"total goals conceded ({reference['goals_against'].sum()})"
        )
    return problems


def table_differences(a: pd.DataFrame, b: pd.DataFrame) -> list[str]:
    """List every difference between two league tables, team by team.

    Both tables are indexed by team, with StatsBomb's spelling of the names.
    """
    problems = []
    only_a = sorted(set(a.index) - set(b.index))
    only_b = sorted(set(b.index) - set(a.index))
    if only_a or only_b:
        problems.append(f"team names do not match: only in the first table {only_a}, only in the second {only_b}")
    for team in sorted(set(a.index) & set(b.index)):
        for column in TABLE_COLUMNS:
            if a.loc[team, column] != b.loc[team, column]:
                problems.append(f"{team} {column}: {a.loc[team, column]} vs {b.loc[team, column]}")
    return problems


# ---------------------------------------------------------------------------
# The data checks. Each one returns one row of results/data_checks.csv.
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    check: str
    description: str
    passed: bool
    detail: str


def check_season(competitions: list[dict], competition_name: str, season_name: str) -> CheckResult:
    description = f"{competition_name} {season_name} is found by name in competitions.json, exactly once"
    try:
        competition_id, season_id = sbdata.find_season(competitions, competition_name, season_name)
    except ValueError as error:
        return CheckResult("1", description, False, str(error))
    return CheckResult("1", description, True, f"competition_id={competition_id}, season_id={season_id}")


def check_fixtures(matches: pd.DataFrame, n_teams: int) -> CheckResult:
    n_matches, per_team = n_teams * (n_teams - 1), 2 * (n_teams - 1)
    description = (
        f"{n_matches} matches, {n_teams} teams, {per_team} matches per team, "
        "and every team meets every other team once at home and once away"
    )
    counts = pd.concat([matches["home_team"], matches["away_team"]]).value_counts()
    # With no repeated (home, away) pair and no team playing itself, the right
    # number of matches means that every pair met exactly once at each ground.
    pairs_once = not matches.duplicated(["home_team", "away_team"]).any() and bool(
        (matches["home_team"] != matches["away_team"]).all()
    )
    passed = len(matches) == n_matches and len(counts) == n_teams and bool((counts == per_team).all()) and pairs_once
    detail = (
        f"{len(matches)} matches, {len(counts)} teams, {counts.min()} to {counts.max()} matches per team, "
        + ("every home-away pair once" if pairs_once else "some home-away pairs are repeated")
    )
    return CheckResult("2", description, passed, detail)


def check_events_files(matches: pd.DataFrame, n_events: dict[int, int]) -> CheckResult:
    description = "every match has an events file with events in it, and no match appears twice"
    repeated = int(matches["match_id"].duplicated().sum())
    empty = [match_id for match_id in matches["match_id"] if n_events.get(match_id, 0) == 0]
    counts = [n_events.get(match_id, 0) for match_id in matches["match_id"]]
    detail = f"{len(matches)} matches, {repeated} repeated; events per match: {min(counts)} to {max(counts)}"
    if empty:
        detail += f"; matches with no events: {len(empty)} (first ones: {empty[:10]})"
    return CheckResult("3", description, repeated == 0 and not empty, detail)


def check_goals_vs_scores(matches: pd.DataFrame, goals: pd.DataFrame) -> CheckResult:
    description = "goals counted from the events (shots + own goals) = the final score, in every match"
    both = matches.merge(goals, on="match_id")
    wrong = both[
        (both["home_goals_events"] != both["home_score"]) | (both["away_goals_events"] != both["away_score"])
    ]
    from_events = int(both["home_goals_events"].sum() + both["away_goals_events"].sum())
    from_scores = int(both["home_score"].sum() + both["away_score"].sum())
    detail = (
        f"{len(both) - len(wrong)} of {len(matches)} matches agree; "
        f"all goals: {from_events} from the events, {from_scores} from the scores"
    )
    if len(wrong):
        detail += f"; different in matches {wrong['match_id'].tolist()[:10]}"
    return CheckResult("4", description, len(both) == len(matches) and wrong.empty, detail)


def check_references_consistent(
    official: pd.DataFrame, second: pd.DataFrame, n_teams: int, matches_per_team: int
) -> CheckResult:
    description = "each typed-in final table adds up (for example, total goals scored = total goals conceded)"
    problems = [f"Lega Serie A table: {p}" for p in reference_problems(official, n_teams, matches_per_team)]
    problems += [f"RSSSF table: {p}" for p in reference_problems(second, n_teams, matches_per_team)]
    detail = "; ".join(problems) if problems else "both tables add up"
    return CheckResult("5a", description, not problems, detail)


def check_sources_agree(official: pd.DataFrame, second: pd.DataFrame) -> CheckResult:
    description = "the Lega Serie A table and the RSSSF table agree on every number"
    problems = table_differences(official.set_index("team"), second.set_index("team"))
    detail = "; ".join(problems) if problems else f"all {len(official)} teams agree on {len(TABLE_COLUMNS)} columns"
    return CheckResult("5b", description, not problems, detail)


def check_table_vs_official(table: pd.DataFrame, official: pd.DataFrame) -> CheckResult:
    description = "the league table rebuilt from StatsBomb's final scores = the official Lega Serie A table"
    problems = table_differences(table, official.set_index("team"))
    detail = "; ".join(problems) if problems else f"all {len(table)} teams agree on {len(TABLE_COLUMNS)} columns"
    return CheckResult("5c", description, not problems, detail)


def check_xg_range(events: pd.DataFrame) -> CheckResult:
    description = "every shot has an xG value between 0 and 1"
    shots = events[events["type"] == "Shot"]
    bad = shots[shots["xg"].isna() | (shots["xg"] < 0) | (shots["xg"] > 1)]
    detail = f"{len(shots)} shots, {len(bad)} without a valid xG"
    if len(shots):
        detail += f"; xG from {shots['xg'].min():.3f} to {shots['xg'].max():.3f}"
    return CheckResult("6", description, len(shots) > 0 and bad.empty, detail)


def check_team_conceded(
    matches: pd.DataFrame, goals: pd.DataFrame, official: pd.DataFrame, team: str
) -> CheckResult:
    description = f"{team}'s goals conceded counted from the events = the official table"
    both = matches.merge(goals, on="match_id")
    conceded = int(
        both.loc[both["home_team"] == team, "away_goals_events"].sum()
        + both.loc[both["away_team"] == team, "home_goals_events"].sum()
    )
    official_by_team = official.set_index("team")
    if team not in official_by_team.index:
        return CheckResult("7", description, False, f"{team} is not in the official table")
    official_value = int(official_by_team.loc[team, "goals_against"])
    detail = f"{conceded} from the events, {official_value} in the official table"
    return CheckResult("7", description, conceded == official_value, detail)
