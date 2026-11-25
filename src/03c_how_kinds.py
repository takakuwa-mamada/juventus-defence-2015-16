"""Step 3c: the third question (PLAN.md section 6c). What is the how part made of?

Run from the project root:
    .venv\\Scripts\\python src\\03c_how_kinds.py

The rules were fixed and published before this script was first run (PLAN.md
section 6c, DECISIONS.md D35-D36). This script only applies them. It writes one table in results/:
- how_kinds_league.csv: for each kind of shot, how many of the league's shots are of that kind,
  their average how part, and the coefficient of the straight-line model (and of the model of the check).
  League-wide only: no team is split out in this table.
"""
import sys

import pandas as pd

import how_kinds
import metrics
import sbdata
import where_how
from config import COMPETITION_NAME, N_ANGLE_GROUPS, N_DISTANCE_GROUPS, RESULTS_DIR, ROOT, SEASON_NAME

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
    coefficients = how_kinds.fit(shots["how"], how_kinds.centre_in_zones(columns, shots["zone"]))
    check_coefficients = how_kinds.fit(shots["how"], how_kinds.centre_in_zones(check_columns, shots["zone"]))

    league = league_table(shots, check_columns, coefficients, check_coefficients)
    write_csv(league, "how_kinds_league.csv")
    print(f"\nLeague: {len(shots)} non-penalty shots in {shots['zone'].nunique()} zones.")
    print(league.drop(columns="note").to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    return 0


def add_how(shots: pd.DataFrame) -> pd.DataFrame:
    """Add each shot's zone and how part, in the same way as step 3b (PLAN.md section 6b)."""
    shots = shots.copy()
    x, y = shots["x"].to_numpy(dtype=float), shots["y"].to_numpy(dtype=float)
    shots["distance"] = where_how.goal_distance(x, y)
    shots["angle"] = where_how.goal_angle(x, y)
    shots["zone"] = where_how.place_zones(shots["distance"], shots["angle"], N_DISTANCE_GROUPS, N_ANGLE_GROUPS)
    shots["how"] = shots["xg"] - where_how.zone_average(shots["xg"], shots["zone"])
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
    # 4 decimal places, as in step 3b.
    frame.to_csv(out, index=False, encoding="utf-8", lineterminator="\n", float_format="%.4f")
    print(f"Written: {out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    sys.exit(main())
