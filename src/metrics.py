"""The measures of PLAN.md section 6, for every team.

These functions only calculate. They do not read files, so the key ones can be
tested with tiny hand-built examples (tests/test_metrics.py).
"""
import numpy as np
import pandas as pd


def opponents(matches: pd.DataFrame) -> pd.DataFrame:
    """One row per team per match: match_id, team, opponent."""
    columns = ["match_id", "team", "opponent"]
    home = matches[["match_id", "home_team", "away_team"]].set_axis(columns, axis=1)
    away = matches[["match_id", "away_team", "home_team"]].set_axis(columns, axis=1)
    return pd.concat([home, away], ignore_index=True)


def conceded_shots(matches: pd.DataFrame, events: pd.DataFrame, include_penalties: bool) -> pd.DataFrame:
    """One row per shot, with the team that conceded it in the column "conceded_by".

    A shot by one team is a shot conceded by the other team in the same match.
    """
    shots = events[events["type"] == "Shot"]
    if not include_penalties:
        shots = shots[shots["shot_type"] != "Penalty"]
    pairs = opponents(matches).rename(columns={"opponent": "conceded_by"})
    conceded = shots.merge(pairs, on=["match_id", "team"], validate="many_to_one")
    # A shot by a team that did not play in that match would be dropped without a word. Stop instead.
    if len(conceded) != len(shots):
        raise ValueError(f"{len(shots) - len(conceded)} shots were made by a team that did not play in that match")
    return conceded


def conceded_table(matches: pd.DataFrame, events: pd.DataFrame, include_penalties: bool) -> pd.DataFrame:
    """Shots, xG and goals that each team conceded, and the own goals it conceded.

    Goals here are goals from shots. Own goals are counted on their own, because
    they are not shots and have no xG (D18).
    """
    shots = conceded_shots(matches, events, include_penalties).assign(is_goal=lambda d: d["shot_outcome"] == "Goal")
    by_team = shots.groupby("conceded_by").agg(shots=("is_goal", "size"), xg=("xg", "sum"), goals=("is_goal", "sum"))
    # "Own Goal Against" is recorded for the team that conceded the own goal.
    own_goals = events[events["type"] == "Own Goal Against"].groupby("team").size()

    table = opponents(matches).groupby("team").size().rename("matches").to_frame()
    table = table.join(by_team).fillna({"shots": 0, "xg": 0.0, "goals": 0})
    table["own_goals"] = own_goals.reindex(table.index, fill_value=0)
    return table.astype({"matches": int, "shots": int, "goals": int, "own_goals": int})


def opponent_possessions(matches: pd.DataFrame, possessions: pd.DataFrame) -> pd.Series:
    """For each team, the number of possessions its opponents had over the season.

    These are the opponents' chances to attack. "Shots conceded per 100 opponent
    possessions" shows how often an opponent's possession ended in a shot, whatever
    the number of possessions (D19). It counts possessions; it does not measure
    the share of time on the ball.
    """
    pairs = opponents(matches)
    merged = pairs.merge(
        possessions, left_on=["match_id", "opponent"], right_on=["match_id", "team"], suffixes=("", "_of_opponent")
    )
    return merged.groupby("team")["possessions"].sum()


def replay_goals(xg: np.ndarray, n_replays: int, seed: int) -> np.ndarray:
    """Replay a set of shots many times and return the number of goals in each replay.

    In each replay, every shot becomes a goal with a probability equal to its xG,
    independently of the other shots (D17). A fixed seed gives the same replays
    every time.
    """
    rng = np.random.default_rng(seed)
    # One row per replay, one column per shot: True where the shot became a goal.
    is_goal = rng.random((n_replays, len(xg))) < np.asarray(xg)
    return is_goal.sum(axis=1)


def ranks_lowest_first(values: pd.Series) -> pd.Series:
    """Every team's rank, 1 = lowest. Teams with the same value share the best of their ranks."""
    return values.rank(method="min").astype(int)


def rank_lowest(values: pd.Series, team: str) -> tuple[int, bool]:
    """The team's rank when the lowest value is 1st, and whether another team has the same rank."""
    ranks = ranks_lowest_first(values)
    rank = int(ranks[team])
    return rank, int((ranks == rank).sum()) > 1
