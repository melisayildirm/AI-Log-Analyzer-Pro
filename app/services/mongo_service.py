from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "ai_log_analyzer_db"
COLLECTION_NAME = "log_predictions"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


def save_prediction(result):
    document = {
        "timestamp": datetime.now(),
        "raw_log": result.get("original_log"),
        "clean_log": result.get("clean_log"),
        "incident_type": result.get("predicted_incident"),
        "confidence": result.get("confidence"),
        "keywords": result.get("keywords", [])
    }

    inserted = collection.insert_one(document)
    return str(inserted.inserted_id)