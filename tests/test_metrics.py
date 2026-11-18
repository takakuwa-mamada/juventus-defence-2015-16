"""Tests for the key calculations of the measures (D11).

Each test uses a tiny hand-built example where the right answer is known in advance.
Run from the project root:
    .venv\\Scripts\\python -m pytest
"""
import numpy as np
import pandas as pd
import pytest

import metrics
import sbdata

# One match, A (home) v B (away).
ONE_MATCH = pd.DataFrame(
    {"match_id": [1], "home_team": ["A"], "away_team": ["B"], "home_score": [3], "away_score": [0]}
)


def shot(team, outcome, xg, shot_type="Open Play"):
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


def test_conceded_counts_go_to_the_opponent():
    raw_events = [
        shot("A", "Goal", 0.3),
        shot("A", "Saved", 0.1),
        shot("A", "Goal", 0.78, shot_type="Penalty"),
        shot("B", "Off T", 0.05),
        # B's player scores into B's own goal: StatsBomb records it for both teams.
        own_goal("B", "Own Goal Against"),
        own_goal("A", "Own Goal For"),
    ]
    events = pd.DataFrame(sbdata.shot_and_own_goal_rows(raw_events, match_id=1))

    # Main numbers: no penalties. A's shots are shots that B conceded.
    main = metrics.conceded_table(ONE_MATCH, events, include_penalties=False)
    assert main.loc["B", ["matches", "shots", "goals", "own_goals"]].tolist() == [1, 2, 1, 1]
    assert main.loc["B", "xg"] == pytest.approx(0.4)
    assert main.loc["A", ["matches", "shots", "goals", "own_goals"]].tolist() == [1, 1, 0, 0]
    assert main.loc["A", "xg"] == pytest.approx(0.05)

    # The check with penalties adds the penalty to B's numbers.
    with_penalties = metrics.conceded_table(ONE_MATCH, events, include_penalties=True)
    assert with_penalties.loc["B", ["shots", "goals"]].tolist() == [3, 2]
    assert with_penalties.loc["B", "xg"] == pytest.approx(1.18)


def test_replay_is_repeatable_with_known_extremes():
    xg = np.array([0.1, 0.5, 0.9])
    first = metrics.replay_goals(xg, n_replays=1000, seed=7)
    second = metrics.replay_goals(xg, n_replays=1000, seed=7)
    # The same seed gives exactly the same replays.
    assert np.array_equal(first, second)
    assert len(first) == 1000
    # Shots with xG 0 never score; shots with xG 1 always score.
    assert (metrics.replay_goals(np.zeros(4), n_replays=100, seed=7) == 0).all()
    assert (metrics.replay_goals(np.ones(5), n_replays=100, seed=7) == 5).all()


def test_opponent_possessions():
    raw_events = []
    for possession, team in [(1, "A"), (2, "B"), (3, "A"), (4, "B"), (5, "B")]:
        for _ in range(3):  # several events in one possession: the possession counts once
            raw_events.append({"type": {"name": "Pass"}, "team": {"name": team},
                               "possession": possession, "possession_team": {"name": team}})
    # An event by A during B's possession (for example a tackle) does not make it A's possession.
    raw_events.append({"type": {"name": "Pressure"}, "team": {"name": "A"},
                       "possession": 2, "possession_team": {"name": "B"}})

    possessions = pd.DataFrame(sbdata.possession_rows(raw_events, match_id=1))
    assert possessions.set_index("team").loc[["A", "B"], "possessions"].tolist() == [2, 3]

    opponent = metrics.opponent_possessions(ONE_MATCH, possessions)
    assert opponent["A"] == 3  # A defended against B's 3 possessions
    assert opponent["B"] == 2


def test_rank_lowest_with_a_shared_first():
    values = pd.Series({"A": 1.0, "B": 1.0, "C": 2.0})
    assert metrics.rank_lowest(values, "A") == (1, True)
    assert metrics.rank_lowest(values, "C") == (3, False)
