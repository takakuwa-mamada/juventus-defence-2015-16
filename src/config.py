"""Settings shared by all scripts: folders, data version and the season to study.

The other scripts import their settings from here, so a change is made in one place.
"""
from pathlib import Path

# Project folder (this file is in <project>/src/).
ROOT = Path(__file__).resolve().parents[1]

# Raw StatsBomb files, saved unchanged. Not in git (see .gitignore).
RAW_DIR = ROOT / "data" / "raw"
# Small tables written by the scripts. These are in git.
RESULTS_DIR = ROOT / "results"
# Final league tables typed in from public sources, for data checks 5 and 7 (D14).
REFERENCE_DIR = ROOT / "reference"
OFFICIAL_TABLE = REFERENCE_DIR / "final_table_legaseriea.csv"
SECOND_TABLE = REFERENCE_DIR / "final_table_rsssf.csv"

# The version of the StatsBomb open-data repository that this project uses.
# Downloading from one fixed commit (not from "master") means that a rerun
# gets exactly the same files, even if StatsBomb changes the data later.
OPEN_DATA_COMMIT = "4b73468fc5b0f1950f9f66fada70ad3a4f9327cb"
BASE_URL = f"https://raw.githubusercontent.com/statsbomb/open-data/{OPEN_DATA_COMMIT}/data"

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
