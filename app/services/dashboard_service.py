from app.services.mongo_service import predictions_collection, analyses_collection


def get_total_predictions():
    return predictions_collection.count_documents({})


def get_total_analyses():
    return analyses_collection.count_documents({})


def get_average_confidence():
    pipeline = [
        {
            "$group": {
                "_id": None,
                "average_confidence": {"$avg": "$confidence"}
            }
        }
    ]

    result = list(predictions_collection.aggregate(pipeline))

    if not result:
        return 0

    return round(result[0]["average_confidence"], 2)


def get_most_common_incident():
    pipeline = [
        {
            "$group": {
                "_id": "$incident_type",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        },
        {
            "$limit": 1
        }
    ]

    result = list(predictions_collection.aggregate(pipeline))

    if not result:
        return "No data"

    return result[0]["_id"]


def get_recent_analyses(limit=10):
    analyses = analyses_collection.find().sort("created_at", -1).limit(limit)

    recent_analyses = []

    for analysis in analyses:
        analysis_id = analysis.get("analysis_id")

        incident_summary = list(predictions_collection.aggregate([
            {"$match": {"analysis_id": analysis_id}},
            {"$group": {"_id": "$incident_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))

        most_common = incident_summary[0]["_id"] if incident_summary else "No data"

        recent_analyses.append({
            "analysis_id": analysis_id,
            "source_type": analysis.get("source_type"),
            "file_name": analysis.get("file_name"),
            "created_at": analysis.get("created_at"),
            "total_logs": analysis.get("total_logs", 0),
            "status": analysis.get("status"),
            "most_common_incident": most_common
        })

    return recent_analyses


def get_recent_predictions(limit=10):
    predictions = predictions_collection.find().sort("timestamp", -1).limit(limit)

    recent_predictions = []

    for item in predictions:
        recent_predictions.append({
            "timestamp": item.get("timestamp"),
            "raw_log": item.get("raw_log"),
            "incident_type": item.get("incident_type"),
            "confidence": item.get("confidence"),
            "keywords": item.get("keywords", []),
            "analysis_id": item.get("analysis_id")
        })

    return recent_predictions