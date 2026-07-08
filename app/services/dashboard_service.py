from app.services.mongo_service import collection


def get_total_predictions():
    return collection.count_documents({})


def get_average_confidence():
    pipeline = [
        {
            "$group": {
                "_id": None,
                "average_confidence": {"$avg": "$confidence"}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

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

    result = list(collection.aggregate(pipeline))

    if not result:
        return "No data"

    return result[0]["_id"]


def get_recent_predictions(limit=10):
    predictions = collection.find().sort("timestamp", -1).limit(limit)

    recent_predictions = []

    for item in predictions:
        recent_predictions.append({
            "timestamp": item.get("timestamp"),
            "raw_log": item.get("raw_log"),
            "incident_type": item.get("incident_type"),
            "confidence": item.get("confidence"),
            "keywords": item.get("keywords", [])
        })

    return recent_predictions