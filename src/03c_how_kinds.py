"""Step 3c: the third question (PLAN.md section 6c). What is the how part made of?

Run from the project root:
    .venv\\Scripts\\python src\\03c_how_kinds.py

The rules were fixed and published before this script was first run (PLAN.md
section 6c, DECISIONS.md D35-D36). This script only applies them. It writes three
tables in results/:
- how_kinds_league.csv: for each kind of shot, how many of the league's shots are of that kind,
  their average how part, and the coefficient of the straight-line model (and of the model of the check).
- how_kinds_teams.csv: for every team, its how part split into the header part, the pressure part,
  the last-pass part and the rest (also with the model of the check), with ranks, and how many more
  shots of each kind it faced than the league's shots from the same zones ("extra_", per shot);
- how_kinds_tests.csv: each part for Juventus, its rule and the result.
"""
import sys

import numpy as np
import pandas as pd

import how_kinds
import metrics
import sbdata
import where_how
from config import (
    COMPETITION_NAME,
    MOST_OF_THE_HOW_PART,
    N_ANGLE_GROUPS,
    N_DISTANCE_GROUPS,
    N_RANDOM_SETS,
    RESULTS_DIR,
    ROOT,
    SEASON_NAME,
    SEED,
    SUPPORTED_SHARE,
    TEAM,
)

# The rows of how_kinds_league.csv, in the order of PLAN.md section 6c. "Any other pass" has a row but no
# column in the model (it is the reference), and header x under pressure is a column of the check only.
KIND_ROWS = (
    [how_kinds.HEADER, how_kinds.PRESSURE]
    + [how_kinds.LAST_PASS + kind for kind in how_kinds.LAST_PASS_KINDS]
    + [how_kinds.JOINT]
)
NOTES = {
    how_kinds.LAST_PASS + how_kinds.REFERENCE: "the reference: each last-pass coefficient is a difference from it",
    how_kinds.JOINT: "only in the model of the check",
}

# The start of the name of each column made with the model of the check.
CHECK = "check_"
# The three parts that are judged: the name of the row in how_kinds_tests.csv, the words for it in the
# results, and what it measures.
JUDGED = {
    "header_part": ("header", "header", "header part: the header coefficient x (header or not, minus the league's "
                    "share of headers in the zone), per shot conceded"),
    "pressure_part": ("pressure", "pressure", "pressure part: the pressure coefficient x (under pressure or not, "
                      "minus the league's share in the zone), per shot conceded"),
    "last_pass_part": ("last pass", "last-pass", "last-pass part: the same for the five kinds of last pass, "
                       "added up, per shot conceded"),
}

# The rules of PLAN.md section 6c, written from the settings in config.py.
RANDOM_SETS_TEXT = (
    f"{N_RANDOM_SETS:,} random sets of whole team-matches (seed {SEED}), each with at least as many shots "
    f"as {TEAM} conceded (the same sets as in section 6b)"
)
CHECK_TEXT = (
    "in the model with one more column, header x under pressure, whose part is split half and half "
    "between the header part and the pressure part"
)
EXPECTATION_RULE = (
    f"most: the three parts together are at least {MOST_OF_THE_HOW_PART:.0%} (two thirds) of {TEAM}'s how part (D36)"
)
SHOWN_ONLY = "shown, not judged"


def part_rule(words: str) -> str:
    return (
        f"supported if fewer than {SUPPORTED_SHARE:.0%} of {RANDOM_SETS_TEXT} have a {words} part "
        f"as low as {TEAM}'s, or lower"
    )


def main() -> int:
    competitions = sbdata.read_json("competitions.json")
    competition_id, season_id = sbdata.find_season(competitions, COMPETITION_NAME, SEASON_NAME)
    matches = sbdata.matches_table(sbdata.read_json(f"matches/{competition_id}/{season_id}.json"))
    print(f"Reading the shots of {len(matches)} matches...", flush=True)
    all_shots = sbdata.load_shot_kinds(matches["match_id"].tolist())
    all_shots["last_pass"] = [how_kinds.last_pass_kind(key_pass) for key_pass in all_shots["key_pass"]]
    shots = metrics.conceded_shots(matches, all_shots, include_penalties=False)

    missing = shots[shots[["x", "y", "xg"]].isna().any(axis=1)]
    if len(missing):
        print(f"STOP  {len(missing)} non-penalty shots have no location or no xG (PLAN.md section 6c)")
        return 1

    shots = add_how(shots)
    if not same_as_step_3b(shots):
        return 1

    # The model, and the model of the check with one more column (PLAN.md section 6c). Each is fitted
    # once, on all the league's shots, so the coefficients are the same for every team and random set.
    columns = how_kinds.kind_columns(shots)
    check_columns = how_kinds.kind_columns(shots, with_joint=True)
    centred = how_kinds.centre_in_zones(columns, shots["zone"])
    check_centred = how_kinds.centre_in_zones(check_columns, shots["zone"])
    coefficients = how_kinds.fit(shots["how"], centred)
    check_coefficients = how_kinds.fit(shots["how"], check_centred)
    parts = how_kinds.shot_parts(centred, coefficients, shots["how"])
    check_parts = how_kinds.shot_parts(check_centred, check_coefficients, shots["how"])

    team_matches = team_match_table(matches, per_shot_table(shots, check_centred, parts, check_parts))
    teams = team_table(team_matches)
    sets = where_how.random_sets(
        team_matches["n_shots"].to_numpy(), int(teams.loc[TEAM, "shots_conceded"]), N_RANDOM_SETS, SEED
    )
    if not same_random_sets_as_step_3b(team_matches, sets, shots["xg"].mean()):
        return 1
    tests = judge(teams, team_matches, sets)

    league = league_table(shots, check_columns, coefficients, check_coefficients)
    write_csv(league, "how_kinds_league.csv")
    write_csv(teams.reset_index(), "how_kinds_teams.csv")
    write_csv(tests, "how_kinds_tests.csv")
    print_summary(shots, league, teams, tests)
    return 0


