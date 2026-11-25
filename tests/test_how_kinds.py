"""Tests for the key calculations of the third question (PLAN.md section 6c, D11).

Each test uses a tiny hand-built example where the right answer is known in advance.
Run from the project root:
    .venv\\Scripts\\python -m pytest
"""
import pandas as pd
import pytest

import how_kinds
import sbdata
import where_how

# The columns of the model, in this order (PLAN.md section 6c). "Any other pass" is the reference, so it has none.
MODEL_COLUMNS = [
    "header",
    "under pressure",
    "last pass: corner",
    "last pass: another set piece",
    "last pass: cross",
    "last pass: through ball",
    "last pass: no pass",
]


def test_last_pass_kinds_follow_the_order_of_the_rules():
    kind = how_kinds.last_pass_kind
    assert kind(None) == "no pass"  # no key pass: for example a dribble, a rebound or a direct free kick
    # A corner that is also a cross is a corner, and a free kick that is also a cross is another set piece.
    assert kind({"type": {"name": "Corner"}, "cross": True, "technique": {"name": "Inswinging"}}) == "corner"
    assert kind({"type": {"name": "Free Kick"}, "cross": True}) == "another set piece"
    for set_piece in ["Throw-in", "Goal Kick", "Kick Off"]:
        assert kind({"type": {"name": set_piece}}) == "another set piece"
    # A cross that is also a through ball is a cross.
    assert kind({"cross": True, "through_ball": True}) == "cross"
    # StatsBomb marks a through ball in two ways; either one counts.
    assert kind({"through_ball": True}) == "through ball"
    assert kind({"technique": {"name": "Through Ball"}}) == "through ball"
    # An ordinary pass has no type. A pass right after winning the ball back is not a set piece.
    assert kind({}) == "any other pass"
    assert kind({"type": {"name": "Recovery"}}) == "any other pass"
    assert kind({"cut_back": True}) == "any other pass"


def test_model_columns_are_one_or_zero_and_the_reference_has_none():
    shots = pd.DataFrame(
        {
            "body_part": ["Head", "Right Foot", "Other", "Head"],
            "under_pressure": [True, False, True, False],
            "last_pass": ["corner", "any other pass", "no pass", "cross"],
        }
    )
    columns = how_kinds.kind_columns(shots)
    assert columns.columns.tolist() == MODEL_COLUMNS
    assert columns["header"].tolist() == [1, 0, 0, 1]  # only "Head" is a header; "Other" is not
    assert columns["under pressure"].tolist() == [1, 0, 1, 0]
    assert columns["last pass: corner"].tolist() == [1, 0, 0, 0]
    assert columns["last pass: another set piece"].tolist() == [0, 0, 0, 0]
    assert columns["last pass: cross"].tolist() == [0, 0, 0, 1]
    assert columns["last pass: through ball"].tolist() == [0, 0, 0, 0]
    assert columns["last pass: no pass"].tolist() == [0, 0, 1, 0]
    # The check adds header x under pressure: 1 only for a header under pressure.
    check = how_kinds.kind_columns(shots, with_joint=True)
    assert check.columns.tolist() == MODEL_COLUMNS + ["header x under pressure"]
    assert check["header x under pressure"].tolist() == [1, 0, 0, 0]
    # A kind of last pass that the rules do not know stops the calculation, instead of counting as no column.
    with pytest.raises(ValueError):
        how_kinds.kind_columns(shots.assign(last_pass=["corner", "long ball", "no pass", "cross"]))


def test_columns_are_compared_inside_the_zones():
    columns = pd.DataFrame({"header": [1.0, 0.0, 1.0, 1.0], "under pressure": [1.0, 1.0, 0.0, 1.0]})
    zones = pd.Series([0, 0, 1, 1])
    centred = how_kinds.centre_in_zones(columns, zones)
    # Zone 0: half of its shots are headers, so 1 - 0.5 and 0 - 0.5. Zone 1: all are headers, so 0 and 0.
    assert centred["header"].tolist() == pytest.approx([0.5, -0.5, 0.0, 0.0])
    # Zone 0: all are under pressure. Zone 1: half are.
    assert centred["under pressure"].tolist() == pytest.approx([0.0, 0.0, -0.5, 0.5])


