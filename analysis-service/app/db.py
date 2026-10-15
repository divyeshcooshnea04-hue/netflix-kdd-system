import os
from pymongo import MongoClient
from pymongo.collection import Collection

_client: MongoClient | None = None

def get_collection() -> Collection:
    global _client
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI is not set (check .env)")
    if _client is None:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db_name = os.getenv("DB_NAME", "assignment1")
    coll_name = os.getenv("COLLECTION", "records")
    return _client[db_name][coll_name]
