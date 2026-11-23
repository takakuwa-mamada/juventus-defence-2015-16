"""Step 4: draw the four charts from the results tables (PLAN.md sections 4 and 6b, D21, D22, D32).

Run from the project root:
    .venv\\Scripts\\python src\\04_charts.py

Every number on a chart is read from the tables in results/ (written by
03_metrics.py and 03b_where_how.py). None is typed in. The charts are written to results/charts/.
The titles were written for the current results: if a result changes, the
script stops and asks for new titles, so a chart can never say the opposite
of its results table.
"""
import sys
import textwrap

import matplotlib
import matplotlib.image as mpimg
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, PercentFormatter

from config import CHARTS_DIR, COMPETITION_NAME, FAR_FEWER_SHARE, LOGO_FILE, RESULTS_DIR, ROOT, SEASON_NAME, TEAM

# Colours. Juventus orange and the grey of the other teams stay distinct for
# colour-blind readers, and both stand out from the background (checked with a
# palette checker on 2026-11-18). Text is never in a data colour.
TEAM_COLOUR = "#eb6834"
OTHER_COLOUR = "#94928a"
BACKGROUND = "#fcfcfb"
INK = "#0b0b0b"  # titles, and the labels that matter
INK_SECONDARY = "#52514e"  # subtitles, axis labels and tick labels
INK_MUTED = "#898781"  # the data credit
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

# Sizes. Every chart is 6 inches wide (1,200 pixels). On a phone 375 pixels wide, GitHub shows it
# 309 pixels wide (checked on 2026-11-18, D27). The subtitle (14 points) is then about 10 pixels high
# and the smallest text (the footer, 10 points) about 7: small, but readable without zooming.
WIDTH_IN = 6.0
SIDE_IN = 0.3  # empty margin on the left and right
TITLE_PT, SUBTITLE_PT, LABEL_PT, TICK_PT, FOOTER_PT = 18, 14, 13, 12, 10
TITLE_CHARS, SUBTITLE_CHARS = 34, 51  # characters per line before a line break (fits DejaVu Sans)
FOOTER_IN = 0.6
DPI = 200
CREDIT = f"Data: StatsBomb · {COMPETITION_NAME} {SEASON_NAME} · penalties excluded"


def main() -> int:
    # Ignore any personal matplotlib settings on this computer (for example a Japanese font),
    # so the charts look the same everywhere. DejaVu Sans comes with matplotlib.
    matplotlib.rcdefaults()
    matplotlib.rcParams["font.family"] = "DejaVu Sans"

    table = pd.read_csv(RESULTS_DIR / "team_metrics.csv", encoding="utf-8").set_index("team")
    tests = pd.read_csv(RESULTS_DIR / "hypothesis_tests.csv", encoding="utf-8")
    replays = pd.read_csv(RESULTS_DIR / "replay_distribution.csv", encoding="utf-8")
    where_how_teams = pd.read_csv(RESULTS_DIR / "where_how_teams.csv", encoding="utf-8").set_index("team")
    where_how_tests = pd.read_csv(RESULTS_DIR / "where_how_tests.csv", encoding="utf-8")
    if not LOGO_FILE.exists():
        sys.exit(f"StatsBomb's logo is missing ({LOGO_FILE}). Run src/01_download.py first.")
    logo = mpimg.imread(LOGO_FILE)

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    save(chances_chart(table, tests, logo), "1_chances.png")
    save(goals_vs_xg_chart(table, logo), "2_goals_vs_xg.png")
    save(replays_chart(table, tests, replays, logo), "3_replays.png")
    save(where_how_chart(where_how_teams, where_how_tests, logo), "4_where_how.png")
    return 0


