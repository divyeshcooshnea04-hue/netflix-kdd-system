import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient

# ─── Config ────────────────────────────────────────────────────────────────
MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = "assignment1"
COLLECTION = "records"

st.set_page_config(
    page_title="Netflix KDD Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS for cleaner look ───────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 2rem; color: #E50914; }
    div[data-testid="stMetricLabel"] { font-size: 0.9rem; color: #999; }
    h1 { color: #E50914; }
    h2 { border-bottom: 1px solid #333; padding-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)


# ─── Data layer ────────────────────────────────────────────────────────────
@st.cache_resource
def get_collection():
    return MongoClient(MONGO_URI)[DB_NAME][COLLECTION]


@st.cache_data(ttl=300)
def load_data():
    """Pull everything we need from Atlas once, cache for 5 min."""
    coll = get_collection()
    rows = list(coll.find(
        {},
        {"_id": 0, "type": 1, "release_year": 1, "rating": 1,
         "listed_in": 1, "director": 1, "country": 1, "duration": 1},
    ))
    return pd.DataFrame(rows)


# ─── Header ────────────────────────────────────────────────────────────────
st.title("Netflix KDD Dashboard")
st.caption("Source: MongoDB Atlas · `assignment1.records` · updated on demand")

df = load_data()

# ─── KPI Row ───────────────────────────────────────────────────────────────
total = len(df)
movies = (df["type"] == "Movie").sum()
tv = (df["type"] == "TV Show").sum()
peak_year = df["release_year"].mode().iloc[0]
latest_year = int(df["release_year"].max())

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Titles", f"{total:,}")
col2.metric("Movies", f"{movies:,}", f"{movies/total:.0%}")
col3.metric("TV Shows", f"{tv:,}", f"{tv/total:.0%}")
col4.metric("Peak Release Year", int(peak_year))
col5.metric("Latest Release", latest_year)

st.divider()

# ─── Sidebar filters ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    content_type = st.multiselect(
        "Content type",
        options=sorted(df["type"].dropna().unique().tolist()),
        default=sorted(df["type"].dropna().unique().tolist()),
    )
    year_min, year_max = int(df["release_year"].min()), int(df["release_year"].max())
    year_range = st.slider("Release year range", year_min, year_max, (1980, year_max))

# Apply filters
fdf = df[
    df["type"].isin(content_type)
    & df["release_year"].between(year_range[0], year_range[1])
]

st.caption(f"Showing **{len(fdf):,}** of **{total:,}** titles after filters")

# ─── Q1 — Genres ──────────────────────────────────────────────────────────
st.header("Q1 — Which genres have the most titles?")

if not fdf.empty:
    exploded = fdf.assign(
        genre=fdf["listed_in"].fillna("").str.split(", ")
    ).explode("genre")
    exploded = exploded[exploded["genre"] != ""]

    genre_counts = exploded["genre"].value_counts().head(15).reset_index()
    genre_counts.columns = ["genre", "count"]

    fig = px.bar(
        genre_counts.sort_values("count"),
        x="count", y="genre", orientation="h",
        text="count",
        color="count",
        color_continuous_scale=["#2a0a0a", "#E50914"],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=550, showlegend=False,
        yaxis_title="", xaxis_title="Titles",
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "A single title may carry multiple genres, so total genre counts exceed the number of titles."
    )

st.divider()

# ─── Q2 — Ratings by Type ─────────────────────────────────────────────────
st.header("Q2 — Maturity ratings by content type")

left, right = st.columns([2, 1])

with left:
    if not fdf.empty:
        rat = fdf[fdf["rating"].str.contains("min", na=False) == False]
        top_ratings = rat["rating"].value_counts().head(8).index
        rat = rat[rat["rating"].isin(top_ratings)]

        grouped = rat.groupby(["rating", "type"]).size().reset_index(name="count")
        fig = px.bar(
            grouped, x="rating", y="count", color="type", barmode="group",
            color_discrete_map={"Movie": "#E50914", "TV Show": "#F5B301"},
        )
        fig.update_layout(
            height=450, xaxis_title="", yaxis_title="Titles",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

with right:
    type_counts = fdf["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    fig = px.pie(
        type_counts, names="type", values="count", hole=0.6,
        color="type",
        color_discrete_map={"Movie": "#E50914", "TV Show": "#F5B301"},
    )
    fig.update_layout(
        height=450, showlegend=True,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ─── Q3 — Top Directors ───────────────────────────────────────────────────
st.header("Q3 — Which directors appear most often?")

if not fdf.empty:
    dirs = fdf[fdf["director"].notna() & (fdf["director"] != "")]
    dir_counts = dirs["director"].value_counts().head(15).reset_index()
    dir_counts.columns = ["director", "count"]

    fig = px.bar(
        dir_counts.sort_values("count"),
        x="count", y="director", orientation="h",
        text="count",
        color="count",
        color_continuous_scale=["#0a1a2a", "#4A9EFF"],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=550, showlegend=False,
        yaxis_title="", xaxis_title="Titles",
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "~30% of records have no director field, so this ranking favours well-documented titles."
    )

st.divider()

# ─── Q4 — Release Years ───────────────────────────────────────────────────
st.header("Q4 — Distribution of release years")

if not fdf.empty:
    years = fdf.groupby("release_year").size().reset_index(name="count")
    years = years[years["release_year"] >= 1980]

    fig = px.area(
        years, x="release_year", y="count",
        color_discrete_sequence=["#E50914"],
    )
    fig.update_traces(fill="tozeroy", line=dict(width=2))
    fig.update_layout(
        height=450, xaxis_title="Release year", yaxis_title="Titles",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Content volume peaked around 2018. Values after 2020 trail off because the dataset was collected in 2021."
    )

st.divider()
st.caption("Netflix KDD System · FastAPI + MongoDB Atlas + Streamlit · Assignment 1")