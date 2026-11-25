"""The calculations of the third question (PLAN.md section 6c): what is the how part made of?

These functions only calculate. They do not read files, so the key ones can be
tested with tiny hand-built examples (tests/test_how_kinds.py).
"""
import numpy as np
import pandas as pd

# The kinds of the last pass, in the order of PLAN.md section 6c. A pass that is two kinds at once
# (for example a corner that is also a cross) gets the first of them.
CORNER = "corner"
OTHER_SET_PIECE = "another set piece"
CROSS = "cross"
THROUGH_BALL = "through ball"
OTHER_PASS = "any other pass"
NO_PASS = "no pass"
LAST_PASS_KINDS = (CORNER, OTHER_SET_PIECE, CROSS, THROUGH_BALL, OTHER_PASS, NO_PASS)
# StatsBomb's pass types that are set pieces, other than the corner. Its other pass types
# ("Recovery", "Interception") are open play.
OTHER_SET_PIECE_TYPES = ("Free Kick", "Throw-in", "Goal Kick", "Kick Off")
# "Any other pass" is the most common kind, so it is the reference: it has no column of its own (D36),
# and every last-pass coefficient is a difference from it.
REFERENCE = OTHER_PASS

# The columns of the model, and the part of the how part that each one goes to.
HEADER = "header"
PRESSURE = "under pressure"
LAST_PASS = "last pass: "  # the start of the name of each last-pass column
JOINT = "header x under pressure"  # only in the check
PARTS = ["header_part", "pressure_part", "last_pass_part", "rest"]


def last_pass_kind(key_pass: dict | None) -> str:
    """The kind of the pass that StatsBomb links to a shot (its "key pass"), in the order of PLAN.md section 6c.

    key_pass is the "pass" part of that event in the raw file, or None if the shot has no key pass.
    """
    if key_pass is None:
        return NO_PASS
    pass_type = key_pass.get("type", {}).get("name")
    if pass_type == "Corner":
        return CORNER
    if pass_type in OTHER_SET_PIECE_TYPES:
        return OTHER_SET_PIECE
    if key_pass.get("cross"):
        return CROSS
    # StatsBomb marks a through ball in two ways (both are in its open data), so either one counts.
    if key_pass.get("through_ball") or key_pass.get("technique", {}).get("name") == "Through Ball":
        return THROUGH_BALL
    return OTHER_PASS


def kind_columns(shots: pd.DataFrame, with_joint: bool = False) -> pd.DataFrame:
    """The columns of the model: for each shot, 1 if it is of that kind, else 0 (PLAN.md section 6c).

    shots needs "body_part" (StatsBomb's name), "under_pressure" (True or False) and "last_pass" (one of
    LAST_PASS_KINDS). with_joint adds the column of the check: header x under pressure.
    """
    unknown = sorted(set(shots["last_pass"]) - set(LAST_PASS_KINDS))
    if unknown:
        # Without this stop, a misspelt kind would quietly count as the reference.
        raise ValueError(f"Kinds of last pass that the rules do not know: {unknown}")
    columns = pd.DataFrame(index=shots.index)
    # Only "Head" is a header; every other body part (a foot, or "Other") is not (D36).
    columns[HEADER] = (shots["body_part"] == "Head").astype(float)
    columns[PRESSURE] = shots["under_pressure"].astype(bool).astype(float)
    for kind in LAST_PASS_KINDS:
        if kind != REFERENCE:
            columns[LAST_PASS + kind] = (shots["last_pass"] == kind).astype(float)
    if with_joint:
        columns[JOINT] = columns[HEADER] * columns[PRESSURE]
    return columns


def centre_in_zones(columns: pd.DataFrame, zones: pd.Series) -> pd.DataFrame:
    """Each column minus the league's average of that column in the shot's zone.

    For a yes-or-no column this is 1 or 0 minus the league's share of that kind in the zone, so the model
    compares each shot only with the league's shots from the same zone (PLAN.md section 6c).
    """
    return columns - columns.groupby(zones).transform("mean")


def fit(how: pd.Series, centred: pd.DataFrame) -> pd.Series:
    """The coefficients of the straight-line model, fitted by least squares with no constant term (D36).

    Inside each zone, the how part and every centred column already average zero, so a constant would be 0.
    Stops if a column adds nothing to the others (for example a kind that no shot has), because then
    its coefficient could be any number.
    """
    x = centred.to_numpy(dtype=float)
    coefficients, _, rank, _ = np.linalg.lstsq(x, how.to_numpy(dtype=float), rcond=None)
    if rank < x.shape[1]:
        raise ValueError(f"The {x.shape[1]} columns of the model tell only {rank} different things: {list(centred)}")
    return pd.Series(coefficients, index=centred.columns)


def shot_parts(centred: pd.DataFrame, coefficients: pd.Series, how: pd.Series) -> pd.DataFrame:
    """Each shot's how part split into the header part, the pressure part, the last-pass part and the rest.

    The part of a column is its coefficient x the shot's centred value (PLAN.md section 6c). The part of
    header x under pressure (the check) is split half and half between the header part and the pressure part.
    Rest = how part - the three parts, so the four parts add up to the how part exactly.
    """
    if list(coefficients.index) != list(centred.columns):
        raise ValueError("The coefficients are not for the same columns as the shots")
    unknown = [c for c in centred.columns if c not in (HEADER, PRESSURE, JOINT) and not c.startswith(LAST_PASS)]
    if unknown:
        # Without this stop, a column with another name would quietly end up in the rest.
        raise ValueError(f"Columns that belong to no part: {unknown}")
    each = centred * coefficients
    joint = each[JOINT] if JOINT in each else 0.0
    parts = pd.DataFrame(index=centred.index)
    parts["header_part"] = each[HEADER] + joint / 2
    parts["pressure_part"] = each[PRESSURE] + joint / 2
    parts["last_pass_part"] = each[[c for c in each.columns if c.startswith(LAST_PASS)]].sum(axis=1)
    parts["rest"] = how - parts["header_part"] - parts["pressure_part"] - parts["last_pass_part"]
    return parts[PARTS]