def add_how(shots: pd.DataFrame) -> pd.DataFrame:
    """Add each shot's zone, its expected xG of the place and its how part, in the same way as step 3b."""
    shots = shots.copy()
    x, y = shots["x"].to_numpy(dtype=float), shots["y"].to_numpy(dtype=float)
    shots["distance"] = where_how.goal_distance(x, y)
    shots["angle"] = where_how.goal_angle(x, y)
    shots["zone"] = where_how.place_zones(shots["distance"], shots["angle"], N_DISTANCE_GROUPS, N_ANGLE_GROUPS)
    shots["place_xg"] = where_how.zone_average(shots["xg"], shots["zone"])
    shots["how"] = shots["xg"] - shots["place_xg"]
    return shots


def same_as_step_3b(shots: pd.DataFrame) -> bool:
    """The zones and every team's how part must be the ones of step 3b, as section 6c says.

    Step 3b read the same files in its own way and wrote its numbers with 4 decimal places.
    """
    zones = pd.read_csv(RESULTS_DIR / "where_how_zones.csv", encoding="utf-8").set_index("zone")
    teams = pd.read_csv(RESULTS_DIR / "where_how_teams.csv", encoding="utf-8").set_index("team")
    by_zone = shots.groupby("zone")["xg"].agg(["size", "mean"]).reindex(zones.index)
    by_team = shots.groupby("conceded_by")["how"].agg(["size", "mean"]).reindex(teams.index)
    wrong = [
        f"zone {zone}"
        for zone in zones.index
        if by_zone.loc[zone, "size"] != zones.loc[zone, "shots"]
        or abs(by_zone.loc[zone, "mean"] - zones.loc[zone, "xg_per_shot"]) > 0.00005
    ] + [
        team
        for team in teams.index
        if by_team.loc[team, "size"] != teams.loc[team, "shots_conceded"]
        or abs(by_team.loc[team, "mean"] - teams.loc[team, "how_part"]) > 0.00005
    ]
    for name in wrong:
        print(f"STOP  {name}: the shots or the numbers differ from step 3b (results/where_how_*.csv)")
    if not wrong:
        print(f"The {len(zones)} zones and the how parts of all {len(teams)} teams match step 3b.")
    return not wrong


def extra_name(column: str) -> str:
    """The name in the tables for a column of the model, for example "last pass: corner" -> "extra_last_pass_corner"."""
    return "extra_" + column.replace(how_kinds.LAST_PASS, "last_pass_").replace(" x ", "_x_").replace(" ", "_")


def per_shot_table(
    shots: pd.DataFrame, check_centred: pd.DataFrame, parts: pd.DataFrame, check_parts: pd.DataFrame
) -> pd.DataFrame:
    """One row per shot, with everything that is added up for each team-match."""
    table = shots[["match_id", "conceded_by", "xg", "place_xg", "how"]].copy()
    # For each kind: 1 or 0, minus the league's share of that kind in the shot's zone. Its average over a
    # team's shots is how many more shots of that kind the team faced than the league's shots from the same
    # zones. The columns of the check include all the columns of the model, so they are taken from there.
    for column in check_centred.columns:
        table[extra_name(column)] = check_centred[column]
    for part in how_kinds.PARTS:
        table[part] = parts[part]
        table[CHECK + part] = check_parts[part]
    return table


