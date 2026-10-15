from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from typing import Optional

from .db import get_collection

router = APIRouter()

def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("/titles")
def list_titles(
    limit: int = Query(20, ge=1, le=200),
    skip: int = Query(0, ge=0),
    type: Optional[str] = None,
):
    coll = get_collection()
    filt = {}
    if type:
        filt["type"] = type
    cursor = coll.find(filt).skip(skip).limit(limit)
    return {
        "count": coll.count_documents(filt),
        "limit": limit,
        "skip": skip,
        "items": [_serialize(d) for d in cursor],
    }

@router.get("/titles/search")
def search_titles(q: str = Query(..., min_length=1), limit: int = 20):
    coll = get_collection()
    regex = {"$regex": q, "$options": "i"}
    filt = {"$or": [{"title": regex}, {"director": regex}, {"cast": regex}]}
    cursor = coll.find(filt).limit(limit)
    return {"query": q, "items": [_serialize(d) for d in cursor]}

@router.get("/titles/{title_id}")
def get_title(title_id: str):
    coll = get_collection()
    try:
        oid = ObjectId(title_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")
    doc = coll.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return _serialize(doc)

@router.delete("/titles/{title_id}")
def delete_title(title_id: str):
    coll = get_collection()
    try:
        oid = ObjectId(title_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")
    result = coll.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True, "id": title_id}
