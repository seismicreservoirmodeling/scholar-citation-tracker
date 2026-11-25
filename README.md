# Scholar Citation Tracker — web edition

A private dashboard configured for Dario Grana's Google Scholar profile:

- Scholar ID: `U10cIV8AAAAJ`
- Profile: https://scholar.google.com/citations?user=U10cIV8AAAAJ&hl=en

The application is designed to be deployed on Streamlit Community Cloud, with
Supabase storing citation snapshots and GitHub Actions collecting one snapshot
per day.

## What it measures

- Total citations: latest recorded Google Scholar total.
- Year-to-date citations: Google Scholar's citation histogram for the current
  calendar year.
- YTD daily average: current-year citations divided by elapsed calendar days.
- 30-day and 90-day daily averages: changes in total citations between the
  latest observation and the latest stored observation at least 30 or 90 days
  earlier.
- Historical chart and CSV export.

**Important:** Google Scholar's yearly histogram is by citation year; it is not
a daily history. Real 30/90-day rates require saved snapshots. Those metrics
will show "Collecting data" until enough history exists.

## Deploy it

You will need accounts at GitHub, Supabase, and Streamlit Community Cloud.
The accounts can be on their free tiers, subject to their current limits.

### 1. Create the Supabase database

1. Create a Supabase project at https://supabase.com/.
2. Open **SQL Editor** in the project dashboard.
3. Paste and run the contents of `schema.sql`.
4. In **Project Settings → API**, copy:
   - Project URL
   - `anon` / publishable key
   - `service_role` / secret key

Keep the service-role key private. Never put it in the Streamlit app's public
code or in a public GitHub file.

### 2. Put the project on GitHub

1. Create a new GitHub repository, preferably private.
2. Add all files in this folder, including the `.github/workflows` directory.
3. In the repository, open **Settings → Secrets and variables → Actions**.
4. Create these repository secrets:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_SERVICE_ROLE_KEY` = your Supabase service-role key

### 3. Test the daily collector

1. Open the repository's **Actions** tab.
2. Select **Daily Google Scholar citation collection**.
3. Choose **Run workflow**.
4. Check the run log. A successful run writes one row to
   `citation_snapshots` in Supabase.
5. Repeat manually if needed to test; the table stores one snapshot per date.

The workflow is scheduled daily at 14:17 UTC. GitHub scheduled workflows can
start later than the exact scheduled minute.

### 4. Deploy the dashboard

1. Sign in at https://share.streamlit.io/ using GitHub.
2. Choose **Create app** and select your repository.
3. Set the main file path to `app.py`.
4. Deploy.
5. In the Streamlit app settings, open **Secrets** and add:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_KEY = "YOUR-ANON-KEY"
```

6. Save and reboot the app.

Your dashboard will have a Streamlit-hosted URL. You can bookmark it. For
privacy, keep the GitHub repository private and use any access-control options
currently offered by your Streamlit hosting plan. Do not assume an unlisted URL
is private.

## Limitations and reliability

Google Scholar does not provide an official public API. This project uses the
unofficial `scholarly` Python package. Google may rate-limit or block automated
requests, so daily collection is best-effort, not guaranteed. Do not attempt to
evade access controls. If collection becomes unreliable, consider a licensed
scholarly-data provider or manual CSV imports.

The initial database has no backfilled daily history. The 30-day average becomes
available after at least 30 days of snapshots; the 90-day average after at least
90 days. Missing collection days can make the observation interval longer, and
the app divides by the actual elapsed days between observations.

## Local test (optional)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export SUPABASE_URL="https://YOUR-PROJECT.supabase.co"
export SUPABASE_KEY="YOUR-ANON-KEY"
streamlit run app.py
```
