"""
Loads data/netflix_titles.csv into MongoDB Atlas.

Uses the standard library csv reader (no pandas) to avoid
datetime/NaT serialization issues with pandas 3.x.

Usage (from project root, after: pip install pymongo python-dotenv):
    python scripts/import_data.py
"""
import os
import sys
import csv
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

load_dotenv()

DATE_FORMATS = ["%B %d, %Y", "%b %d, %Y"]  # "September 25, 2021" / "Sep 25, 2021"


def parse_date(value: str):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def parse_year(value: str):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def main():
    uri = os.getenv("MONGO_URI")
    if not uri:
        sys.exit("MONGO_URI missing from .env")
    db_name = os.getenv("DB_NAME", "assignment1")
    coll_name = os.getenv("COLLECTION", "records")

    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "netflix_titles.csv")
    print(f"Reading {csv_path}")

    records = []
    with open(csv_path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        # Normalise header names (strip, lowercase)
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
        for row in reader:
            clean = {
                "show_id":     row.get("show_id", "").strip(),
                "type":        row.get("type", "").strip(),
                "title":       row.get("title", "").strip(),
                "director":    row.get("director", "").strip(),
                "cast":        row.get("cast", "").strip(),
                "country":     row.get("country", "").strip(),
                "date_added":  parse_date(row.get("date_added", "")),
                "release_year": parse_year(row.get("release_year", "")),
                "rating":      row.get("rating", "").strip(),
                "duration":    row.get("duration", "").strip(),
                "listed_in":   row.get("listed_in", "").strip(),
                "description": row.get("description", "").strip(),
            }
            records.append(clean)

    print(f"{len(records)} records ready for insert")

    client = MongoClient(uri)
    coll = client[db_name][coll_name]

    coll.delete_many({})
    result = coll.insert_many(records)
    print(f"Inserted {len(result.inserted_ids)} documents into {db_name}.{coll_name}")

    coll.create_index([("release_year", ASCENDING)])
    coll.create_index([("type", ASCENDING)])
    coll.create_index([("director", ASCENDING)])
    print("Indexes created: release_year, type, director")


if __name__ == "__main__":
    main()