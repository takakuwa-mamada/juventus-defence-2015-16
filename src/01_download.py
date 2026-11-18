"""Step 1: download the raw StatsBomb files for Serie A 2015/16.

Run from the project root:
    .venv\\Scripts\\python src\\01_download.py

Files that are already in data/raw/ are not downloaded again. At the end, the
size and fingerprint of every raw file are written to results/data_manifest.csv.
"""
import sbdata
from config import COMPETITION_NAME, DATA_DIR, LOGO_REL_PATH, RAW_DIR, REPO_URL, RESULTS_DIR, SEASON_NAME


def main() -> None:
    # The season's ids are looked up by name, not typed in (data check 1).
    sbdata.download_file("competitions.json")
    competitions = sbdata.read_json("competitions.json")
    competition_id, season_id = sbdata.find_season(competitions, COMPETITION_NAME, SEASON_NAME)
    print(f"{COMPETITION_NAME} {SEASON_NAME}: competition_id={competition_id}, season_id={season_id}")

    matches_path = f"matches/{competition_id}/{season_id}.json"
    sbdata.download_file(matches_path)
    match_ids = [m["match_id"] for m in sbdata.read_json(matches_path)]
    print(f"Matches in the season file: {len(match_ids)}")

    # One events file per match, downloaded one after another (polite to the server).
    downloaded = 0
    for i, match_id in enumerate(match_ids, start=1):
        downloaded += sbdata.download_file(f"events/{match_id}.json")
        if i % 20 == 0 or i == len(match_ids):
            print(f"  events files ready: {i}/{len(match_ids)} (downloaded in this run: {downloaded})", flush=True)

    # StatsBomb's logo, for the credit on every chart (D22). It is not data, so it is not in the manifest.
    sbdata.download_file(LOGO_REL_PATH, raw_dir=DATA_DIR, base_url=REPO_URL)

    manifest = sbdata.write_manifest(RAW_DIR, RESULTS_DIR / "data_manifest.csv")
    total_mb = manifest["bytes"].sum() / 1_000_000
    print(f"Manifest: {len(manifest)} files, {total_mb:.0f} MB -> results/data_manifest.csv")


if __name__ == "__main__":
    main()
