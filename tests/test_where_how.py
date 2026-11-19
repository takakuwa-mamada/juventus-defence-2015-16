"""Tests for the key calculations of the second question (PLAN.md section 6b, D11).

Each test uses a tiny hand-built example where the right answer is known in advance.
Run from the project root:
    .venv\\Scripts\\python -m pytest
"""
import math

import numpy as np
import pandas as pd
import pytest

import where_how


def player(x, y, teammate=False, position="Center Back"):
    """One player of a freeze frame, in the same shape as StatsBomb's raw events files."""
    return {
        "location": [x, y],
        "player": {"id": 1, "name": "Someone"},
        "position": {"id": 1 if position == "Goalkeeper" else 3, "name": position},
        "teammate": teammate,
    }


def test_distance_to_the_centre_of_the_goal():
    # The penalty spot is 12 yards straight out; (117, 44) is 3 yards out and 4 to the side (3-4-5).
    distance = where_how.goal_distance(np.array([108.0, 117.0]), np.array([40.0, 44.0]))
    assert distance == pytest.approx([12.0, 5.0])


def test_angle_between_the_lines_to_the_posts():
    x = np.array([108.0, 116.0, 110.0, 110.0, 120.0, 120.0])
    y = np.array([40.0, 36.0, 30.0, 50.0, 30.0, 40.0])
    angle = where_how.goal_angle(x, y)
    # Penalty spot: each post is 4 yards to the side and 12 ahead, so 2 x atan(4/12) = 36.87 degrees.
    assert angle[0] == pytest.approx(36.8699, abs=1e-4)
    # Level with a post, 4 yards out: atan(8/4) = 63.43 degrees.
    assert angle[1] == pytest.approx(63.4349, abs=1e-4)
    # The same distance to the left and to the right gives the same angle: atan(14/10) - atan(6/10).
    assert angle[2] == pytest.approx(23.4986, abs=1e-4)
    assert angle[3] == pytest.approx(angle[2])
    # On the goal line: outside the posts the goal cannot be seen (0); between them it is wide open (180).
    assert angle[4] == pytest.approx(0.0)
    assert angle[5] == pytest.approx(180.0)


def test_defenders_in_the_way_are_outfield_opponents_inside_the_triangle():
    # A shot from the penalty spot: the triangle has its corners at (108, 40), (120, 36) and (120, 44).
    frame = [
        player(114, 40),  # inside: counts
        player(114, 38),  # on the edge from the ball to the post at y = 36: counts
        player(120, 42),  # on the goal line between the posts, also an edge: counts
        player(114, 37.9),  # just outside that edge
        player(105, 40),  # behind the ball
        player(119, 40, position="Goalkeeper"),  # inside, but the goalkeeper is not counted
        player(116, 40, teammate=True),  # inside, but a team-mate of the shooter is not a defender
    ]
    assert where_how.defenders_in_the_way(frame, 108.0, 40.0) == 3


def test_defenders_in_the_way_of_a_shot_from_the_goal_line():
    # From (120, 30) the three corners are on the goal line, so the "triangle" is the line from y = 30 to y = 44.
    frame = [player(120, 40), player(120, 50), player(119, 40)]
    assert where_how.defenders_in_the_way(frame, 120.0, 30.0) == 1


def test_nearest_defender_leaves_out_the_goalkeeper_and_team_mates():
    frame = [
        player(111, 44),  # 5 yards from the ball (3-4-5)
        player(100, 40),  # 8 yards
        player(109, 40, position="Goalkeeper"),  # 1 yard, but the goalkeeper
        player(108, 41, teammate=True),  # 1 yard, but a team-mate of the shooter
    ]
    assert where_how.nearest_defender(frame, 108.0, 40.0) == pytest.approx(5.0)
    # With no outfield defender in the frame, there is no distance.
    assert math.isnan(where_how.nearest_defender(frame[2:], 108.0, 40.0))


def test_zones_split_by_distance_then_by_angle():
    # 30 shots at distances 1 to 30, so each of the 10 distance groups has 3 shots.
    # Inside each group the angles are base + 2, base and base + 1 degrees, so each of the 3 angle groups
    # has 1 shot. As on a real pitch, farther shots have narrower angles (base 100 for the nearest group,
    # 10 for the farthest), so angle groups cut over all 30 shots at once would give other zones.
    distance = np.arange(1.0, 31.0)
    angle = np.repeat(np.arange(100.0, 0.0, -10.0), 3) + np.tile([2.0, 0.0, 1.0], 10)
    # Zone = 3 x distance group + angle group: the nearest group is zones 0-2, the farthest 27-29.
    expected = [2, 0, 1, 5, 3, 4, 8, 6, 7, 11, 9, 10, 14, 12, 13,
                17, 15, 16, 20, 18, 19, 23, 21, 22, 26, 24, 25, 29, 27, 28]
    zones = where_how.place_zones(pd.Series(distance), pd.Series(angle), n_distance=10, n_angle=3)
    assert zones.tolist() == expected

    # The order of the shots must not change any zone.
    order = np.random.default_rng(0).permutation(30)
    shuffled = where_how.place_zones(pd.Series(distance[order]), pd.Series(angle[order]), n_distance=10, n_angle=3)
    assert shuffled.tolist() == [expected[i] for i in order]


def test_shots_without_a_place_are_found():
    shots = pd.DataFrame(
        {
            "x": [108.0, None, 100.0, 100.0, 100.0],
            "y": [40.0, None, 30.0, 30.0, 30.0],
            # A frame can be missing as None or as NaN (for example after a merge), or be an empty list.
            "freeze_frame": [[player(114, 40)], [player(114, 40)], None, [], float("nan")],
        }
    )
    assert where_how.shots_without_a_place(shots).index.tolist() == [1, 2, 3, 4]
