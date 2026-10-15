from .db import get_collection

def genres_pipeline(limit: int = 15):
    """Q1: Which genres have the most titles?"""
    coll = get_collection()
    return list(coll.aggregate([
        {"$match": {"listed_in": {"$exists": True, "$ne": ""}}},
        {"$project": {"genres": {"$split": ["$listed_in", ", "]}}},
        {"$unwind": "$genres"},
        {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "genre": "$_id", "count": 1}},
    ]))

def ratings_by_type_pipeline():
    """Q2: Distribution of maturity ratings, split by Movies vs TV Shows."""
    coll = get_collection()
    return list(coll.aggregate([
        {"$match": {"rating": {"$exists": True, "$ne": ""}}},
        {"$group": {"_id": {"rating": "$rating", "type": "$type"},
                    "count": {"$sum": 1}}},
        {"$sort": {"_id.rating": 1, "_id.type": 1}},
        {"$project": {"_id": 0,
                      "rating": "$_id.rating",
                      "type": "$_id.type",
                      "count": 1}},
    ]))

def top_directors_pipeline(limit: int = 15):
    """Q3: Which directors appear most often? (excluding nulls/empty)"""
    coll = get_collection()
    return list(coll.aggregate([
        {"$match": {"director": {"$exists": True, "$nin": ["", None]}}},
        {"$group": {"_id": "$director", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "director": "$_id", "count": 1}},
    ]))

def release_years_pipeline():
    """Q4: Distribution of release years."""
    coll = get_collection()
    return list(coll.aggregate([
        {"$match": {"release_year": {"$type": "number"}}},
        {"$group": {"_id": "$release_year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "year": "$_id", "count": 1}},
    ]))
