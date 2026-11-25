import os
from datetime import datetime, timezone

from scholarly import scholarly
from supabase import create_client

PROFILE_ID = "U10cIV8AAAAJ"


def main():
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_KEY"]
    client = create_client(supabase_url, supabase_key)

    # Google Scholar has no official public API. scholarly is an unofficial
    # interface; requests may be rate-limited or blocked by Google.
    author = scholarly.search_author_id(PROFILE_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "counts"])

    total_citations = int(author.get("citedby", 0))
    per_year = author.get("cites_per_year", {}) or {}
    current_year = datetime.now(timezone.utc).year
    year_citations = int(per_year.get(str(current_year), per_year.get(current_year, 0)))

    now = datetime.now(timezone.utc)
    row = {
        "observed_on": now.date().isoformat(),
        "total_citations": total_citations,
        "year_citations": year_citations,
        "fetched_at": now.isoformat(),
    }

    result = (
        client.table("citation_snapshots")
        .upsert(row, on_conflict="observed_on")
        .execute()
    )
    print(f"Saved citation snapshot: {row}")
    print(result)


if __name__ == "__main__":
    main()
