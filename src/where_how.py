"""The calculations of the second question (PLAN.md section 6b): where the shots were taken, and how.

These functions only calculate. They do not read files, so the key ones can be
tested with tiny hand-built examples (tests/test_where_how.py).
"""
import math

import numpy as np
import pandas as pd

# StatsBomb's pitch is 120 x 80 yards, and every team shoots at the goal at x = 120.
GOAL_X = 120.0
GOAL_CENTRE_Y = 40.0
POST_YS = (36.0, 44.0)
# A player exactly on an edge of the triangle counts (PLAN.md section 6b). Positions have one decimal
# place, which a computer cannot always store exactly, so a tiny margin keeps such a player from being lost.
EDGE_MARGIN = 1e-9


def goal_distance(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Distance in yards from where the shot was taken to the centre of the goal."""
    return np.hypot(GOAL_X - x, GOAL_CENTRE_Y - y)


def goal_angle(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """The angle in degrees between the lines from the shot to the two posts: how wide the goal looks."""
    # arctan2 gives the direction of each line; the angle between them is the difference.
    to_one_post = np.arctan2(POST_YS[0] - y, GOAL_X - x)
    to_other_post = np.arctan2(POST_YS[1] - y, GOAL_X - x)
    return np.degrees(np.abs(to_other_post - to_one_post))


def is_defender(player: dict) -> bool:
    """An outfield player of the team that conceded the shot.

    In a freeze frame, "teammate" is about the shooter: False means the other team.
    The goalkeeper is left out, because the goalkeeper's play is kept apart from how the team defended (D30).
    """
    return not player["teammate"] and player["position"]["name"] != "Goalkeeper"


def side_of_line(a: tuple, b: tuple, x: float, y: float) -> float:
    """Above 0 if the point is on the left of the line from a to b, below 0 on the right, 0 on the line."""
    return (b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0])


def in_triangle(x: float, y: float, corners: tuple) -> bool:
    """True if the point is inside the triangle or on one of its edges."""
    a, b, c = corners
    sides = (side_of_line(a, b, x, y), side_of_line(b, c, x, y), side_of_line(c, a, x, y))
    # Inside means on the same side of all three edges (on an edge counts).
    same_side = all(s >= -EDGE_MARGIN for s in sides) or all(s <= EDGE_MARGIN for s in sides)
    # When the ball is on the goal line, the three corners are on one line, and every point of that line
    # would pass the test above. Only the points between the corners are part of the "triangle".
    xs, ys = [corner[0] for corner in corners], [corner[1] for corner in corners]
    between = (min(xs) - EDGE_MARGIN <= x <= max(xs) + EDGE_MARGIN) and (min(ys) - EDGE_MARGIN <= y <= max(ys) + EDGE_MARGIN)
    return same_side and between


def defenders_in_the_way(frame: list[dict], x: float, y: float) -> int:
    """How many outfield defenders stand inside the triangle between the ball and the two posts."""
    corners = ((x, y), (GOAL_X, POST_YS[0]), (GOAL_X, POST_YS[1]))
    return sum(1 for player in frame if is_defender(player) and in_triangle(*player["location"][:2], corners))


def nearest_defender(frame: list[dict], x: float, y: float) -> float:
    """Distance in yards from the ball to the nearest outfield defender (NaN if the frame shows none)."""
    distances = [
        math.hypot(player["location"][0] - x, player["location"][1] - y) for player in frame if is_defender(player)
    ]
    return min(distances) if distances else math.nan


def place_zones(distance: pd.Series, angle: pd.Series, n_distance: int, n_angle: int) -> pd.Series:
    """Put every shot in a zone: first n_distance groups of the same size by distance, then n_angle groups by angle.

    Zone = n_angle x distance group + angle group, so zone 0 is the nearest group with the narrowest angle.
    Groups are cut at the values, so two shots at the same distance are always in the same group.
    """
    distance_group = pd.qcut(distance, n_distance, labels=False)
    angle_group = angle.groupby(distance_group).transform(lambda a: pd.qcut(a, n_angle, labels=False))
    return (n_angle * distance_group + angle_group).astype(int)


def shots_without_a_place(shots: pd.DataFrame) -> pd.DataFrame:
    """The shots that have no location or no freeze frame. The rules say to stop if there is one (PLAN.md 6b)."""
    no_location = shots["x"].isna() | shots["y"].isna()
    # A missing frame can be None or NaN, and an empty list shows no player: all three count as no frame.
    no_frame = shots["freeze_frame"].map(lambda frame: not isinstance(frame, list) or len(frame) == 0)
    return shots[no_location | no_frame]
