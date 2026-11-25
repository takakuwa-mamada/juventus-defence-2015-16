"""Settings shared by all scripts: folders, data version and the season to study.

The other scripts import their settings from here, so a change is made in one place.
"""
import urllib.parse
from pathlib import Path

# Project folder (this file is in <project>/src/).
ROOT = Path(__file__).resolve().parents[1]

# Downloaded files. Not in git (see .gitignore).
DATA_DIR = ROOT / "data"
# Raw StatsBomb files, saved unchanged.
RAW_DIR = DATA_DIR / "raw"
# Small tables and the charts written by the scripts. These are in git.
RESULTS_DIR = ROOT / "results"
CHARTS_DIR = RESULTS_DIR / "charts"
# The text of the README and of the one-page summaries, with a placeholder for every number (D23),
# and the folder where the summaries are written.
TEMPLATES_DIR = ROOT / "templates"
DOCS_DIR = ROOT / "docs"
# Final league tables typed in from public sources, for data checks 5 and 7 (D14).
REFERENCE_DIR = ROOT / "reference"
OFFICIAL_TABLE = REFERENCE_DIR / "final_table_legaseriea.csv"
SECOND_TABLE = REFERENCE_DIR / "final_table_rsssf.csv"

# The version of the StatsBomb open-data repository that this project uses.
# Downloading from one fixed commit (not from "master") means that a rerun
# gets exactly the same files, even if StatsBomb changes the data later.
OPEN_DATA_COMMIT = "4b73468fc5b0f1950f9f66fada70ad3a4f9327cb"
REPO_URL = f"https://raw.githubusercontent.com/statsbomb/open-data/{OPEN_DATA_COMMIT}"
BASE_URL = f"{REPO_URL}/data"
# StatsBomb's logo, from the same commit. The user agreement asks for it on published
# analysis, so every chart shows it (D22). Like the data, it is downloaded, not committed.
LOGO_REL_PATH = "img/SB - Icon Lockup - Colour positive.png"
LOGO_FILE = DATA_DIR / LOGO_REL_PATH
# The README cannot show a file that is not committed, so it shows the logo from the same commit online.
LOGO_URL = f"{REPO_URL}/{urllib.parse.quote(LOGO_REL_PATH)}"

# The season is found by name in competitions.json. Its ids are never typed in.
COMPETITION_NAME = "Serie A"
SEASON_NAME = "2015/2016"
TEAM = "Juventus"

# League format: 20 teams, and every team plays every other team twice
# (once at home and once away). The counts expected in data check 2 follow from this.
N_TEAMS = 20
MATCHES_PER_TEAM = 2 * (N_TEAMS - 1)
N_MATCHES = N_TEAMS * (N_TEAMS - 1)

# The season replay for "goals vs. xG" (PLAN.md section 6, D17). The seed was fixed
# before any replay was run, so every computer gets the same replays.
SEED = 2016
N_REPLAYS = 10_000
# "Far fewer goals than xG" if fewer than this share of the replays end with
# as few goals as Juventus really conceded (or fewer).
FAR_FEWER_SHARE = 0.05

# The second question (PLAN.md section 6b, D30), fixed before any of its results was calculated.
# The zones of the pitch: groups of the same size by distance, then by angle inside each.
N_DISTANCE_GROUPS = 10
N_ANGLE_GROUPS = 3
# The check: "defenders in the way" again, with only the frames that show at least this many players.
MIN_PLAYERS_IN_FRAME = 8
# The random sets of team-matches that Juventus is compared with (they use SEED, like the replays),
# and the share below which a part is supported.
N_RANDOM_SETS = 10_000
SUPPORTED_SHARE = 0.05
# My expectation (D30): the where part and the how part are "about the same size", which means
# that each of them is between a third and two thirds of Juventus's gap.
ABOUT_THE_SAME_SIZE = (1 / 3, 2 / 3)

# The third question (PLAN.md section 6c, D36) uses the same zones, random sets and 5% line as the second.
# My expectation (D36): the three kinds explain "most" of Juventus's how part, which means two thirds or more.
MOST_OF_THE_HOW_PART = 2 / 3
