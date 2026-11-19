"""Step 3b: the second question (PLAN.md section 6b). Why were the chances against Juventus weak?

Run from the project root:
    .venv\\Scripts\\python src\\03b_where_how.py

The rules were fixed and published before this script was first run (PLAN.md
section 6b, DECISIONS.md D29-D30). This script only applies them. It writes three
tables in results/:
- where_how_zones.csv: the 30 zones of the pitch, with the league's numbers in each.
  The columns that start with "check_" use only the frames that show at least
  MIN_PLAYERS_IN_FRAME players (the check at the end of section 6b).
- where_how_teams.csv: for every team, the split of its gap into "where" and "how",
  and the defenders in the way, with ranks;
- where_how_tests.csv: each part for Juventus, its rule and the result.
"""
import sys

import numpy as np
import pandas as pd

import metrics
import sbdata
import where_how
from config import (
    ABOUT_THE_SAME_SIZE,
    COMPETITION_NAME,
    MIN_PLAYERS_IN_FRAME,
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

# Direct free kicks are left out of the defenders measures, because the wall would count as defenders in the way.
DIRECT_FREE_KICK = "Free Kick"

# The rules of PLAN.md section 6b, written from the settings in config.py.
RANDOM_SETS_TEXT = (
    f"{N_RANDOM_SETS:,} random sets of whole team-matches (seed {SEED}), "
    f"each with at least as many shots as {TEAM} conceded"
)
WHERE_RULE = (
    f"supported if fewer than {SUPPORTED_SHARE:.0%} of {RANDOM_SETS_TEXT} have a where part "
    f"as low as {TEAM}'s, or lower"
)
HOW_RULE = (
    f"supported if fewer than {SUPPORTED_SHARE:.0%} of {RANDOM_SETS_TEXT} have a how part "
    f"as low as {TEAM}'s, or lower"
)
DEFENDERS_RULE = (
    f"supported if fewer than {SUPPORTED_SHARE:.0%} of {RANDOM_SETS_TEXT} have as many extra "
    f"defenders in the way as {TEAM}, or more"
)
CHECK_RULE = f"{DEFENDERS_RULE}; only the frames that show at least {MIN_PLAYERS_IN_FRAME} players"
EXPECTATION_RULE = (
    f"about the same size: each part between {ABOUT_THE_SAME_SIZE[0]:.0%} and {ABOUT_THE_SAME_SIZE[1]:.0%} "
    f"of {TEAM}'s gap (D30)"
)
SHOWN_ONLY = "shown, not judged"


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

    shots = add_expected(add_places(shots))
    league_xg_per_shot = shots["xg"].mean()
    team_matches = team_match_table(matches, shots)
    teams = team_table(team_matches, league_xg_per_shot)
    if not same_as_step_3(teams):
        return 1

    sets = where_how.random_sets(
        team_matches["n_shots"].to_numpy(), int(teams.loc[TEAM, "shots_conceded"]), N_RANDOM_SETS, SEED
    )
    tests = judge(teams, team_matches, sets, league_xg_per_shot)

    write_csv(zone_table(shots), "where_how_zones.csv")
    write_csv(teams.reset_index(), "where_how_teams.csv")
    write_csv(tests, "where_how_tests.csv")
    print_summary(shots, teams, sets, team_matches, tests)
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


def add_expected(shots: pd.DataFrame) -> pd.DataFrame:
    """Add each shot's expected values (the league's averages in its zone) and its difference from them."""
    shots = shots.copy()
    shots["place_xg"] = where_how.zone_average(shots["xg"], shots["zone"])
    # Without direct free kicks, and with expected numbers made without them too. Free kicks get no value here.
    d = shots[shots["for_defenders"]]
    shots["extra_defenders"] = d["defenders_in_the_way"] - where_how.zone_average(d["defenders_in_the_way"], d["zone"])
    shots["nearest_defender_vs_zone"] = d["nearest_defender"] - where_how.zone_average(d["nearest_defender"], d["zone"])
    # The check: the same zones, and expected numbers made again from the league's shots that are left.
    c = shots[shots["for_check"]]
    shots["check_extra_defenders"] = (
        c["defenders_in_the_way"] - where_how.zone_average(c["defenders_in_the_way"], c["zone"])
    )
    return shots


def team_match_table(matches: pd.DataFrame, shots: pd.DataFrame) -> pd.DataFrame:
    """One row per team per match (760 rows): sums over the shots that the team conceded in that match.

    A team-match in which the team conceded no shot is kept, with zeros, because it is one of the 760.
    """
    sums = (
        shots.assign(
            n_defenders=shots["for_defenders"].astype(int),
            n_nearest=shots["nearest_defender_vs_zone"].notna().astype(int),
            n_check=shots["for_check"].astype(int),
        )
        .groupby(["match_id", "conceded_by"])
        .agg(
            n_shots=("xg", "size"),
            sum_xg=("xg", "sum"),
            sum_place_xg=("place_xg", "sum"),
            n_defenders=("n_defenders", "sum"),
            sum_extra_defenders=("extra_defenders", "sum"),
            n_nearest=("n_nearest", "sum"),
            sum_nearest_defender_vs_zone=("nearest_defender_vs_zone", "sum"),
            n_check=("n_check", "sum"),
            sum_check_extra_defenders=("check_extra_defenders", "sum"),
        )
        .reset_index()
        .rename(columns={"conceded_by": "team"})
    )
    keys = metrics.opponents(matches)[["match_id", "team"]]
    table = keys.merge(sums, on=["match_id", "team"], how="left", validate="one_to_one").fillna(0)
    table = table.astype({"n_shots": int, "n_defenders": int, "n_nearest": int, "n_check": int})
    if table["n_shots"].sum() != len(shots):
        raise ValueError("Some shots were not counted in any team-match")
    return table


def team_table(team_matches: pd.DataFrame, league_xg_per_shot: float) -> pd.DataFrame:
    """One row per team, calculated in the same way as a random set: the team's 38 team-matches as one set."""
    teams = sorted(team_matches["team"].unique())
    team_sets = [np.flatnonzero(team_matches["team"].to_numpy() == team) for team in teams]
    column = {name: team_matches[name].to_numpy(dtype=float) for name in team_matches.columns[2:]}
    where, how = where_how.where_and_how(
        column["sum_xg"], column["sum_place_xg"], column["n_shots"], team_sets, league_xg_per_shot
    )
    table = pd.DataFrame(
        {
            "shots_conceded": [int(column["n_shots"][s].sum()) for s in team_sets],
            "xg_per_shot_conceded": where_how.set_averages(column["sum_xg"], column["n_shots"], team_sets),
            "place_xg_per_shot": where_how.set_averages(column["sum_place_xg"], column["n_shots"], team_sets),
            "gap": where + how,
            "where_part": where,
            "how_part": how,
            "shots_for_defenders": [int(column["n_defenders"][s].sum()) for s in team_sets],
            "extra_defenders": where_how.set_averages(column["sum_extra_defenders"], column["n_defenders"], team_sets),
            "check_shots": [int(column["n_check"][s].sum()) for s in team_sets],
            "check_extra_defenders": where_how.set_averages(
                column["sum_check_extra_defenders"], column["n_check"], team_sets
            ),
            "nearest_defender_vs_zone": where_how.set_averages(
                column["sum_nearest_defender_vs_zone"], column["n_nearest"], team_sets
            ),
        },
        index=pd.Index(teams, name="team"),
    )
    # Rank 1 is the value that helps the defence most: the lowest where part, how part and nearest-defender
    # distance, and the most extra defenders in the way. The ranks are shown only; they decide nothing.
    table["rank_where_part"] = metrics.ranks_lowest_first(table["where_part"])
    table["rank_how_part"] = metrics.ranks_lowest_first(table["how_part"])
    table["rank_extra_defenders"] = metrics.ranks_lowest_first(-table["extra_defenders"])
    table["rank_check_extra_defenders"] = metrics.ranks_lowest_first(-table["check_extra_defenders"])
    table["rank_nearest_defender_vs_zone"] = metrics.ranks_lowest_first(table["nearest_defender_vs_zone"])
    return table


def same_as_step_3(teams: pd.DataFrame) -> bool:
    """The shots and the xG per shot of every team must match step 3, which read the same data another way."""
    step3 = pd.read_csv(RESULTS_DIR / "team_metrics.csv", encoding="utf-8").set_index("team").reindex(teams.index)
    # step 3 wrote xG per shot with 4 decimal places.
    wrong = [
        team
        for team in teams.index
        if teams.loc[team, "shots_conceded"] != step3.loc[team, "shots_conceded"]
        or abs(teams.loc[team, "xg_per_shot_conceded"] - step3.loc[team, "xg_per_shot_conceded"]) > 0.00005
    ]
    for team in wrong:
        print(f"STOP  {team}: the shots or the xG per shot differ from results/team_metrics.csv")
    if not wrong:
        print(f"Shots and xG per shot match step 3 for all {len(teams)} teams.")
    return not wrong


def judge(
    teams: pd.DataFrame, team_matches: pd.DataFrame, sets: list[np.ndarray], league_xg_per_shot: float
) -> pd.DataFrame:
    """Apply each rule of PLAN.md section 6b to TEAM. One row per part."""
    column = {name: team_matches[name].to_numpy(dtype=float) for name in team_matches.columns[2:]}
    where_sets, how_sets = where_how.where_and_how(
        column["sum_xg"], column["sum_place_xg"], column["n_shots"], sets, league_xg_per_shot
    )
    extra_sets = where_how.set_averages(column["sum_extra_defenders"], column["n_defenders"], sets)
    check_sets = where_how.set_averages(column["sum_check_extra_defenders"], column["n_check"], sets)
    team = teams.loc[TEAM]

    where_share = where_how.share_as_extreme(where_sets, team["where_part"], lower_is_extreme=True)
    how_share = where_how.share_as_extreme(how_sets, team["how_part"], lower_is_extreme=True)
    extra_share = where_how.share_as_extreme(extra_sets, team["extra_defenders"], lower_is_extreme=False)
    check_share = where_how.share_as_extreme(check_sets, team["check_extra_defenders"], lower_is_extreme=False)

    where_result = (
        "supported: the opponents shot from worse places than chance can explain"
        if where_share < SUPPORTED_SHARE
        else "not supported: the places are within what chance can explain"
    )
    how_result = (
        "supported: from the same places, the shots were less likely to go in than chance can explain"
        if how_share < SUPPORTED_SHARE
        else "not supported: from the same places, the shots were within what chance can explain"
    )
    extra_supported = extra_share < SUPPORTED_SHARE
    check_supported = check_share < SUPPORTED_SHARE
    defenders_result = (
        "supported: more defenders in the way than chance can explain"
        if extra_supported
        else "not supported: the defenders in the way are within what chance can explain"
    )
    check_result = (
        "supported: more defenders in the way than chance can explain"
        if check_supported
        else "not supported: the defenders in the way are within what chance can explain"
    )
    check_result += (
        "; the same judgement as with all frames"
        if check_supported == extra_supported
        else "; a different judgement from all frames, so the result depends on the frames with few players"
    )

    where_of_gap = team["where_part"] / team["gap"]
    how_of_gap = team["how_part"] / team["gap"]
    low, high = ABOUT_THE_SAME_SIZE
    met = low <= where_of_gap <= high and low <= how_of_gap <= high
    expectation_result = (
        f"{'met' if met else 'not met'}: the where part is {where_of_gap:.0%} of the gap, "
        f"and the how part {how_of_gap:.0%}"
    )

    rows = [
        row("gap", "xG per shot conceded minus the league's xG per shot", team["gap"], None, None, None,
            "the where part and the how part add up to the gap", SHOWN_ONLY),
        row("where", "where part: expected xG of the places minus the league's xG per shot", team["where_part"],
            team["rank_where_part"], "lowest first", where_share, WHERE_RULE, where_result),
        row("how", "how part: xG per shot conceded minus the expected xG of the places", team["how_part"],
            team["rank_how_part"], "lowest first", how_share, HOW_RULE, how_result),
        row("defenders in the way", "extra defenders in the way per shot, without direct free kicks",
            team["extra_defenders"], team["rank_extra_defenders"], "highest first", extra_share,
            DEFENDERS_RULE, defenders_result),
        row("defenders in the way (check)",
            f"extra defenders in the way per shot, frames with at least {MIN_PLAYERS_IN_FRAME} players",
            team["check_extra_defenders"], team["rank_check_extra_defenders"], "highest first", check_share,
            CHECK_RULE, check_result),
        row("my expectation", "share of the gap that is the where part", where_of_gap, None, None, None,
            EXPECTATION_RULE, expectation_result),
        row("nearest defender", "distance to the nearest defender minus the league's for the zone, in yards",
            team["nearest_defender_vs_zone"], team["rank_nearest_defender_vs_zone"], "lowest first", None,
            SHOWN_ONLY, SHOWN_ONLY),
    ]
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
    # 4 decimal places are enough for these measures; ranks and judgements were made before rounding.
    frame.to_csv(out, index=False, encoding="utf-8", lineterminator="\n", float_format="%.4f")
    print(f"Written: {out.relative_to(ROOT).as_posix()}")


def print_summary(
    shots: pd.DataFrame, teams: pd.DataFrame, sets: list[np.ndarray], team_matches: pd.DataFrame, tests: pd.DataFrame
) -> None:
    n_shots = team_matches["n_shots"].to_numpy()
    set_shots = np.array([n_shots[s].sum() for s in sets])
    set_sizes = np.array([len(s) for s in sets])
    print(
        f"\nLeague: {len(shots)} non-penalty shots, xG per shot {shots['xg'].mean():.4f}. "
        f"{TEAM}: {int(teams.loc[TEAM, 'shots_conceded'])} shots conceded. Random sets: "
        f"{set_sizes.min()}-{set_sizes.max()} team-matches, {set_shots.min()}-{set_shots.max()} shots "
        f"(mean {set_shots.mean():.1f})"
    )
    for test in tests.itertuples():
        rank = "" if pd.isna(test.rank_of_20) else f", rank {test.rank_of_20} of 20 ({test.rank_order})"
        share = "" if pd.isna(test.share_of_random_sets) else f", random sets as extreme: {test.share_of_random_sets:.1%}"
        print(f"- {test.part}: {test.value:.4f}{rank}{share}\n    -> {test.result}")


if __name__ == "__main__":
    sys.exit(main())
