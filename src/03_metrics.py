"""Step 3: calculate the measures of PLAN.md section 6 and apply the fixed rules to Juventus.

Run from the project root:
    .venv\\Scripts\\python src\\03_metrics.py

The rules were fixed and committed before this script was first run (PLAN.md
section 6, DECISIONS.md D17-D20). This script only applies them. It writes three
tables in results/:
- team_metrics.csv: the measures for all 20 teams, with ranks (1 = lowest);
- replay_distribution.csv: the goals Juventus conceded in each replay of the season;
- hypothesis_tests.csv: each part of the hypothesis, its rule and the result.
"""
import sys

import numpy as np
import pandas as pd

import metrics
import sbdata
from config import (
    COMPETITION_NAME,
    FAR_FEWER_SHARE,
    N_REPLAYS,
    N_TEAMS,
    OFFICIAL_TABLE,
    RESULTS_DIR,
    ROOT,
    SEASON_NAME,
    SEED,
    TEAM,
)

# Measures ranked among the 20 teams, 1 = lowest. Measure 4 (goals vs xG) is judged by the replay.
RANKED = [
    "shots_conceded_per_match",  # measure 1
    "xg_per_shot_conceded",  # measure 2
    "xg_conceded_per_match",  # measure 3
    "shots_conceded_per_100_possessions",  # measure 5
    "xg_conceded_per_100_possessions",  # measure 5
]

# The rules of PLAN.md section 6, written from the settings in config.py.
FIRST_RULE = f"supported only if {TEAM} is 1st (lowest) of the {N_TEAMS} teams; a shared first counts as first"
REPLAY_RULE = (
    f"replay the season {N_REPLAYS:,} times (seed {SEED}); far fewer goals than xG if fewer than "
    f"{FAR_FEWER_SHARE:.0%} of the replays end with as few goals as {TEAM} conceded, or fewer"
)
POSSESSION_RULE = (
    f"possession does not explain the low numbers only if {TEAM} is 1st (lowest) on both per-possession measures"
)


def main() -> int:
    competitions = sbdata.read_json("competitions.json")
    competition_id, season_id = sbdata.find_season(competitions, COMPETITION_NAME, SEASON_NAME)
    matches = sbdata.matches_table(sbdata.read_json(f"matches/{competition_id}/{season_id}.json"))
    print(f"Reading the events of {len(matches)} matches...", flush=True)
    events, _, possessions = sbdata.load_events(matches["match_id"].tolist())

    table = team_metrics(matches, events, possessions)
    official = pd.read_csv(OFFICIAL_TABLE, encoding="utf-8")
    if not adds_up(table, official):
        return 1

    # The replays of the shots that Juventus conceded: the main one without penalties, and the check with them.
    replays = {
        include_penalties: metrics.replay_goals(team_shot_xg(matches, events, include_penalties), N_REPLAYS, SEED)
        for include_penalties in (False, True)
    }
    tests = hypothesis_tests(table, replays)

    write_csv(table.reset_index(), "team_metrics.csv")
    write_csv(replay_distribution(replays), "replay_distribution.csv")
    write_csv(tests, "hypothesis_tests.csv")
    print_summary(table, replays, tests)
    return 0


def team_metrics(matches: pd.DataFrame, events: pd.DataFrame, possessions: pd.DataFrame) -> pd.DataFrame:
    """One row per team: the measures of PLAN.md section 6, the checks with penalties, and the ranks."""
    main = metrics.conceded_table(matches, events, include_penalties=False)
    with_penalties = metrics.conceded_table(matches, events, include_penalties=True)
    opponent_possessions = metrics.opponent_possessions(matches, possessions).reindex(main.index)

    table = pd.DataFrame(
        {
            "matches": main["matches"],
            "shots_conceded": main["shots"],
            "shots_conceded_per_match": main["shots"] / main["matches"],
            "xg_per_shot_conceded": main["xg"] / main["shots"],
            "xg_conceded": main["xg"],
            "xg_conceded_per_match": main["xg"] / main["matches"],
            "goals_conceded_from_shots": main["goals"],
            "goals_minus_xg": main["goals"] - main["xg"],
            "own_goals_conceded": main["own_goals"],
            "opponent_possessions": opponent_possessions,
            "shots_conceded_per_100_possessions": 100 * main["shots"] / opponent_possessions,
            "xg_conceded_per_100_possessions": 100 * main["xg"] / opponent_possessions,
            "shots_conceded_with_penalties": with_penalties["shots"],
            "xg_conceded_with_penalties": with_penalties["xg"],
            "goals_conceded_with_penalties": with_penalties["goals"],
        }
    ).rename_axis("team")
    if table.isna().any().any():
        raise ValueError("A measure is missing for some team")
    for column in RANKED:
        table[f"rank_{column}"] = metrics.ranks_lowest_first(table[column])
    return table


def adds_up(table: pd.DataFrame, official: pd.DataFrame) -> bool:
    """Review focus 4: for every team, the parts of its goals conceded add up to the official table.

    Parts: goals from non-penalty shots + goals from penalties + own goals.
    If a part were counted for the wrong team, or twice, some team would not add up.
    """
    from_shots = table["goals_conceded_from_shots"]
    from_penalties = table["goals_conceded_with_penalties"] - from_shots
    own_goals = table["own_goals_conceded"]
    official_goals = official.set_index("team")["goals_against"].reindex(table.index)
    parts = from_shots + from_penalties + own_goals

    wrong = [team for team in table.index if parts[team] != official_goals[team]]
    for team in wrong:
        print(f"STOP  {team}: {parts[team]} from the parts, {official_goals[team]} in the official table")
    if not wrong:
        print(
            f"Adding up: all {len(table)} teams match the official table. League total: "
            f"{from_shots.sum()} from non-penalty shots + {from_penalties.sum()} from penalties "
            f"+ {own_goals.sum()} own goals = {parts.sum()}"
        )
    return not wrong


