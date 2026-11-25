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
    "src/03_metrics.py",  # the measures and the hypothesis tests -> results/team_metrics.csv and 2 more
    "src/03b_where_how.py",  # the second question, where and how (PLAN.md section 6b) -> results/where_how_*.csv
    "src/03c_how_kinds.py",  # the third question, what the how part is made of (PLAN.md section 6c) -> results/how_kinds_*.csv
    "src/04_charts.py",  # the four charts -> results/charts/
    "src/05_report.py",  # the text, with every number from results/ -> README.md and docs/summary_*.md
    "src/06_pdf.py",  # the one-page summaries printed to PDF -> docs/summary_*.pdf (needs Edge or Chrome)
]

for step in STEPS:
    print(f"\n=== {step} ===", flush=True)
    # sys.executable is the Python running this file, so every step uses the same virtual environment.
    finished = subprocess.run([sys.executable, str(ROOT / step)], cwd=ROOT)
    if finished.returncode != 0:
        sys.exit(f"Stopped: {step} failed, so the later steps were not run.")
print("\nAll steps finished.")
