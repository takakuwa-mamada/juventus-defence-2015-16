"""Step 6: print the one-page summaries to PDF (PLAN.md section 4, D25).

Run from the project root:
    .venv\\Scripts\\python src\\06_pdf.py

Each summary (docs/summary_en.md and docs/summary_ja.md, written by 05_report.py) is turned into a
web page with Python-Markdown. A web browser without a window (Microsoft Edge, or Google Chrome)
prints the page to a PDF next to the summary. The script stops if a summary does not fit on one page.

A PDF stores the time when it was printed. So a new print is compared with the old PDF without those
times, and the old file is kept if nothing else changed: a rerun does not change the PDFs.
If no browser is found, this step is skipped with a message. The Markdown summaries are still up to date.
"""
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import markdown

from config import DOCS_DIR, LOGO_FILE, LOGO_URL, ROOT

SUMMARIES = ["summary_en", "summary_ja"]  # the last two letters are the language
# The usual places of Edge and Chrome. If neither is there, the browser is looked for by its name.
BROWSER_FILES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
BROWSER_NAMES = ["msedge", "microsoft-edge", "google-chrome", "chrome", "chromium"]
# The two times that a PDF stores when it is printed.
PRINT_TIMES = re.compile(rb"/(CreationDate|ModDate) ?\([^)]*\)")

# One A4 page. The text uses the same ink colours as the charts (04_charts.py).
STYLE = """
@page { size: A4; margin: 12mm 14mm; }
html { font-size: 9.3pt; }
body { margin: 0; color: #0b0b0b; line-height: 1.4; font-family: "Segoe UI", Arial, sans-serif; }
html[lang="ja"] body { font-family: "Yu Gothic", YuGothic, Meiryo, sans-serif; font-weight: 500; line-height: 1.55; }
h1 { font-size: 18pt; line-height: 1.2; margin: 0 0 2pt; }
h1 + p { color: #52514e; margin: 0 0 8pt; }
p { margin: 0 0 5pt; }
ul { margin: 0 0 6pt; padding-left: 14pt; }
li { margin: 0 0 2pt; }
em { color: #52514e; }
a { color: inherit; text-decoration: none; }
img { vertical-align: top; }
"""


def main() -> int:
    browser = find_browser()
    if browser is None:
        print("Skipped: neither Microsoft Edge nor Google Chrome was found, so no PDF was printed. "
              "The Markdown summaries in docs/ are up to date.")
        return 0
    if not LOGO_FILE.exists():
        sys.exit(f"StatsBomb's logo is missing ({LOGO_FILE}). Run src/01_download.py first.")

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        for name in SUMMARIES:
            summary = (DOCS_DIR / f"{name}.md").read_text(encoding="utf-8")
            page = Path(tmp) / f"{name}.html"
            page.write_text(web_page(summary, language=name[-2:]), encoding="utf-8")
            new = Path(tmp) / f"{name}.pdf"
            print_pdf(browser, page, new, profile=Path(tmp) / f"browser-profile-{name}")
            pages = page_count(new)
            if pages != 1:
                sys.exit(f"{name}.pdf would have {pages} pages, but the summary must fit on one. "
                         f"Shorten templates/{name}.template.md.")
            out = DOCS_DIR / f"{name}.pdf"
            if out.exists() and same_print(out, new):
                print(f"Unchanged: {out.relative_to(ROOT).as_posix()}")
            else:
                shutil.copyfile(new, out)
                print(f"Written: {out.relative_to(ROOT).as_posix()} (1 page)")
    return 0


def find_browser() -> str | None:
    for file in BROWSER_FILES:
        if Path(file).exists():
            return file
    for name in BROWSER_NAMES:
        if shutil.which(name):
            return shutil.which(name)
    return None


def web_page(summary: str, language: str) -> str:
    """The summary as a web page.

    Pictures are found from docs/, as on GitHub. The logo is the downloaded copy instead of the
    online one, so printing also works offline.
    """
    title = next(line[2:] for line in summary.splitlines() if line.startswith("# "))
    body = markdown.markdown(summary).replace(LOGO_URL, LOGO_FILE.as_uri())
    return (
        f'<!doctype html>\n<html lang="{language}">\n<head>\n<meta charset="utf-8">\n'
        f'<base href="{DOCS_DIR.as_uri()}/">\n<title>{title}</title>\n<style>{STYLE}</style>\n</head>\n'
        f"<body>\n{body}\n</body>\n</html>\n"
    )


def print_pdf(browser: str, page: Path, pdf: Path, profile: Path) -> None:
    command = [
        browser, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
        f"--user-data-dir={profile}",  # a new, empty profile, so the user's own browser is not touched
        "--no-pdf-header-footer",  # no date, address or page number added by the browser
        f"--print-to-pdf={pdf}", page.as_uri(),
    ]
    finished = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace", timeout=180)
    if finished.returncode != 0 or not wait_for_pdf(pdf, seconds=60):
        sys.exit(f"The browser could not print {page.name}:\n{finished.stderr[-2000:]}")


def wait_for_pdf(pdf: Path, seconds: float) -> bool:
    """Wait until the PDF is complete. Edge can return before the PDF is written (another Edge process
    does the printing), so the file is checked until it ends with "%%EOF", the last line of every PDF."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if pdf.exists() and pdf.read_bytes().rstrip().endswith(b"%%EOF"):
            return True
        time.sleep(0.2)
    return False


def page_count(pdf: Path) -> int:
    """The number of pages. A PDF marks each page with "/Type /Page" (and the list of all pages with "/Pages")."""
    return len(re.findall(rb"/Type\s*/Page\b", pdf.read_bytes()))


def same_print(old: Path, new: Path) -> bool:
    """True if two PDFs differ only in the times when they were printed."""
    return PRINT_TIMES.sub(b"", old.read_bytes()) == PRINT_TIMES.sub(b"", new.read_bytes())


if __name__ == "__main__":
    sys.exit(main())