def chances_chart(table: pd.DataFrame, tests: pd.DataFrame, logo) -> Figure:
    """Chart 1: how many chances each team allowed, and how good they were (measures 1 and 2)."""
    expect_result(tests, "fewest chances", "not supported")
    expect_result(tests, "weakest chances", "supported")
    juve = table.loc[TEAM]
    fewest = table["shots_conceded"].idxmin()
    extra_shots = int(juve["shots_conceded"] - table.loc[fewest, "shots_conceded"])
    title = f"{TEAM} allowed the weakest chances, but not the fewest"
    subtitle = (
        f"Each dot is a team. {TEAM} faced only {extra_shots} shots more than {fewest} all season "
        f"({juve['shots_conceded_per_match']:.1f} and {table.loc[fewest, 'shots_conceded_per_match']:.1f} "
        f"per match), but the average shot had just a {juve['xg_per_shot_conceded']:.1%} chance of "
        f"going in (its xG), the lowest of the {len(table)} teams."
    )
    fig, ax = new_chart(title, subtitle, plot_in=3.9, left_in=1.25, bottom_in=0.7, logo=logo)

    x, y = table["shots_conceded_per_match"], table["xg_per_shot_conceded"]
    others = table.index != TEAM
    # A ring in the background colour keeps dots apart where they touch.
    ax.scatter(x[others], y[others], s=70, color=OTHER_COLOUR, edgecolor=BACKGROUND, linewidth=1.5, zorder=3)
    ax.scatter(x[TEAM], y[TEAM], s=140, color=TEAM_COLOUR, edgecolor=BACKGROUND, linewidth=2, zorder=4)
    # Name only the three teams that allowed the fewest shots: only one of them kept the shots weak.
    for team in table.nsmallest(3, "shots_conceded_per_match").index:
        is_team = team == TEAM
        ax.annotate(
            team, (x[team], y[team]), xytext=(9, 0), textcoords="offset points", va="center",
            fontsize=LABEL_PT, color=INK if is_team else INK_SECONDARY, fontweight="bold" if is_team else "normal",
        )
    ax.grid(color=GRID, linewidth=0.8)
    ax.margins(x=0.08, y=0.1)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    ax.set_xlabel("Shots conceded per match  (← fewer)", fontsize=LABEL_PT, color=INK_SECONDARY)
    ax.set_ylabel("Average chance that a shot goes in\n(xG per shot, ← lower)", fontsize=LABEL_PT,
                  color=INK_SECONDARY)
    return fig


def goals_vs_xg_chart(table: pd.DataFrame, logo) -> Figure:
    """Chart 2: goals conceded minus xG conceded for all 20 teams (measure 4, the picture promised in D17)."""
    gap = table["goals_minus_xg"].sort_values()  # the furthest below xG first
    if gap[TEAM] >= 0:
        sys.exit("The title of chart 2 was written for fewer goals than xG. Rewrite it in src/04_charts.py.")
    bigger_gap = int((gap < gap[TEAM]).sum())
    title = f"{TEAM} conceded {-gap[TEAM]:.1f} goals fewer than xG; {bigger_gap} teams had a bigger gap"
    subtitle = (
        "Goals conceded from shots minus xG conceded (what the chances were worth). "
        "Below zero: fewer goals than expected. No penalties or own goals."
    )
    fig, ax = new_chart(title, subtitle, plot_in=5.6, left_in=1.75, bottom_in=0.7, logo=logo)

    rows = range(len(gap))
    colours = [TEAM_COLOUR if team == TEAM else OTHER_COLOUR for team in gap.index]
    ax.barh(rows, gap.values, height=0.55, color=colours, linewidth=0, zorder=3)
    ax.set_yticks(list(rows), gap.index)
    ax.invert_yaxis()  # the team furthest below xG at the top
    ax.axvline(0, color=AXIS, linewidth=1, zorder=2)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    for label in ax.get_yticklabels():
        if label.get_text() == TEAM:
            label.set_color(INK)
            label.set_fontweight("bold")
    # Only Juventus's bar gets its value, at the end of the bar.
    ax.annotate(
        f"{gap[TEAM]:.1f}".replace("-", "−"), (gap[TEAM], list(gap.index).index(TEAM)), xytext=(-6, 0),
        textcoords="offset points", ha="right", va="center", fontsize=LABEL_PT, color=INK, fontweight="bold",
    )
    ax.set_xlabel("Goals minus xG  (← fewer than expected)", fontsize=LABEL_PT, color=INK_SECONDARY)
    return fig


