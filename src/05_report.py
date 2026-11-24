"""Step 5: write the README and the one-page summaries, with every number from the results tables (D23).

Run from the project root:
    .venv\\Scripts\\python src\\05_report.py

The text is written by hand in templates/, with a placeholder such as {{juve_goals_total}} wherever a
number goes. This script reads the tables in results/, fills in every placeholder, and writes
README.md, docs/summary_en.md and docs/summary_ja.md.

It stops, and writes nothing, if:
- a result is no longer the one that the text was written for (the text would then be wrong);
- a template contains a typed number (every number must come from the results tables);
- a template uses a placeholder that has no value.
"""
import re
import sys

import pandas as pd

from config import (
    DOCS_DIR, FAR_FEWER_SHARE, LOGO_URL, MIN_PLAYERS_IN_FRAME, N_ANGLE_GROUPS, N_DISTANCE_GROUPS, N_RANDOM_SETS,
    RESULTS_DIR, ROOT, SUPPORTED_SHARE, TEAM, TEMPLATES_DIR,
)

# Each template, and the file written from it.
OUTPUTS = {
    "readme.template.md": ROOT / "README.md",
    "summary_en.template.md": DOCS_DIR / "summary_en.md",
    "summary_ja.template.md": DOCS_DIR / "summary_ja.md",
}
PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
# Names and units that contain digits but are not results, so they may be typed in a template.
TYPED_TERMS_ALLOWED = ["2015/16", "juventus-defence-2015-16", "per 100 ", "100 回あたり"]
# Japanese names for the teams that the Japanese summary may name. Any other team keeps StatsBomb's name.
JAPANESE_NAMES = {"Napoli": "ナポリ"}
# The parts of the second question that are judged (PLAN.md section 6b). The check is not a test of its own.
JUDGED_PARTS = ["where", "how", "defenders in the way"]


def main() -> int:
    table = read("team_metrics.csv").set_index("team")
    tests = read("hypothesis_tests.csv")
    replays = read("replay_distribution.csv")
    checks = read("data_checks.csv")
    manifest = read("data_manifest.csv")
    where_how_teams = read("where_how_teams.csv").set_index("team")
    where_how_tests = read("where_how_tests.csv")

    check_results(table, tests, checks)
    check_where_how(where_how_tests)
    values = values_for_text(table, tests, replays, checks, manifest)
    values.update(where_how_values(where_how_teams, where_how_tests))

    # Fill every template first, and write the files only if all of them are fine.
    texts = {}
    for name, out in OUTPUTS.items():
        template = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
        typed = typed_numbers(template)
        if typed:
            sys.exit(f"templates/{name} has typed numbers. Use a placeholder instead:\n  " + "\n  ".join(typed))
        texts[out] = header(name) + fill(template, values, name)
    for out, text in texts.items():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8", newline="\n")
        print(f"Written: {out.relative_to(ROOT).as_posix()}")
    return 0


def check_results(table: pd.DataFrame, tests: pd.DataFrame, checks: pd.DataFrame) -> None:
    """Stop if a result is not the one that the text in templates/ was written for."""
    if not checks["passed"].all():
        sys.exit("A data check failed (results/data_checks.csv). The text is not written about data that failed.")
    expect(tests, "fewest chances", "not supported")
    expect(tests, "weakest chances", "supported")
    expect(tests, "goals about what xG predicted", "not far fewer")
    expect(tests, "goals about what xG predicted (check with penalties)", "not far fewer")
    expect(tests, "possession", "possession explains part")

    # Facts that the text states in words, beyond the results of the tests.
    juve = table.loc[TEAM]
    goals_all = all_goals_conceded(table)
    fewest = table.loc[fewest_shots_team(table)]
    facts = {
        "Juventus conceded the fewest goals, with no tie": goals_all[TEAM] < goals_all.drop(TEAM).min(),
        "Juventus allowed almost the fewest shots (2nd)": juve["rank_shots_conceded_per_match"] == 2,
        "the team with the fewest shots allowed better chances": fewest["xg_per_shot_conceded"] > juve["xg_per_shot_conceded"],
        "Juventus had the lowest xG conceded per match": juve["rank_xg_conceded_per_match"] == 1,
        "Juventus conceded fewer goals than xG": juve["goals_minus_xg"] < 0,
    }
    for fact, holds in facts.items():
        if not holds:
            sys.exit(f"The text in templates/ says: {fact}. The results no longer show this. Rewrite the text.")


