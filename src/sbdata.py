"""Download and read the raw StatsBomb open-data files.

The files are saved unchanged in data/raw/, with the same paths as in the
StatsBomb open-data repository, so anyone can compare them with the source.
"""
import hashlib
import http.client
import json
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

from config import BASE_URL, RAW_DIR

# Waits between download tries, in seconds. A short break often fixes a
# temporary network or server problem.
RETRY_WAITS = (5, 15)


def download_file(rel_path: str, raw_dir: Path = RAW_DIR, base_url: str = BASE_URL) -> bool:
    """Download one file from the fixed open-data commit, unless it is already here.

    Returns True if the file was downloaded now, False if it was already on disk.
    The file is first written as "<name>.part" and renamed only when it is
    complete, so a broken connection never leaves a half file that looks complete.
    """
    target = raw_dir / rel_path
    if target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    # quote() writes spaces in a file name as %20, which a web address needs.
    url = f"{base_url}/{urllib.parse.quote(rel_path)}"
    for attempt in range(len(RETRY_WAITS) + 1):
        last_try = attempt == len(RETRY_WAITS)
        try:
            with urllib.request.urlopen(url, timeout=60) as response, open(part, "wb") as out:
                shutil.copyfileobj(response, out)
            part.replace(target)
            return True
        except urllib.error.HTTPError as error:
            # A wrong path or commit (404) will not be fixed by waiting.
            if error.code == 404 or last_try:
                raise
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, ConnectionError):
            if last_try:
                raise
        time.sleep(RETRY_WAITS[attempt])
    return False  # not reached: the last try either returns or raises


def read_json(rel_path: str, raw_dir: Path = RAW_DIR):
    """Read one raw file.

    StatsBomb files are UTF-8. Without encoding="utf-8", Windows would read
    them with another encoding and break names with accents.
    """
    with open(raw_dir / rel_path, encoding="utf-8") as f:
        return json.load(f)


def find_season(competitions: list[dict], competition_name: str, season_name: str) -> tuple[int, int]:
    """Return (competition_id, season_id), found by name so that ids are never typed in."""
    found = [
        (c["competition_id"], c["season_id"])
        for c in competitions
        if c["competition_name"] == competition_name and c["season_name"] == season_name
    ]
    if len(found) != 1:
        raise ValueError(
            f"Expected exactly 1 row for {competition_name} {season_name}, found {len(found)}: {found}"
        )
    return found[0]


def matches_table(matches_json: list[dict]) -> pd.DataFrame:
    """One row per match, with the final score from StatsBomb's matches file."""
    rows = [
        {
            "match_id": m["match_id"],
            "match_date": m["match_date"],
            "home_team": m["home_team"]["home_team_name"],
            "away_team": m["away_team"]["away_team_name"],
            "home_score": m["home_score"],
            "away_score": m["away_score"],
        }
        for m in matches_json
    ]
    return pd.DataFrame(rows).sort_values(["match_date", "match_id"]).reset_index(drop=True)


# The events needed for goals and xG. Everything else (passes, carries, ...) is left out.
KEPT_TYPES = ("Shot", "Own Goal For", "Own Goal Against")
# Columns of the table returned by load_events: one row per kept event.
EVENT_COLUMNS = ["match_id", "team", "type", "shot_outcome", "shot_type", "xg", "period", "minute"]


def shot_and_own_goal_rows(events: list[dict], match_id: int) -> list[dict]:
    """Keep only shots and own goals from one match's raw events.

    A match has thousands of events. Keeping only these makes the whole season
    small enough to hold in memory as one table.
    """
    rows = []
    for event in events:
        kind = event["type"]["name"]
        if kind not in KEPT_TYPES:
            continue
        shot = event.get("shot", {})  # only shots have this part; own goals do not
        rows.append(
            {
                "match_id": match_id,
                "team": event["team"]["name"],
                "type": kind,
                "shot_outcome": shot.get("outcome", {}).get("name"),
                "shot_type": shot.get("type", {}).get("name"),
                "xg": shot.get("statsbomb_xg"),
                "period": event["period"],
                "minute": event["minute"],
            }
        )
    return rows


def possession_rows(events: list[dict], match_id: int) -> list[dict]:
    """Count each team's possessions in one match (for the possession check, D19).

    StatsBomb numbers every possession (a sequence of play controlled by one team)
    and names the team that has the ball. All events of a possession share its
    number, so each (number, team) pair is counted once, however short it is.
    """
    pairs = {(event["possession"], event["possession_team"]["name"]) for event in events}
    teams = sorted({team for _, team in pairs})
    return [
        {"match_id": match_id, "team": team, "possessions": sum(1 for _, t in pairs if t == team)}
        for team in teams
    ]


def load_events(
    match_ids: list[int], raw_dir: Path = RAW_DIR
) -> tuple[pd.DataFrame, dict[int, int], pd.DataFrame]:
    """Read each match's events file, one at a time.

    Returns three things: the shots and own goals; the number of events in each
    file; and each team's possessions in each match. A missing file counts as
    0 events, so that data check 3 reports it as a failure.
    """
    rows, n_events, possessions = [], {}, []
    for match_id in match_ids:
        rel_path = f"events/{match_id}.json"
        if not (raw_dir / rel_path).exists():
            n_events[match_id] = 0
            continue
        events = read_json(rel_path, raw_dir)
        n_events[match_id] = len(events)
        rows.extend(shot_and_own_goal_rows(events, match_id))
        possessions.extend(possession_rows(events, match_id))
    return (
        pd.DataFrame(rows, columns=EVENT_COLUMNS),
        n_events,
        pd.DataFrame(possessions, columns=["match_id", "team", "possessions"]),
    )


def write_manifest(raw_dir: Path, out_csv: Path) -> pd.DataFrame:
    """Write the size and SHA-256 fingerprint of every raw file (D12).

    Anyone who downloads the same files gets the same fingerprints, so this
    table shows whether two people used exactly the same data.
    Unfinished ".part" files are left out because they do not end in ".json".
    """
    rows = []
    for path in raw_dir.rglob("*.json"):
        rows.append(
            {
                "path": path.relative_to(raw_dir).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    manifest = pd.DataFrame(rows, columns=["path", "bytes", "sha256"]).sort_values("path")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    # "\n" line endings, so the file is byte-for-byte the same on every computer.
    manifest.to_csv(out_csv, index=False, encoding="utf-8", lineterminator="\n")
    return manifest