def replays_chart(table: pd.DataFrame, tests: pd.DataFrame, replays: pd.DataFrame, logo) -> Figure:
    """Chart 3: the goals Juventus conceded in each replay of their season (D17)."""
    part = "goals about what xG predicted"
    expect_result(tests, part, "not far fewer")
    juve = table.loc[TEAM]
    goals, xg = int(juve["goals_conceded_from_shots"]), float(juve["xg_conceded"])
    share = float(tests.loc[tests["part"] == part, "share_of_replays_at_or_below"].item())
    n_replays = int(replays["replays_without_penalties"].sum())
    title = f"{TEAM}'s {goals} goals conceded are within what chance can explain"
    subtitle = (
        f"We replayed the season {n_replays:,} times; each shot faced scored with a probability equal to "
        f"its xG. {share:.1%} of the replays ended with {goals} goals or fewer (orange). Under "
        f"{FAR_FEWER_SHARE:.0%} would have meant far fewer than xG (rule fixed in advance)."
    )
    fig, ax = new_chart(title, subtitle, plot_in=3.7, left_in=1.05, bottom_in=0.7, logo=logo)

    shown = replays[replays["replays_without_penalties"] > 0]
    percent = 100 * shown["replays_without_penalties"] / n_replays
    colours = [TEAM_COLOUR if g <= goals else OTHER_COLOUR for g in shown["goals"]]
    ax.bar(shown["goals"], percent, width=0.8, color=colours, linewidth=0, zorder=3)
    ax.axvline(xg, color=INK_SECONDARY, linewidth=1.2, zorder=4)
    top = percent.max()
    ax.annotate(f"Expected: {xg:.1f} (xG)", (xg, top * 1.06), xytext=(6, 0), textcoords="offset points",
                ha="left", va="center", fontsize=LABEL_PT, color=INK_SECONDARY)
    at_goals = float(percent[shown["goals"] == goals].iloc[0])
    ax.annotate(f"Actual: {goals}", (goals, at_goals), xytext=(-8, 14), textcoords="offset points",
                ha="right", va="bottom", fontsize=LABEL_PT, color=INK, fontweight="bold")
    ax.set_ylim(0, top * 1.15)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.set_xlabel("Goals conceded in one replay", fontsize=LABEL_PT, color=INK_SECONDARY)
    ax.set_ylabel("Share of the replays", fontsize=LABEL_PT, color=INK_SECONDARY)
    return fig