def team_match_table(matches: pd.DataFrame, per_shot: pd.DataFrame) -> pd.DataFrame:
    """One row per team per match (760 rows): sums over the shots that the team conceded in that match.

    The rows are in the same order as in step 3b, and a team-match without a shot is kept with zeros,
    so the random sets made from this table are the same as in step 3b.
    """
    groups = per_shot.groupby(["match_id", "conceded_by"])
    sums = groups.sum().add_prefix("sum_")
    sums.insert(0, "n_shots", groups.size())
    sums = sums.reset_index().rename(columns={"conceded_by": "team"})
    keys = metrics.opponents(matches)[["match_id", "team"]]
    table = keys.merge(sums, on=["match_id", "team"], how="left", validate="one_to_one").fillna(0)
    table["n_shots"] = table["n_shots"].astype(int)
    if table["n_shots"].sum() != len(per_shot):
        raise ValueError("Some shots were not counted in any team-match")
    return table


def team_table(team_matches: pd.DataFrame) -> pd.DataFrame:
    """One row per team, calculated in the same way as a random set: the team's 38 team-matches as one set."""
    teams = sorted(team_matches["team"].unique())
    team_sets = [np.flatnonzero(team_matches["team"].to_numpy() == team) for team in teams]
    n_shots = team_matches["n_shots"].to_numpy(dtype=float)

    def per_shot(name: str) -> np.ndarray:
        return where_how.set_averages(team_matches["sum_" + name].to_numpy(dtype=float), n_shots, team_sets)

    table = pd.DataFrame(index=pd.Index(teams, name="team"))
    table["shots_conceded"] = [int(n_shots[s].sum()) for s in team_sets]
    table["how_part"] = per_shot("how")
    for name in [c[len("sum_"):] for c in team_matches.columns if c.startswith("sum_extra_")]:
        table[name] = per_shot(name)
    for part in how_kinds.PARTS + [CHECK + part for part in how_kinds.PARTS]:
        table[part] = per_shot(part)
    # Rank 1 is the lowest part: the one that helps the defence most. The ranks are shown only; they decide nothing.
    for part in how_kinds.PARTS + [CHECK + part for part in how_kinds.PARTS]:
        table["rank_" + part] = metrics.ranks_lowest_first(table[part])
    return table


def same_random_sets_as_step_3b(team_matches: pd.DataFrame, sets: list[np.ndarray], league_xg_per_shot: float) -> bool:
    """Section 6c uses the same random sets as section 6b, but step 3b does not save its sets.

    So step 3b's shares of random sets for the where part and the how part are calculated again with these
    sets. Other sets would almost surely give other shares.
    """
    step3b = pd.read_csv(RESULTS_DIR / "where_how_tests.csv", encoding="utf-8").set_index("part")
    n_shots = team_matches["n_shots"].to_numpy(dtype=float)
    sum_xg = team_matches["sum_xg"].to_numpy(dtype=float)
    sum_place_xg = team_matches["sum_place_xg"].to_numpy(dtype=float)
    team_set = [np.flatnonzero(team_matches["team"].to_numpy() == TEAM)]
    (team_where,), (team_how,) = where_how.where_and_how(sum_xg, sum_place_xg, n_shots, team_set, league_xg_per_shot)
    where_sets, how_sets = where_how.where_and_how(sum_xg, sum_place_xg, n_shots, sets, league_xg_per_shot)
    shares = {
        "where": where_how.share_as_extreme(where_sets, team_where, lower_is_extreme=True),
        "how": where_how.share_as_extreme(how_sets, team_how, lower_is_extreme=True),
    }
    wrong = [part for part, share in shares.items() if abs(share - step3b.loc[part, "share_of_random_sets"]) > 0.00005]
    for part in wrong:
        print(
            f"STOP  the random sets differ from step 3b: for the {part} part, {shares[part]:.4f} of them are as low "
            f"as {TEAM}, not {step3b.loc[part, 'share_of_random_sets']:.4f}"
        )
    if not wrong:
        print(f"The {len(sets):,} random sets give the same shares as step 3b for the where part and the how part.")
    return not wrong