def test_fit_finds_what_each_kind_changes_when_the_other_kinds_are_the_same():
    # 8 shots in 2 zones. Each xG is the zone's base (0.10 or 0.30), minus 0.06 for a header and
    # minus 0.02 under pressure, so the right coefficients are known in advance: -0.06 and -0.02.
    zones = pd.Series([0, 0, 0, 0, 1, 1, 1, 1])
    columns = pd.DataFrame(
        {
            "header": [1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            "under pressure": [1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0],
        }
    )
    xg = pd.Series([0.02, 0.04, 0.10, 0.10, 0.22, 0.28, 0.30, 0.30])
    how = xg - where_how.zone_average(xg, zones)
    coefficients = how_kinds.fit(how, how_kinds.centre_in_zones(columns, zones))
    # The headers were more often under pressure, so inside each zone they are about 0.07 below the other
    # shots. The model splits this into what the header does and what the pressure does.
    assert coefficients.index.tolist() == ["header", "under pressure"]
    assert coefficients.tolist() == pytest.approx([-0.06, -0.02])


def test_fit_stops_when_a_column_tells_nothing_new():
    zones = pd.Series([0, 0, 1, 1])
    how = pd.Series([-0.01, 0.01, 0.02, -0.02])
    header = pd.Series([1.0, 0.0, 0.0, 1.0])
    # A kind that no shot has (for example after a misspelt name) gives a column of zeros.
    no_shot = how_kinds.centre_in_zones(pd.DataFrame({"header": header, "last pass: through ball": 0.0}), zones)
    with pytest.raises(ValueError):
        how_kinds.fit(how, no_shot)
    # Two columns that are always the same cannot be told apart.
    twins = how_kinds.centre_in_zones(pd.DataFrame({"header": header, "under pressure": header}), zones)
    with pytest.raises(ValueError):
        how_kinds.fit(how, twins)


def test_parts_and_the_rest_add_up_to_the_how_part():
    centred = pd.DataFrame(
        {
            "header": [0.5, -0.5],
            "under pressure": [0.75, -0.25],
            "last pass: corner": [0.4, -0.4],
            "last pass: cross": [-0.2, 0.2],
        }
    )
    coefficients = pd.Series(
        {"header": -0.06, "under pressure": -0.02, "last pass: corner": -0.08, "last pass: cross": -0.03}
    )
    how = pd.Series([-0.10, 0.05])
    parts = how_kinds.shot_parts(centred, coefficients, how)
    assert parts.columns.tolist() == ["header_part", "pressure_part", "last_pass_part", "rest"]
    # Shot 0: header -0.06 x 0.5; pressure -0.02 x 0.75; last pass -0.08 x 0.4 + (-0.03) x (-0.2) = -0.026;
    # rest -0.10 - (-0.03 - 0.015 - 0.026).
    assert parts.iloc[0].tolist() == pytest.approx([-0.03, -0.015, -0.026, -0.029])
    # Shot 1: header -0.06 x (-0.5); pressure -0.02 x (-0.25); last pass -0.08 x (-0.4) + (-0.03) x 0.2 = 0.026;
    # rest 0.05 - (0.03 + 0.005 + 0.026).
    assert parts.iloc[1].tolist() == pytest.approx([0.03, 0.005, 0.026, -0.011])
    assert parts.sum(axis=1).tolist() == pytest.approx(how.tolist())


def test_the_joint_part_is_split_half_and_half():
    centred = pd.DataFrame({"header": [0.5], "under pressure": [0.75], "header x under pressure": [0.6]})
    coefficients = pd.Series({"header": -0.04, "under pressure": -0.01, "header x under pressure": -0.05})
    how = pd.Series([-0.08])
    parts = how_kinds.shot_parts(centred, coefficients, how)
    # The joint part is -0.05 x 0.6 = -0.03: half of it goes to the header part, half to the pressure part.
    # Header -0.04 x 0.5 - 0.015; pressure -0.01 x 0.75 - 0.015; no last-pass column; rest -0.08 - (-0.0575).
    assert parts.iloc[0].tolist() == pytest.approx([-0.035, -0.0225, 0.0, -0.0225])
    # A column that belongs to no part, or coefficients for other columns, stop the calculation.
    with pytest.raises(ValueError):
        how_kinds.shot_parts(
            centred.rename(columns={"header": "heading"}), coefficients.rename({"header": "heading"}), how
        )
    with pytest.raises(ValueError):
        how_kinds.shot_parts(centred, coefficients.drop("header x under pressure"), how)


def test_the_key_pass_is_found_in_the_same_match():
    def event(event_id, kind, **parts):
        return {"id": event_id, "type": {"name": kind}, "team": {"name": "A"}, **parts}

    def shot(event_id, key_pass_id=None, body_part="Right Foot", **parts):
        details = {"type": {"name": "Open Play"}, "statsbomb_xg": 0.1, "body_part": {"name": body_part}}
        if key_pass_id is not None:
            details["key_pass_id"] = key_pass_id
        return event(event_id, "Shot", location=[110.0, 40.0], shot=details, **parts)

    events = [
        event("p1", "Pass", **{"pass": {"cross": True}}),
        shot("s1", key_pass_id="p1", body_part="Head", under_pressure=True),
        shot("s2"),
    ]
    rows = sbdata.shot_kind_rows(events, match_id=7)
    assert [row["key_pass"] for row in rows] == [{"cross": True}, None]
    assert [row["body_part"] for row in rows] == ["Head", "Right Foot"]
    # StatsBomb leaves the mark out when a shot is not under pressure.
    assert [row["under_pressure"] for row in rows] == [True, False]
    # A key pass that is not a pass of the same match stops the calculation (D36).
    with pytest.raises(ValueError):
        sbdata.shot_kind_rows([shot("s3", key_pass_id="p9")], match_id=7)
    with pytest.raises(ValueError):
        sbdata.shot_kind_rows([event("c1", "Carry"), shot("s4", key_pass_id="c1")], match_id=7)
