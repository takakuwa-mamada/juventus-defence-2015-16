"""Step 3b: the second question (PLAN.md section 6b). Why were the chances against Juventus weak?

Run from the project root:
    .venv\\Scripts\\python src\\03b_where_how.py

The rules were fixed and published before this script was first run (PLAN.md
section 6b, DECISIONS.md D29-D30). This script only applies them. It writes:
- where_how_zones.csv: the 30 zones of the pitch, with the league's numbers in each.
  The columns that start with "check_" use only the frames that show at least
  MIN_PLAYERS_IN_FRAME players (the check at the end of section 6b).
"""
import sys

import pandas as pd

import metrics
import sbdata
import where_how
from config import (
    COMPETITION_NAME,
    MIN_PLAYERS_IN_FRAME,
    N_ANGLE_GROUPS,
    N_DISTANCE_GROUPS,
    RESULTS_DIR,
    ROOT,
    SEASON_NAME,
)

# Direct free kicks are left out of the defenders measures, because the wall would count as defenders in the way.
DIRECT_FREE_KICK = "Free Kick"


def main() -> int:
    competitions = sbdata.read_json("competitions.json")
    competition_id, season_id = sbdata.find_season(competitions, COMPETITION_NAME, SEASON_NAME)
    matches = sbdata.matches_table(sbdata.read_json(f"matches/{competition_id}/{season_id}.json"))
    print(f"Reading the shots of {len(matches)} matches...", flush=True)
    all_shots = sbdata.load_shot_frames(matches["match_id"].tolist())
    shots = metrics.conceded_shots(matches, all_shots, include_penalties=False)

    missing = where_how.shots_without_a_place(shots)
    if len(missing):
        print(f"STOP  {len(missing)} non-penalty shots have no location or no freeze frame (PLAN.md section 6b)")
        return 1
    print(f"All {len(shots)} non-penalty shots have a location and a freeze frame.")

    shots = add_places(shots)
    zones = zone_table(shots)
    write_csv(zones, "where_how_zones.csv")
    print_summary(shots, zones)
    return 0


def add_places(shots: pd.DataFrame) -> pd.DataFrame:
    """Add where each shot was taken, its zone, and what its freeze frame shows."""
    shots = shots.copy()
    x, y = shots["x"].to_numpy(dtype=float), shots["y"].to_numpy(dtype=float)
    shots["distance"] = where_how.goal_distance(x, y)
    shots["angle"] = where_how.goal_angle(x, y)
    shots["zone"] = where_how.place_zones(shots["distance"], shots["angle"], N_DISTANCE_GROUPS, N_ANGLE_GROUPS)
    shots["players_in_frame"] = shots["freeze_frame"].map(len)
    frames = list(zip(shots["freeze_frame"], x, y))
    shots["defenders_in_the_way"] = [where_how.defenders_in_the_way(frame, sx, sy) for frame, sx, sy in frames]
    shots["nearest_defender"] = [where_how.nearest_defender(frame, sx, sy) for frame, sx, sy in frames]
    shots["for_defenders"] = shots["shot_type"] != DIRECT_FREE_KICK
    shots["for_check"] = shots["for_defenders"] & (shots["players_in_frame"] >= MIN_PLAYERS_IN_FRAME)
    return shots


def zone_table(shots: pd.DataFrame) -> pd.DataFrame:
    """One row per zone: where it is, and the league's numbers in it (the "expected" values of section 6b)."""
    by_zone = shots.groupby("zone")
    defenders = shots[shots["for_defenders"]].groupby("zone")
    check = shots[shots["for_check"]].groupby("zone")
    table = pd.DataFrame(
        {
            "distance_from": by_zone["distance"].min(),
            "distance_to": by_zone["distance"].max(),
            "angle_from": by_zone["angle"].min(),
            "angle_to": by_zone["angle"].max(),
            "shots": by_zone.size(),
            # The expected xG of the place.
            "xg_per_shot": by_zone["xg"].mean(),
            "shots_without_free_kicks": defenders.size(),
            # The expected number of defenders in the way.
            "defenders_in_the_way_per_shot": defenders["defenders_in_the_way"].mean(),
            # Shown, not judged. Shots whose frame shows no outfield defender have no distance and are left out.
            "nearest_defender": defenders["nearest_defender"].mean(),
            "check_shots": check.size(),
            "check_defenders_in_the_way_per_shot": check["defenders_in_the_way"].mean(),
        }
    ).rename_axis("zone")
    return table.reset_index()


def write_csv(frame: pd.DataFrame, name: str) -> None:
    out = RESULTS_DIR / name
    out.parent.mkdir(parents=True, exist_ok=True)
    # 4 decimal places are enough for these measures.
    frame.to_csv(out, index=False, encoding="utf-8", lineterminator="\n", float_format="%.4f")
    print(f"Written: {out.relative_to(ROOT).as_posix()}")


def print_summary(shots: pd.DataFrame, zones: pd.DataFrame) -> None:
    free_kicks = int((~shots["for_defenders"]).sum())
    small = int((shots["for_defenders"] & ~shots["for_check"]).sum())
    print(
        f"\nLeague: {len(shots)} non-penalty shots, xG per shot {shots['xg'].mean():.4f}; "
        f"{free_kicks} direct free kicks; {small} other shots whose frame shows fewer than {MIN_PLAYERS_IN_FRAME} players"
    )
    print(f"Zones: {len(zones)}, with {zones['shots'].min()} to {zones['shots'].max()} shots each")
    print(" zone  distance (yd)   angle (deg)   shots  xG/shot  defenders in the way  nearest defender (yd)")
    for z in zones.itertuples():
        print(
            f" {z.zone:>4}  {z.distance_from:5.1f}-{z.distance_to:5.1f}  {z.angle_from:5.1f}-{z.angle_to:5.1f}"
            f"  {z.shots:>6}  {z.xg_per_shot:7.3f}  {z.defenders_in_the_way_per_shot:20.2f}  {z.nearest_defender:21.2f}"
        )


if __name__ == "__main__":
    sys.exit(main())
