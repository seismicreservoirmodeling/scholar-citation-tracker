import os
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client


PROFILE_ID = "U10cIV8AAAAJ"
PROFILE_URL = f"https://scholar.google.com/citations?user={PROFILE_ID}&hl=en"


st.set_page_config(
    page_title="Scholar Citation Tracker",
    page_icon="📈",
    layout="wide",
)

st.title("Scholar Citation Tracker")
st.caption("Personal citation dashboard · Dario Grana")
st.markdown(f"[Open Google Scholar profile]({PROFILE_URL})")


def get_secret(name: str):
    try:
        return st.secrets[name]
    except Exception:
        return os.environ.get(name)


@st.cache_resource
def get_supabase():
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def load_data(client):
    result = (
        client.table("citation_snapshots")
        .select("observed_on,total_citations,year_citations,fetched_at")
        .order("observed_on")
        .execute()
    )
    df = pd.DataFrame(result.data or [])
    if not df.empty:
        df["observed_on"] = pd.to_datetime(df["observed_on"]).dt.date
        df["total_citations"] = pd.to_numeric(df["total_citations"])
        df["year_citations"] = pd.to_numeric(df["year_citations"])
    return df


def average_since(df: pd.DataFrame, days: int):
    if len(df) < 2:
        return None
    latest = df.iloc[-1]
    cutoff = latest["observed_on"] - timedelta(days=days)
    eligible = df[df["observed_on"] <= cutoff]
    if eligible.empty:
        return None
    baseline = eligible.iloc[-1]
    elapsed = (latest["observed_on"] - baseline["observed_on"]).days
    if elapsed <= 0:
        return None
    gained = int(latest["total_citations"] - baseline["total_citations"])
    return gained / elapsed, gained, elapsed


client = get_supabase()
if client is None:
    st.error(
        "The database is not connected yet. Follow the deployment steps in README.md "
        "to add SUPABASE_URL and SUPABASE_KEY to your Streamlit app secrets."
    )
    st.stop()

try:
    data = load_data(client)
except Exception as exc:
    st.error(f"Could not read citation history from Supabase: {exc}")
    st.stop()

if data.empty:
    st.info(
        "The dashboard is deployed, but no citation snapshots have been collected yet. "
        "After you configure the GitHub Actions secrets and run the daily workflow, "
        "your first observation will appear here."
    )
    st.stop()

latest = data.iloc[-1]
today = date.today()
year_start = date(today.year, 1, 1)
days_elapsed = (today - year_start).days + 1
year_citations = int(latest["year_citations"])

st.caption(f"Latest recorded snapshot: {latest['observed_on']}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total citations", f"{int(latest['total_citations']):,}")
c2.metric(f"{today.year} citations", f"{year_citations:,}")
c3.metric("Daily average · YTD", f"{year_citations / days_elapsed:.2f}")
last_90 = average_since(data, 90)
c4.metric(
    "Daily average · 90 days",
    f"{last_90[0]:.2f}" if last_90 else "Collecting data",
    help="Requires a stored observation at least 90 days before the latest snapshot.",
)

last_30 = average_since(data, 30)
st.subheader("Recent citation growth")
a, b = st.columns(2)
if last_30:
    a.metric("Daily average · 30 days", f"{last_30[0]:.2f}",
             f"{last_30[1]:+d} citations over {last_30[2]} days")
else:
    a.metric("Daily average · 30 days", "Collecting data")
    a.caption("This becomes available after the database contains at least 30 days of history.")
if last_90:
    b.metric("Citations gained · 90-day window", f"{last_90[1]:+,}",
             f"{last_90[2]} days between observations")
else:
    b.metric("Citations gained · 90-day window", "Collecting data")
    b.caption("This becomes available after the database contains at least 90 days of history.")

st.subheader("Citation history")
fig = px.line(
    data,
    x="observed_on",
    y="total_citations",
    markers=True,
    labels={"observed_on": "Date", "total_citations": "Total citations"},
)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Recorded observations")
display = data.rename(columns={
    "observed_on": "Date",
    "total_citations": "Total citations",
    "year_citations": f"{today.year} citations",
    "fetched_at": "Retrieved at",
})
st.dataframe(display, use_container_width=True, hide_index=True)

csv = data.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download history as CSV",
    data=csv,
    file_name="dario_grana_scholar_citation_history.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    "YTD uses Google Scholar's current-year citation histogram divided by elapsed "
    "calendar days. The 30- and 90-day averages use changes in stored total-citation "
    "snapshots. These rolling metrics become reliable only after enough daily history "
    "has accumulated. Google Scholar does not provide an official public API; automated "
    "retrieval can be rate-limited or blocked."
)
