from fastapi import FastAPI
from .pipelines import (
    genres_pipeline,
    ratings_by_type_pipeline,
    top_directors_pipeline,
    release_years_pipeline,
)

app = FastAPI(
    title="Netflix KDD — Analysis Service",
    description="Aggregation pipelines answering the assignment's KDD questions.",
    version="1.0.0",
)

@app.get("/analysis/genres")
def genres(limit: int = 15):
    return {"question": "Which genres have the most titles?",
            "results": genres_pipeline(limit)}

@app.get("/analysis/ratings-by-type")
def ratings_by_type():
    return {"question": "Maturity rating distribution per content type",
            "results": ratings_by_type_pipeline()}

@app.get("/analysis/top-directors")
def top_directors(limit: int = 15):
    return {"question": "Which directors appear most often?",
            "results": top_directors_pipeline(limit)}

@app.get("/analysis/release-years")
def release_years():
    return {"question": "Distribution of release years",
            "results": release_years_pipeline()}

@app.get("/health")
def health():
    return {"status": "ok", "service": "analysis-service"}