def check_where_how(tests: pd.DataFrame) -> None:
    """Stop if a result of the second question (PLAN.md section 6b) is not the one that the text was written for."""
    expect(tests, "where", "supported")
    expect(tests, "how", "supported")
    expect(tests, "defenders in the way", "not supported")
    expect(tests, "defenders in the way (check)", "not supported")
    expect(tests, "my expectation", "met")
    part = tests.set_index("part")
    facts = {
        "the shots against Juventus came from worse places than the league's": part.loc["where", "value"] < 0,
        "from the same places, they were less likely to go in": part.loc["how", "value"] < 0,
        "the where part of Juventus was the lowest of the teams": part.loc["where", "rank_of_20"] == 1,
        "the how part of Juventus was the lowest of the teams": part.loc["how", "rank_of_20"] == 1,
        "Juventus did not have more defenders in the way than usual": part.loc["defenders in the way", "value"] <= 0,
        "the check gave the same judgement": "the same judgement" in part.loc["defenders in the way (check)", "result"],
        "the nearest defender was closer than usual": part.loc["nearest defender", "value"] < 0,
    }
    for fact, holds in facts.items():
        if not holds:
            sys.exit(f"The text in templates/ says: {fact}. The results no longer show this. Rewrite the text.")


def expect(tests: pd.DataFrame, part: str, start: str) -> None:
    """Stop if the result of a part of the hypothesis does not start as the text expects."""
    results = tests.loc[tests["part"] == part, "result"].unique()
    if len(results) != 1 or not results[0].startswith(start):
        sys.exit(
            f"The text in templates/ was written for a result that starts with '{start}' in '{part}', "
            f"but the result is now {list(results)}. Rewrite the text."
        )


