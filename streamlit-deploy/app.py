import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = "assignment1"
COLLECTION = "records"

@st.cache_resource
def get_collection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME][COLLECTION]

st.set_page_config(page_title="Netflix KDD Dashboard", page_icon="??", layout="wide")
st.title("?? Netflix KDD Dashboard")
st.caption("Source: MongoDB Atlas ? 8,807 titles")

coll = get_collection()

# --- Q1: Genres ---
st.header("Q1 ? Which genres have the most titles?")
genres_data = list(coll.aggregate([
    {"$match": {"listed_in": {"$exists": True, "$ne": ""}}},
    {"$project": {"genres": {"$split": ["$listed_in", ", "]}}},
    {"$unwind": "$genres"},
    {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 15},
    {"$project": {"_id": 0, "genre": "$_id", "count": 1}},
]))
if genres_data:
    df = pd.DataFrame(genres_data)
    fig = px.bar(df.sort_values("count", ascending=True), x="count", y="genre",
                 orientation="h", text="count", color="count", color_continuous_scale="reds")
    fig.update_layout(showlegend=False, height=500, yaxis_title="", xaxis_title="Titles")
    st.plotly_chart(fig, use_container_width=True)

# --- Q2: Ratings by Type ---
st.header("Q2 ? Maturity rating distribution by content type")
ratings_data = list(coll.aggregate([
    {"$match": {"rating": {"$exists": True, "$ne": ""}}},
    {"$group": {"_id": {"rating": "$rating", "type": "$type"}, "count": {"$sum": 1}}},
    {"$sort": {"_id.rating": 1, "_id.type": 1}},
    {"$project": {"_id": 0, "rating": "$_id.rating", "type": "$_id.type", "count": 1}},
]))
if ratings_data:
    df = pd.DataFrame(ratings_data)
    df = df[~df["rating"].str.contains("min", na=False)]
    top_ratings = df.groupby("rating")["count"].sum().nlargest(10).index
    df = df[df["rating"].isin(top_ratings)]
    fig = px.bar(df, x="rating", y="count", color="type", barmode="group",
                 title="Maturity ratings (Movies vs TV Shows)")
    fig.update_layout(height=500, xaxis_title="", yaxis_title="Titles")
    st.plotly_chart(fig, use_container_width=True)

# --- Q3: Top Directors ---
st.header("Q3 ? Which directors appear most often?")
directors_data = list(coll.aggregate([
    {"$match": {"director": {"$exists": True, "$nin": ["", None]}}},
    {"$group": {"_id": "$director", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 15},
    {"$project": {"_id": 0, "director": "$_id", "count": 1}},
]))
if directors_data:
    df = pd.DataFrame(directors_data)
    fig = px.bar(df.sort_values("count", ascending=True), x="count", y="director",
                 orientation="h", text="count", color="count", color_continuous_scale="blues")
    fig.update_layout(showlegend=False, height=500, yaxis_title="", xaxis_title="Titles")
    st.plotly_chart(fig, use_container_width=True)

# --- Q4: Release Years ---
st.header("Q4 ? Distribution of release years")
years_data = list(coll.aggregate([
    {"$match": {"release_year": {"$type": "number"}}},
    {"$group": {"_id": "$release_year", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}},
    {"$project": {"_id": 0, "year": "$_id", "count": 1}},
]))
if years_data:
    df = pd.DataFrame(years_data)
    df = df[df["year"] >= 1980]
    fig = px.area(df, x="year", y="count", title="Titles released per year (1980 onwards)")
    fig.update_layout(height=450, xaxis_title="Release year", yaxis_title="Titles")
    st.plotly_chart(fig, use_container_width=True)
