from pymongo import MongoClient
from datetime import datetime
from uuid import uuid4

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "ai_log_analyzer_db"

PREDICTIONS_COLLECTION = "log_predictions"
ANALYSES_COLLECTION = "analysis_sessions"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

predictions_collection = db[PREDICTIONS_COLLECTION]
analyses_collection = db[ANALYSES_COLLECTION]


def create_analysis_session(source_type="manual", file_name=None):
    analysis_id = f"ANL-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid4())[:8]}"

    document = {
        "analysis_id": analysis_id,
        "source_type": source_type,
        "file_name": file_name,
        "created_at": datetime.now(),
        "total_logs": 0,
        "status": "created"
    }

    analyses_collection.insert_one(document)
    return analysis_id


def update_analysis_session(analysis_id, total_logs, status="completed"):
    analyses_collection.update_one(
        {"analysis_id": analysis_id},
        {
            "$set": {
                "total_logs": total_logs,
                "status": status,
                "completed_at": datetime.now()
            }
        }
    )


def save_prediction(result, analysis_id=None):
    document = {
        "analysis_id": analysis_id,
        "timestamp": datetime.now(),
        "raw_log": result.get("original_log"),
        "clean_log": result.get("clean_log"),
        "incident_type": result.get("predicted_incident"),
        "confidence": result.get("confidence"),
        "keywords": result.get("keywords", [])
    }

    inserted = predictions_collection.insert_one(document)
    return str(inserted.inserted_id)


collection = predictions_collection