def values_for_text(table, tests, replays, checks, manifest) -> dict[str, str]:
    """Every value that a template can use, already written as text."""
    juve = table.loc[TEAM]
    goals_all = all_goals_conceded(table)
    second = goals_all.drop(TEAM).idxmin()
    fewest = fewest_shots_team(table)
    shots_gap = int(juve["shots_conceded"] - table.loc[fewest, "shots_conceded"])
    replay_share = tests.drop_duplicates("part").set_index("part")["share_of_replays_at_or_below"]
    n_replays = int(replays["replays_without_penalties"].sum())
    shots_per_100_rank = int(juve["rank_shots_conceded_per_100_possessions"])
    xg_per_100_rank = int(juve["rank_xg_conceded_per_100_possessions"])
    return {
        # The league and the season.
        "n_teams": str(len(table)),
        "n_matches": str(int(table["matches"].sum()) // 2),  # every match is counted once for each team
        "matches_per_team": str(int(juve["matches"])),
        # All goals conceded.
        "juve_goals_total": str(int(goals_all[TEAM])),
        "second_goals_team": second,
        "second_goals_total": str(int(goals_all[second])),
        # How many chances (measure 1).
        "juve_shots_per_match": f"{juve['shots_conceded_per_match']:.1f}",
        "juve_shots_rank": ordinal(int(juve["rank_shots_conceded_per_match"])),
        "juve_shots_rank_n": str(int(juve["rank_shots_conceded_per_match"])),
        "fewest_shots_team": fewest,
        "fewest_shots_team_ja": JAPANESE_NAMES.get(fewest, fewest),
        "fewest_shots_per_match": f"{table.loc[fewest, 'shots_conceded_per_match']:.1f}",
        "shots_gap": str(shots_gap),
        "shots_gap_text": count(shots_gap, "shot"),
        # How good the chances were (measures 2 and 3).
        "juve_xg_per_shot_pct": f"{juve['xg_per_shot_conceded']:.1%}",
        "fewest_shots_xg_per_shot_pct": f"{table.loc[fewest, 'xg_per_shot_conceded']:.1%}",
        "juve_xg_per_match": f"{juve['xg_conceded_per_match']:.2f}",
        # Goals vs. xG, and the replay of the season (measure 4, D17).
        "juve_goals_from_shots": str(int(juve["goals_conceded_from_shots"])),
        "juve_xg": f"{juve['xg_conceded']:.1f}",
        "goals_below_xg": f"{-juve['goals_minus_xg']:.1f}",
        "bigger_gap_count": count(int((table["goals_minus_xg"] < juve["goals_minus_xg"]).sum()), "team"),
        "n_replays": f"{n_replays:,}",
        "n_replays_ja": japanese_count(n_replays),
        "replay_share": f"{replay_share['goals about what xG predicted']:.1%}",
        "replay_share_with_penalties": f"{replay_share['goals about what xG predicted (check with penalties)']:.1%}",
        "far_fewer_pct": f"{FAR_FEWER_SHARE:.0%}",
        "far_fewer_max_goals": str(far_fewer_limit(replays)),
        # Possession (measure 5, D19).
        "juve_shots_per_100_rank": ordinal(shots_per_100_rank),
        "juve_shots_per_100_rank_n": str(shots_per_100_rank),
        "juve_xg_per_100_rank": ordinal(xg_per_100_rank),
        "juve_xg_per_100_rank_n": str(xg_per_100_rank),
        # The data checks and the download.
        "n_checks": str(len(checks)),
        "data_checks_table": checks_table(checks),
        "n_files": str(len(manifest)),
        "download_gb": f"{manifest['bytes'].sum() / 1e9:.1f} GB",
        "logo_url": LOGO_URL,
    }


def where_how_values(teams: pd.DataFrame, tests: pd.DataFrame) -> dict[str, str]:
    """The values of the second question (PLAN.md section 6b), already written as text."""
    part = tests.set_index("part")
    juve = teams.loc[TEAM]
    where_part_of_gap = float(part.loc["my expectation", "value"])
    n_tests = len(JUDGED_PARTS)
    return {
        # From the league's xG per shot to Juventus's, in two steps.
        "league_xg_per_shot_pct": f"{part.loc['league', 'value']:.1%}",
        "juve_place_xg_per_shot_pct": f"{juve['place_xg_per_shot']:.1%}",
        "gap_points": points(part.loc["gap", "value"]),
        "where_points": points(part.loc["where", "value"]),
        "how_points": points(part.loc["how", "value"]),
        "where_part_of_gap": f"{where_part_of_gap:.0%}",
        "how_part_of_gap": f"{1 - where_part_of_gap:.0%}",
        "where_share": f"{part.loc['where', 'share_of_random_sets']:.2%}",
        "how_share": f"{part.loc['how', 'share_of_random_sets']:.2%}",
        # The defenders in the way, and the nearest defender (shown, not judged).
        "defenders_rank": ordinal(int(part.loc["defenders in the way", "rank_of_20"])),
        "defenders_rank_n": str(int(part.loc["defenders in the way", "rank_of_20"])),
        "defenders_share": f"{part.loc['defenders in the way', 'share_of_random_sets']:.0%}",
        "check_defenders_rank": ordinal(int(part.loc["defenders in the way (check)", "rank_of_20"])),
        "nearest_defender_text": f"{-part.loc['nearest defender', 'value']:.2f} yards closer",
        "nearest_defender_rank": ordinal(int(part.loc["nearest defender", "rank_of_20"])),
        # The rules (config.py).
        "n_zones": str(N_DISTANCE_GROUPS * N_ANGLE_GROUPS),
        "n_distance_groups": str(N_DISTANCE_GROUPS),
        "n_angle_groups": str(N_ANGLE_GROUPS),
        "n_random_sets": f"{N_RANDOM_SETS:,}",
        "n_random_sets_ja": japanese_count(N_RANDOM_SETS),
        "supported_pct": f"{SUPPORTED_SHARE:.0%}",
        "min_players_in_frame": str(MIN_PLAYERS_IN_FRAME),
        "n_new_tests": str(n_tests),
        "any_new_test_pct": f"{n_tests * SUPPORTED_SHARE:.0%}",  # the most it can be, without assuming independence
    }


def points(share: float) -> str:
    """-0.0136 -> "1.4": a difference of two shares, in percentage points (the text says whether it is less)."""
    return f"{abs(100 * share):.1f}"


def all_goals_conceded(table: pd.DataFrame) -> pd.Series:
    """Every goal conceded: from shots (penalties included) and own goals.
    03_metrics.py checks that this equals the official table for every team."""
    return table["goals_conceded_with_penalties"] + table["own_goals_conceded"]


def fewest_shots_team(table: pd.DataFrame) -> str:
    return table["shots_conceded"].idxmin()


def far_fewer_limit(replays: pd.DataFrame) -> int:
    """The most goals that the replay would still have called "far fewer than xG" (a limit of the test, D17).

    A number of goals counts as "far fewer" if fewer than FAR_FEWER_SHARE of the replays end with
    that many goals or fewer.
    """
    counts = replays["replays_without_penalties"]
    share_at_or_below = counts.cumsum() / counts.sum()
    return int(replays.loc[share_at_or_below < FAR_FEWER_SHARE, "goals"].max())


def checks_table(checks: pd.DataFrame) -> str:
    """The data checks as a Markdown table, written from results/data_checks.csv."""
    lines = ["| Check | What is checked | Result |", "|---|---|---|"]
    for check in checks.itertuples():
        result = "passed" if check.passed else "failed"
        lines.append(f"| {check.check} | {check.description} | {result}: {check.detail} |")
    return "\n".join(lines)


def typed_numbers(template: str) -> list[str]:
    """The lines of a template that contain a typed digit.

    Placeholders, comments, code, web addresses and HTML tags are not text for the reader,
    so they are removed before looking for digits.
    """
    text = re.sub(r"<!--.*?-->", "", template, flags=re.DOTALL)  # comments
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)  # blocks of code
    text = re.sub(r"`[^`\n]*`", "", text)  # code inside a line
    text = re.sub(r"<[^>\n]+>", "", text)  # HTML tags, such as <img src="...">
    text = re.sub(r"\]\([^)\s]*\)", "]", text)  # the address of a link: [text](address)
    text = PLACEHOLDER.sub("", text)
    for term in TYPED_TERMS_ALLOWED:
        text = text.replace(term, "")
    return [line.strip() for line in text.splitlines() if re.search(r"\d", line)]


def fill(template: str, values: dict[str, str], name: str) -> str:
    missing = sorted(set(PLACEHOLDER.findall(template)) - set(values))
    if missing:
        sys.exit(f"templates/{name} uses placeholders with no value: {', '.join(missing)}")
    return PLACEHOLDER.sub(lambda match: values[match.group(1)], template)


def header(template_name: str) -> str:
    return (
        f"<!-- Written by src/05_report.py from templates/{template_name}. "
        "Do not edit this file: edit the template, then run run_all.py. -->\n"
    )


def ordinal(n: int) -> str:
    """1 -> 1st, 2 -> 2nd, 3 -> 3rd, 4 -> 4th, 11 -> 11th (the same as in 03_metrics.py)."""
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def count(n: int, word: str) -> str:
    """2, "shot" -> "2 shots"; 1, "team" -> "1 team"."""
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def japanese_count(n: int) -> str:
    """10000 -> "1 万" (Japanese counts large numbers in units of 10,000)."""
    return f"{n // 10_000} 万" if n % 10_000 == 0 else f"{n:,}"


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(RESULTS_DIR / name, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
