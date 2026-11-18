"""Tests for the key calculations (D11).

Each test uses a tiny hand-built example where the right answer is known in
advance, so a mistake in the calculation shows up as a failed test.
Run from the project root:
    .venv\\Scripts\\python -m pytest
"""
import pandas as pd

import checks
import sbdata


def shot(team, outcome, xg=0.1, shot_type="Open Play"):
    """A shot event in the same shape as StatsBomb's raw events files."""
    return {
        "type": {"name": "Shot"},
        "team": {"name": team},
        "period": 1,
        "minute": 10,
        "shot": {"outcome": {"name": outcome}, "type": {"name": shot_type}, "statsbomb_xg": xg},
    }


def own_goal(team, kind):
    """An own-goal event. kind is "Own Goal For" or "Own Goal Against"."""
    return {"type": {"name": kind}, "team": {"name": team}, "period": 2, "minute": 70}


def test_goals_count_shots_and_own_goals():
    matches = pd.DataFrame(
        {
            "match_id": [1, 2],
            "home_team": ["Home", "Home"],
            "away_team": ["Away", "Away"],
            "home_score": [3, 0],
            "away_score": [0, 0],
        }
    )
    raw_events = [
        shot("Home", "Goal"),
        shot("Home", "Goal", xg=0.76, shot_type="Penalty"),
        shot("Home", "Saved"),
        shot("Away", "Off T"),
        # StatsBomb records one own goal twice: once for each team.
        own_goal("Away", "Own Goal Against"),
        own_goal("Home", "Own Goal For"),
        {"type": {"name": "Pass"}, "team": {"name": "Home"}, "period": 1, "minute": 1},
    ]
    events = pd.DataFrame(sbdata.shot_and_own_goal_rows(raw_events, match_id=1))

    goals = checks.goals_per_match(matches, events).set_index("match_id")

    # 2 goals from shots + 1 own goal = 3, and the own goal is counted only once.
    assert goals.loc[1, "home_goals_events"] == 3
    assert goals.loc[1, "away_goals_events"] == 0
    # A match with no goal events still gets a row, with 0 goals.
    assert goals.loc[2, "home_goals_events"] == 0
    assert goals.loc[2, "away_goals_events"] == 0


def three_matches():
    """A 2-0 B, B 1-1 C, C 0-3 A."""
    return pd.DataFrame(
        {
            "match_id": [1, 2, 3],
            "home_team": ["A", "B", "C"],
            "away_team": ["B", "C", "A"],
            "home_score": [2, 1, 0],
            "away_score": [0, 1, 3],
        }
    )


def test_league_table_points_and_goals():
    table = checks.league_table(three_matches())
    columns = ["played", "won", "drawn", "lost", "goals_for", "goals_against", "points"]

    assert table.loc["A", columns].tolist() == [2, 2, 0, 0, 5, 0, 6]
    assert table.loc["B", columns].tolist() == [2, 0, 1, 1, 1, 3, 1]
    assert table.loc["C", columns].tolist() == [2, 0, 1, 1, 1, 4, 1]


def test_reference_check_finds_a_typo():
    reference = checks.league_table(three_matches()).reset_index()
    assert checks.reference_problems(reference, n_teams=3, matches_per_team=2) == []

    # A typing mistake: A scored 5 goals, not 6.
    reference.loc[reference["team"] == "A", "goals_for"] = 6
    problems = checks.reference_problems(reference, n_teams=3, matches_per_team=2)
    assert len(problems) == 1
    assert "goals" in problems[0]
