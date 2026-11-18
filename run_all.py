"""Run every step of the analysis in order, with one command.

Run from the project root:
    .venv\\Scripts\\python run_all.py

Each step is a separate script in src/. If a step fails (for example a data
check), the run stops there, so later steps never use data that failed a check.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    "src/01_download.py",  # download the raw StatsBomb files (files already here are skipped)
    "src/02_checks.py",  # the data checks -> results/data_checks.csv
]

for step in STEPS:
    print(f"\n=== {step} ===", flush=True)
    # sys.executable is the Python running this file, so every step uses the same virtual environment.
    finished = subprocess.run([sys.executable, str(ROOT / step)], cwd=ROOT)
    if finished.returncode != 0:
        sys.exit(f"Stopped: {step} failed, so the later steps were not run.")
print("\nAll steps finished.")
