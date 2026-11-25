# Scholar Citation Tracker

Tracks Dario Grana's Google Scholar citations (profile `U10cIV8AAAAJ`) using only GitHub:

- **GitHub Actions** fetches the citation counts once a day and saves them to `citations.csv`.
- **GitHub Pages** hosts `index.html`, a dashboard showing total citations, citations this
  year, the daily average for the year, and the daily averages over the last 30 and 90 days.

No other accounts, databases, or keys are needed.

## Files

| File | What it does |
|---|---|
| `index.html` | The dashboard page |
| `collector.py` | Fetches the counts from Google Scholar and updates `citations.csv` |
| `requirements.txt` | The Python package the collector needs |
| `.github/workflows/collect.yml` | Runs the collector every day |
| `citations.csv` | Created automatically on the first run |

## Setup (about 10 minutes)

### 1. Create the repository
1. Sign in at https://github.com and click **New** (the green button, or **+ → New repository**).
2. Name it, e.g. `scholar-tracker`. Choose **Public** (needed for free GitHub Pages).
3. Click **Create repository**.

### 2. Upload the files
1. On the new repository page, click **uploading an existing file**.
2. Drag in `index.html`, `collector.py`, `requirements.txt`, and `README.md`, then click **Commit changes**.

### 3. Add the workflow file
On a Mac, the `.github` folder is hidden in Finder, so create this file in the browser instead:
1. Click **Add file → Create new file**.
2. Type this exact name: `.github/workflows/collect.yml`. The slashes create the folders automatically.
3. Paste in the contents of `collect.yml` and click **Commit changes**.

### 4. Allow the workflow to save data
1. Go to **Settings → Actions → General**.
2. Under **Workflow permissions**, select **Read and write permissions** and click **Save**.

### 5. Run it once
1. Open the **Actions** tab. If asked, click the button to enable workflows.
2. Click **Daily citation snapshot → Run workflow → Run workflow**.
3. After 1–2 minutes it should show a green check, and `citations.csv` will appear in the repository.
   A red X means Google Scholar blocked the request (see *If collection fails* below).

### 6. Turn on the dashboard
1. Go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**, choose branch **main**
   and folder **/ (root)**, then click **Save**.
3. After a minute or two, the page shows your site address, something like
   `https://YOUR-USERNAME.github.io/scholar-tracker/`. **Bookmark it.** That's your one click.

From then on, the workflow runs every day at 14:17 UTC (6:17 am Pacific). GitHub sometimes starts
scheduled runs a bit late.

## What the numbers mean

- **Daily average this year** = Scholar's citation count for the current year ÷ days elapsed this
  year. It's available immediately.
- **Daily averages over the last 30 and 90 days** = the change in total citations between today's
  snapshot and the one from at least 30 or 90 days earlier, divided by the actual number of days
  between them. Scholar doesn't publish daily or monthly data, so these averages appear only after
  30 and 90 days of collected history. Until then, the page shows a preliminary rate based on the
  history collected so far. A missed day doesn't break anything; it just widens the interval.

## If collection fails

Google Scholar has no official API and sometimes blocks automated requests from cloud servers like
GitHub's. The script retries three times. If runs keep failing:

- Occasional failures are harmless; the next day's run fills in.
- If it fails every day, run the collector on your own computer instead, where Scholar is much less
  likely to block it, and upload the updated `citations.csv` to the repository:
  ```bash
  pip install -r requirements.txt
  python collector.py
  ```
  The dashboard works the same either way.

The page shows a red warning next to "Latest snapshot" if no new data has arrived for more than two days.

GitHub may pause scheduled workflows in repositories with no activity for 60 days. If you get an email
about that, open the **Actions** tab and re-enable the workflow.

## Tracking a different researcher

Change `PROFILE_ID` at the top of `collector.py` and in `index.html`, and update the name in `index.html`.