def where_how_chart(teams: pd.DataFrame, tests: pd.DataFrame, logo) -> Figure:
    """Chart 4: from the league's xG per shot to Juventus's, in two steps: where and how (PLAN.md 6b, D32)."""
    for part in ("where", "how"):
        expect_result(tests, part, "supported")
        if tests.loc[tests["part"] == part, "rank_of_20"].item() != 1:
            sys.exit(f"The subtitle of chart 4 says the {part} part was the lowest. Rewrite it in src/04_charts.py.")
    expect_result(tests, "my expectation", "met")  # the title says "about the same size"
    league, where, how = (part_value(tests, part) for part in ("league", "where", "how"))
    juve = teams.loc[TEAM]
    place, actual = float(juve["place_xg_per_shot"]), float(juve["xg_per_shot_conceded"])
    # The two steps must lead from the league's bar to Juventus's. Every number in the tables is
    # rounded to 4 decimals, so a difference of up to 0.00015 is only rounding.
    if abs(league + where - place) > 0.00015 or abs(place + how - actual) > 0.00015:
        sys.exit("In results/where_how_*.csv, the league's value plus the two parts is not Juventus's value.")

    title = f"{TEAM}'s weak chances: two parts of about the same size"
    subtitle = (
        f"From the league's average xG per shot to {TEAM}'s. Where: what shots from about the same "
        "distance and angle are worth on average. How: the rest. Each part was the lowest of the "
        f"{len(teams)} teams, and unlikely to be chance (rule fixed in advance)."
    )
    fig, ax = new_chart(title, subtitle, plot_in=2.4, left_in=1.75, bottom_in=0.95, logo=logo)

    # From the top: the league, the two steps, Juventus. Each step starts where the bar above ended,
    # and a thin dashed line joins them. Grey is the league; orange is Juventus and its two parts.
    names = ["League average", "Where the shots\nwere taken", "How (from the\nsame places)", TEAM]
    starts = [0, place, actual, 0]
    ends = [league, league, place, actual]
    colours = [OTHER_COLOUR, TEAM_COLOUR, TEAM_COLOUR, TEAM_COLOUR]
    rows = list(range(len(names)))
    height = 0.55
    ax.barh(rows, [end - start for start, end in zip(starts, ends)], left=starts, height=height,
            color=colours, linewidth=0, zorder=3)
    for row, x in enumerate([league, place, actual]):
        ax.plot([x, x], [row + height / 2, row + 1 - height / 2], color=INK_MUTED, linewidth=1,
                linestyle=(0, (2, 2)), zorder=2)
    ax.set_yticks(rows, names)
    ax.invert_yaxis()  # the league at the top, Juventus at the bottom
    for label in ax.get_yticklabels():
        if label.get_text() == TEAM:
            label.set_color(INK)
            label.set_fontweight("bold")

    # The values: the two totals at the right end of their bars, each step at the end it moves to.
    def minus(text: str) -> str:
        return text.replace("-", "−")

    ax.annotate(f"{league:.1%}", (league, 0), xytext=(6, 0), textcoords="offset points", ha="left",
                va="center", fontsize=LABEL_PT, color=INK_SECONDARY)
    for row, (step, x) in enumerate([(where, place), (how, actual)], start=1):
        ax.annotate(minus(f"{100 * step:.1f}"), (x, row), xytext=(-6, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=LABEL_PT, color=INK, fontweight="bold")
    ax.annotate(f"{actual:.1%}", (actual, 3), xytext=(6, 0), textcoords="offset points", ha="left",
                va="center", fontsize=LABEL_PT, color=INK, fontweight="bold")

    ax.set_xlim(0, league * 1.2)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    ax.set_xlabel("Average chance that a shot goes in\n(xG per shot, ← lower)", fontsize=LABEL_PT,
                  color=INK_SECONDARY)
    return fig


def new_chart(title: str, subtitle: str, plot_in: float, left_in: float, bottom_in: float, logo):
    """A chart with a title, a subtitle, one plot, and a footer with the data credit and StatsBomb's logo.

    Sizes are set in inches, so the text has the same size on all the charts.
    plot_in: height of the plot; left_in and bottom_in: room for the tick labels and axis labels.
    """
    title_lines = textwrap.wrap(title, TITLE_CHARS)
    subtitle_lines = textwrap.wrap(subtitle, SUBTITLE_CHARS)
    title_in = len(title_lines) * TITLE_PT * 1.2 / 72  # 72 points in an inch
    subtitle_in = len(subtitle_lines) * SUBTITLE_PT * 1.35 / 72
    top_in = 0.25 + title_in + 0.12 + subtitle_in + 0.3
    height_in = top_in + plot_in + bottom_in + FOOTER_IN
    fig = Figure(figsize=(WIDTH_IN, height_in), facecolor=BACKGROUND)

    def fx(inches: float) -> float:  # inches from the left -> share of the width
        return inches / WIDTH_IN

    def fy(inches: float) -> float:  # inches from the bottom -> share of the height
        return inches / height_in

    y = height_in - 0.25
    fig.text(fx(SIDE_IN), fy(y), "\n".join(title_lines), ha="left", va="top", fontsize=TITLE_PT,
             fontweight="bold", color=INK, linespacing=1.2)
    y -= title_in + 0.12
    fig.text(fx(SIDE_IN), fy(y), "\n".join(subtitle_lines), ha="left", va="top", fontsize=SUBTITLE_PT,
             color=INK_SECONDARY, linespacing=1.35)

    ax = fig.add_axes((fx(left_in), fy(FOOTER_IN + bottom_in), fx(WIDTH_IN - left_in - SIDE_IN), fy(plot_in)))
    ax.set_facecolor(BACKGROUND)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.tick_params(length=0, pad=5, labelsize=TICK_PT, labelcolor=INK_SECONDARY)
    ax.set_axisbelow(True)

    # Footer: the data credit on the left and StatsBomb's logo on the right (D22).
    fig.text(fx(SIDE_IN), fy(FOOTER_IN / 2), CREDIT, ha="left", va="center", fontsize=FOOTER_PT, color=INK_MUTED)
    logo_w = 1.1
    logo_h = logo_w * logo.shape[0] / logo.shape[1]
    logo_ax = fig.add_axes((fx(WIDTH_IN - SIDE_IN - logo_w), fy(FOOTER_IN / 2 - logo_h / 2), fx(logo_w), fy(logo_h)))
    logo_ax.imshow(logo)
    logo_ax.axis("off")
    return fig, ax


def expect_result(tests: pd.DataFrame, part: str, start: str) -> None:
    """Stop if a result is not the one that the chart's title was written for."""
    result = tests.loc[tests["part"] == part, "result"].item()
    if not result.startswith(start):
        sys.exit(
            f"The chart titles were written for a result that starts with '{start}' in '{part}', "
            f"but the result is now '{result}'. Rewrite the titles in src/04_charts.py."
        )


def part_value(tests: pd.DataFrame, part: str) -> float:
    """The value of one part (one row) of a tests table."""
    return float(tests.loc[tests["part"] == part, "value"].item())


def save(fig: Figure, name: str) -> None:
    out = CHARTS_DIR / name
    # No software version in the file, so a rerun with the same libraries gives the same file.
    fig.savefig(out, dpi=DPI, facecolor=BACKGROUND, metadata={"Software": None})
    print(f"Written: {out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    sys.exit(main())