def judge(teams: pd.DataFrame, team_matches: pd.DataFrame, sets: list[np.ndarray]) -> pd.DataFrame:
    """Apply each rule of PLAN.md section 6c to TEAM. One row per part."""
    n_shots = team_matches["n_shots"].to_numpy(dtype=float)
    team = teams.loc[TEAM]

    def share_of_sets(column: str) -> float:
        set_values = where_how.set_averages(team_matches["sum_" + column].to_numpy(dtype=float), n_shots, sets)
        return where_how.share_as_extreme(set_values, team[column], lower_is_extreme=True)

    rows = [
        row("how", "how part: xG per shot conceded minus the expected xG of the places (section 6b)",
            team["how_part"], None, None, None, "the four parts add up to the how part", SHOWN_ONLY),
    ]
    supported = {}
    for prefix, name_end in (("", ""), (CHECK, " (check)")):
        for part, (name, words, measure) in JUDGED.items():
            share = share_of_sets(prefix + part)
            supported[prefix + part] = share < SUPPORTED_SHARE
            result = (
                f"supported: the {words} part is lower than chance can explain"
                if supported[prefix + part]
                else f"not supported: the {words} part is within what chance can explain"
            )
            rule = part_rule(words)
            if prefix:
                measure, rule = f"{measure}, {CHECK_TEXT}", f"{rule}, {CHECK_TEXT}"
                result += (
                    "; the same judgement as the model without header x under pressure"
                    if supported[prefix + part] == supported[part]
                    else "; a different judgement from the model without header x under pressure, "
                    "so the result depends on this joint effect"
                )
            rows.append(row(name + name_end, measure, team[prefix + part], team["rank_" + prefix + part],
                            "lowest first", share, rule, result))
        rows.append(row("rest" + name_end, "rest: the how part minus the three parts" + (f", {CHECK_TEXT}" if prefix else ""),
                        team[prefix + "rest"], team["rank_" + prefix + "rest"], "lowest first", None,
                        SHOWN_ONLY, SHOWN_ONLY))
        if not prefix:
            explained = (team["header_part"] + team["pressure_part"] + team["last_pass_part"]) / team["how_part"]
            met = explained >= MOST_OF_THE_HOW_PART
            result = f"{'met' if met else 'not met'}: the three parts together are {explained:.0%} of the how part"
            if explained > 1:
                result += ", so the rest has the other sign"
            rows.append(row("my expectation", "share of the how part that the three parts explain together",
                            explained, None, None, None, EXPECTATION_RULE, result))
    tests = pd.DataFrame(rows)
    tests["rank_of_20"] = tests["rank_of_20"].astype("Int64")  # whole numbers, empty where there is no rank
    return tests


def row(part, measure, value, rank, rank_order, share, rule, result) -> dict:
    return {
        "part": part,
        "measure": measure,
        "value": float(value),
        "rank_of_20": rank,
        "rank_order": rank_order,
        "share_of_random_sets": share,
        "rule": rule,
        "result": result,
    }


def league_table(
    shots: pd.DataFrame, check_columns: pd.DataFrame, coefficients: pd.Series, check_coefficients: pd.Series
) -> pd.DataFrame:
    """One row per kind of shot, over the league's shots: shown, not judged.

    how_per_shot is the plain average how part of the shots of that kind: how far they are from the average
    shot of their zone, which includes them. A coefficient compares them with the other shots of the same zone,
    when the other kinds are the same. So the two can differ. An empty coefficient means that the model has
    no column for that kind.
    """
    rows = []
    for kind in KIND_ROWS:
        if kind in check_columns:
            is_kind = check_columns[kind] == 1
        else:
            is_kind = shots["last_pass"] == how_kinds.REFERENCE
        rows.append(
            {
                "kind": kind,
                "shots": int(is_kind.sum()),
                "share_of_shots": is_kind.mean(),
                "how_per_shot": shots.loc[is_kind, "how"].mean(),
                "coefficient": coefficients.get(kind),
                "check_coefficient": check_coefficients.get(kind),
                "note": NOTES.get(kind, ""),
            }
        )
    return pd.DataFrame(rows)


def write_csv(frame: pd.DataFrame, name: str) -> None:
    out = RESULTS_DIR / name
    out.parent.mkdir(parents=True, exist_ok=True)
    # 4 decimal places, as in step 3b; ranks and judgements were made before rounding.
    frame.to_csv(out, index=False, encoding="utf-8", lineterminator="\n", float_format="%.4f")
    print(f"Written: {out.relative_to(ROOT).as_posix()}")


def print_summary(shots: pd.DataFrame, league: pd.DataFrame, teams: pd.DataFrame, tests: pd.DataFrame) -> None:
    print(f"\nLeague: {len(shots)} non-penalty shots in {shots['zone'].nunique()} zones.")
    print(league.drop(columns="note").to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    extras = teams.loc[TEAM, [c for c in teams.columns if c.startswith("extra_")]]
    print(f"\n{TEAM}: {int(teams.loc[TEAM, 'shots_conceded'])} shots conceded. More shots of each kind than the "
          f"league's shots from the same zones, per shot: "
          + ", ".join(f"{name[len('extra_'):]} {value:+.4f}" for name, value in extras.items()))
    for test in tests.itertuples():
        rank = "" if pd.isna(test.rank_of_20) else f", rank {test.rank_of_20} of 20 ({test.rank_order})"
        share = "" if pd.isna(test.share_of_random_sets) else f", random sets as low: {test.share_of_random_sets:.1%}"
        print(f"- {test.part}: {test.value:.4f}{rank}{share}\n    -> {test.result}")


if __name__ == "__main__":
    sys.exit(main())
