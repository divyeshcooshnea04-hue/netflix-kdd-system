"""
Netflix KDD Dashboard — Streamlit client for the analysis service.

Reads from the analysis-service through the Nginx gateway on
http://nginx:80 (inside Docker) or http://localhost:8080 (from host).
"""
import os
import time
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# Inside Docker Compose the gateway is reachable at http://nginx
# From the host machine (running streamlit run manually) it's http://localhost:8080
GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:8080")

st.set_page_config(
    page_title="Netflix KDD Dashboard",
    page_icon="🎬",
    layout="wide",
)


@st.cache_data(ttl=30)
def fetch(path: str):
    """GET a JSON endpoint from the gateway with a 30s cache."""
    url = f"{GATEWAY}{path}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Request to {url} failed: {e}")
        return None


st.title("🎬 Netflix KDD Dashboard")
st.caption(f"Source: MongoDB Atlas · Gateway: `{GATEWAY}` · 8,807 titles")

if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()

st.divider()

# ─── Q1: Genres ─────────────────────────────────────────────────────────────
st.header("Q1 — Which genres have the most titles?")
genres = fetch("/analysis/genres")
if genres and genres.get("results"):
    df = pd.DataFrame(genres["results"])
    fig = px.bar(
        df.sort_values("count", ascending=True),
        x="count", y="genre", orientation="h",
        text="count", color="count", color_continuous_scale="reds",
        title="Top genres by title count",
    )
    fig.update_layout(showlegend=False, height=520, yaxis_title="", xaxis_title="Titles")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Note: a title may carry multiple genres, so the sum of counts exceeds 8,807."
    )

st.divider()

# ─── Q2: Ratings by type ────────────────────────────────────────────────────
st.header("Q2 — Maturity rating distribution by content type")
ratings = fetch("/analysis/ratings-by-type")
if ratings and ratings.get("results"):
    df = pd.DataFrame(ratings["results"])
    # Exclude malformed entries like "66 min"
    df = df[~df["rating"].str.contains("min", na=False)]
    top_ratings = df.groupby("rating")["count"].sum().nlargest(10).index
    df = df[df["rating"].isin(top_ratings)]
    fig = px.bar(
        df, x="rating", y="count", color="type", barmode="group",
        title="Maturity ratings (Movies vs TV Shows)",
    )
    fig.update_layout(height=500, xaxis_title="", yaxis_title="Titles")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ─── Q3: Top directors ──────────────────────────────────────────────────────
st.header("Q3 — Which directors appear most often?")
directors = fetch("/analysis/top-directors")
if directors and directors.get("results"):
    df = pd.DataFrame(directors["results"])
    fig = px.bar(
        df.sort_values("count", ascending=True),
        x="count", y="director", orientation="h",
        text="count", color="count", color_continuous_scale="blues",
        title="Top 15 directors by credited titles",
    )
    fig.update_layout(showlegend=False, height=520, yaxis_title="", xaxis_title="Titles")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("~30% of records have no director, so this ranking is biased toward well-documented titles.")

st.divider()

# ─── Q4: Release years ──────────────────────────────────────────────────────
st.header("Q4 — Distribution of release years")
years = fetch("/analysis/release-years")
if years and years.get("results"):
    df = pd.DataFrame(years["results"])
    df = df[df["year"] >= 1980]  # trim sparse early years
    fig = px.area(
        df, x="year", y="count",
        title="Titles released per year (1980 onwards)",
    )
    fig.update_layout(height=450, xaxis_title="Release year", yaxis_title="Titles")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Peak year: 2018 (1,147 titles). 2021 is partial — the dataset was collected mid-2021.")

st.divider()
st.caption(f"Last refreshed: {time.strftime('%Y-%m-%d %H:%M:%S')}")