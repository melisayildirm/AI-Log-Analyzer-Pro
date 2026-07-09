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
from collections import Counter


def get_analysis_by_id(analysis_id):
    return analyses_collection.find_one({"analysis_id": analysis_id})


def get_predictions_by_analysis_id(analysis_id):
    predictions = predictions_collection.find({"analysis_id": analysis_id}).sort("timestamp", 1)

    result = []

    for item in predictions:
        result.append({
            "timestamp": item.get("timestamp"),
            "raw_log": item.get("raw_log"),
            "clean_log": item.get("clean_log"),
            "incident_type": item.get("incident_type"),
            "confidence": item.get("confidence"),
            "keywords": item.get("keywords", [])
        })

    return result


def get_analysis_summary(analysis_id):
    predictions = get_predictions_by_analysis_id(analysis_id)

    if not predictions:
        return {
            "incident_distribution": {},
            "average_confidence": 0,
            "top_keywords": [],
            "recommendations": []
        }

    incident_distribution = Counter(
        item["incident_type"] for item in predictions
    )

    confidences = [
        item["confidence"] for item in predictions
        if item.get("confidence") is not None
    ]

    average_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0

    all_keywords = []
    for item in predictions:
        all_keywords.extend(item.get("keywords", []))

    top_keywords = Counter(all_keywords).most_common(10)

    recommendations = generate_recommendations(incident_distribution)

    return {
        "incident_distribution": dict(incident_distribution),
        "average_confidence": average_confidence,
        "top_keywords": top_keywords,
        "recommendations": recommendations
    }


def generate_recommendations(incident_distribution):
    recommendations = []

    if not incident_distribution:
        return ["No incidents detected in this analysis."]

    most_common_incident = max(incident_distribution, key=incident_distribution.get)

    if most_common_incident == "Storage/File System":
        recommendations.append("Storage/File System incidents dominate this analysis. Check disk health, filesystem integrity, and storage controller logs.")
    elif most_common_incident == "Network/Communication":
        recommendations.append("Network-related incidents are frequent. Inspect node connectivity, packet loss, and switch/router status.")
    elif most_common_incident == "Memory Error":
        recommendations.append("Memory-related incidents are frequent. Inspect memory modules, cache parity events, and affected nodes.")
    elif most_common_incident == "Power/Thermal Issue":
        recommendations.append("Power or thermal issues detected. Check cooling, fan status, power supply, and temperature thresholds.")
    elif most_common_incident == "Application Failure":
        recommendations.append("Application failures detected. Review application runtime logs, crashes, and segmentation fault traces.")
    else:
        recommendations.append("Multiple or unclear incident patterns detected. Review detailed logs and keyword distribution.")

    return recommendations
from datetime import datetime, timedelta


def get_incident_distribution():
    pipeline = [
        {"$group": {"_id": "$incident_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    result = list(predictions_collection.aggregate(pipeline))

    return {
        item["_id"] or "Unknown": item["count"]
        for item in result
    }


def get_confidence_distribution():
    buckets = {
        "0-50": 0,
        "50-70": 0,
        "70-80": 0,
        "80-90": 0,
        "90-100": 0
    }

    predictions = predictions_collection.find({}, {"confidence": 1})

    for item in predictions:
        confidence = item.get("confidence", 0)

        if confidence < 50:
            buckets["0-50"] += 1
        elif confidence < 70:
            buckets["50-70"] += 1
        elif confidence < 80:
            buckets["70-80"] += 1
        elif confidence < 90:
            buckets["80-90"] += 1
        else:
            buckets["90-100"] += 1

    return buckets


def get_analyses_by_day(days=7):
    today = datetime.now().date()
    start_date = today - timedelta(days=days - 1)

    day_counts = {
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d"): 0
        for i in range(days)
    }

    analyses = analyses_collection.find({
        "created_at": {
            "$gte": datetime.combine(start_date, datetime.min.time())
        }
    })

    for analysis in analyses:
        created_at = analysis.get("created_at")
        if created_at:
            day_key = created_at.date().strftime("%Y-%m-%d")
            if day_key in day_counts:
                day_counts[day_key] += 1

    return day_counts