from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, VIOLATIONS_COLLECTION

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
violations_col = db[VIOLATIONS_COLLECTION]

def store_violation(plate, speed_kmph, timestamp, track_id):
    violation = {
        "plate": plate,
        "speed_kmph": speed_kmph,
        "timestamp": timestamp,
        "track_id": track_id,
        "paid": False
    }
    violations_col.insert_one(violation)

def mark_violation_paid(plate):
    result = violations_col.update_many({"plate": plate, "paid": False}, {"$set": {"paid": True}})
    return result.modified_count

def list_violations():
    return list(violations_col.find({"paid": False}, {"_id":0}))