def team_shot_xg(matches: pd.DataFrame, events: pd.DataFrame, include_penalties: bool) -> np.ndarray:
    """The xG of every shot that TEAM conceded over the season."""
    shots = metrics.conceded_shots(matches, events, include_penalties)
    return shots.loc[shots["conceded_by"] == TEAM, "xg"].to_numpy()


def hypothesis_tests(table: pd.DataFrame, replays: dict[bool, np.ndarray]) -> pd.DataFrame:
    """Apply each rule of PLAN.md section 6 to TEAM. One row per measure."""
    rows = []
    for part, column, measure in [
        ("fewest chances", "shots_conceded_per_match", "shots conceded per match"),
        ("weakest chances", "xg_per_shot_conceded", "xG per shot conceded"),
    ]:
        rank, rank_text = rank_of(table[column])
        result = f"{'supported' if rank == 1 else 'not supported'}: {TEAM} is {rank_text}"
        rows.append(row(part, measure, table.loc[TEAM, column], rank, None, FIRST_RULE, result))

    for include_penalties in (False, True):
        goals_column = "goals_conceded_with_penalties" if include_penalties else "goals_conceded_from_shots"
        xg_column = "xg_conceded_with_penalties" if include_penalties else "xg_conceded"
        goals = table.loc[TEAM, goals_column]
        share = float((replays[include_penalties] <= goals).mean())
        if share < FAR_FEWER_SHARE:
            result = "far fewer goals than xG: the keeper or luck also mattered"
        else:
            result = "not far fewer than xG: the gap is within what chance can explain (not proof of no luck)"
        part = "goals about what xG predicted" + (" (check with penalties)" if include_penalties else "")
        measure = "goals conceded from shots minus xG conceded, " + (
            "penalties included" if include_penalties else "no penalties"
        )
        rows.append(row(part, measure, goals - table.loc[TEAM, xg_column], None, share, REPLAY_RULE, result))

    shots_rank, shots_text = rank_of(table["shots_conceded_per_100_possessions"])
    xg_rank, xg_text = rank_of(table["xg_conceded_per_100_possessions"])
    ranks_text = f"{TEAM} is {shots_text} on shots and {xg_text} on xG"
    if shots_rank == 1 and xg_rank == 1:
        result = f"possession does not explain the low numbers: {ranks_text}"
    else:
        result = f"possession explains part of the low numbers: {ranks_text}"
    rows.append(
        row(
            "possession", "shots conceded per 100 opponent possessions",
            table.loc[TEAM, "shots_conceded_per_100_possessions"], shots_rank, None, POSSESSION_RULE, result,
        )
    )
    rows.append(
        row(
            "possession", "xG conceded per 100 opponent possessions",
            table.loc[TEAM, "xg_conceded_per_100_possessions"], xg_rank, None, POSSESSION_RULE, result,
        )
    )

    tests = pd.DataFrame(rows)
    tests["rank_of_20"] = tests["rank_of_20"].astype("Int64")  # whole numbers, empty where there is no rank
    return tests


def row(part, measure, value, rank, share, rule, result) -> dict:
    return {
        "part": part,
        "measure": measure,
        "value": float(value),
        "rank_of_20": rank,
        "share_of_replays_at_or_below": share,
        "rule": rule,
        "result": result,
    }


def rank_of(values: pd.Series) -> tuple[int, str]:
    """TEAM's rank (1 = lowest), and the same in words ("2nd of 20"), naming any team with the same value."""
    rank, shared = metrics.rank_lowest(values, TEAM)
    text = f"{ordinal(rank)} of {len(values)}"
    if shared:
        others = sorted(team for team in values.index[values == values[TEAM]] if team != TEAM)
        text += f" (shared with {', '.join(others)})"
    return rank, text


def ordinal(n: int) -> str:
    """1 -> 1st, 2 -> 2nd, 3 -> 3rd, 4 -> 4th, 11 -> 11th, 21 -> 21st."""
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def replay_distribution(replays: dict[bool, np.ndarray]) -> pd.DataFrame:
    """How many replays ended with 0, 1, 2, ... goals conceded (for the chart in M4)."""
    top = int(max(r.max() for r in replays.values()))
    return pd.DataFrame(
        {
            "goals": np.arange(top + 1),
            "replays_without_penalties": np.bincount(replays[False], minlength=top + 1),
            "replays_with_penalties": np.bincount(replays[True], minlength=top + 1),
        }
    )


def write_csv(frame: pd.DataFrame, name: str) -> None:
    out = RESULTS_DIR / name
    out.parent.mkdir(parents=True, exist_ok=True)
    # 4 decimal places are enough for these measures; ranks were calculated before rounding.
    frame.to_csv(out, index=False, encoding="utf-8", lineterminator="\n", float_format="%.4f")
    print(f"Written: {out.relative_to(ROOT).as_posix()}")


def print_summary(table: pd.DataFrame, replays: dict[bool, np.ndarray], tests: pd.DataFrame) -> None:
    juve = table.loc[TEAM]
    print(f"\n{TEAM}: {int(juve['goals_conceded_from_shots'])} goals from non-penalty shots, "
          f"xG {juve['xg_conceded']:.2f}; mean goals in the replays {replays[False].mean():.2f}")
    for test in tests.itertuples():
        share = "" if pd.isna(test.share_of_replays_at_or_below) else f", replays at or below: {test.share_of_replays_at_or_below:.1%}"
        print(f"- {test.part}: {test.measure} = {test.value:.3f}{share}\n    -> {test.result}")


if __name__ == "__main__":
    sys.exit(main())
