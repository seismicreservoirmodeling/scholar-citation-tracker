"""Fetch today's Google Scholar citation counts and record them in citations.csv.

Run daily by GitHub Actions (.github/workflows/collect.yml). Can also be run
locally:  pip install -r requirements.txt && python collector.py
"""

import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from scholarly import scholarly

PROFILE_ID = "U10cIV8AAAAJ"  # Google Scholar user ID (from the profile URL)
CSV_PATH = Path(__file__).with_name("citations.csv")
FIELDS = ["date", "total_citations", "year_citations", "fetched_at_utc"]
ATTEMPTS = 3


def fetch():
    """Return (total_citations, current_year_citations) from Google Scholar."""
    author = scholarly.search_author_id(PROFILE_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "counts"])
    total = int(author.get("citedby") or 0)
    per_year = author.get("cites_per_year") or {}
    year = datetime.now(timezone.utc).year
    year_cites = int(per_year.get(year, per_year.get(str(year), 0)) or 0)
    if total <= 0:
        raise RuntimeError("Scholar returned 0 total citations; treating as a failed fetch.")
    return total, year_cites


def read_rows():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(newline="") as f:
        return list(csv.DictReader(f))


def main():
    last_error = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            total, year_cites = fetch()
            break
        except Exception as exc:  # Scholar often rate-limits automated requests
            last_error = exc
            print(f"Attempt {attempt} failed: {exc}", file=sys.stderr)
            if attempt < ATTEMPTS:
                time.sleep(60 * attempt)
    else:
        print("Could not fetch citations from Google Scholar.", file=sys.stderr)
        raise SystemExit(f"Last error: {last_error}")

    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    new_row = {
        "date": today,
        "total_citations": str(total),
        "year_citations": str(year_cites),
        "fetched_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # One row per date: replace today's row if the workflow ran twice.
    rows = [r for r in read_rows() if r.get("date") != today]
    rows.append(new_row)
    rows.sort(key=lambda r: r["date"])

    with CSV_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved snapshot: {new_row}  ({len(rows)} days recorded)")


if __name__ == "__main__":
    main()
