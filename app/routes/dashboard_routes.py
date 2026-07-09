from flask import Blueprint, render_template, abort, Response, jsonify
import csv
import io
from datetime import datetime

from app.services.dashboard_service import (
    get_total_predictions,
    get_total_analyses,
    get_average_confidence,
    get_most_common_incident,
    get_recent_analyses,
    get_analysis_by_id,
    get_predictions_by_analysis_id,
    get_analysis_summary,
    get_incident_distribution,
    get_confidence_distribution,
    get_analyses_by_day
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    total_predictions = get_total_predictions()
    total_analyses = get_total_analyses()
    average_confidence = get_average_confidence()
    most_common_incident = get_most_common_incident()
    recent_analyses = get_recent_analyses(limit=10)
    incident_distribution = get_incident_distribution()
    confidence_distribution = get_confidence_distribution()
    analyses_by_day = get_analyses_by_day()

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        total_analyses=total_analyses,
        average_confidence=average_confidence,
        most_common_incident=most_common_incident,
        recent_analyses=recent_analyses,
        incident_distribution=incident_distribution,
        confidence_distribution=confidence_distribution,
        analyses_by_day=analyses_by_day
    )


@dashboard_bp.route("/analysis/<analysis_id>/export/csv")
def export_analysis_csv(analysis_id):
    analysis = get_analysis_by_id(analysis_id)

    if analysis is None:
        abort(404)

    predictions = get_predictions_by_analysis_id(analysis_id)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Analysis ID",
        "Timestamp",
        "Incident Type",
        "Confidence",
        "Clean Log",
        "Raw Log",
        "Keywords"
    ])

    for item in predictions:
        writer.writerow([
            analysis_id,
            item.get("timestamp"),
            item.get("incident_type"),
            item.get("confidence"),
            item.get("clean_log"),
            item.get("raw_log"),
            ", ".join(item.get("keywords", []))
        ])

    filename = f"{analysis_id}_report.csv"

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@dashboard_bp.route("/analysis/<analysis_id>/export/json")
def export_analysis_json(analysis_id):
    analysis = get_analysis_by_id(analysis_id)

    if analysis is None:
        abort(404)

    predictions = get_predictions_by_analysis_id(analysis_id)
    summary = get_analysis_summary(analysis_id)

    cleaned_predictions = []

    for item in predictions:
        cleaned_predictions.append({
            "timestamp": str(item.get("timestamp")),
            "raw_log": item.get("raw_log"),
            "clean_log": item.get("clean_log"),
            "incident_type": item.get("incident_type"),
            "confidence": item.get("confidence"),
            "keywords": item.get("keywords", [])
        })

    data = {
        "analysis": {
            "analysis_id": analysis.get("analysis_id"),
            "source_type": analysis.get("source_type"),
            "file_name": analysis.get("file_name"),
            "created_at": str(analysis.get("created_at")),
            "completed_at": str(analysis.get("completed_at")),
            "total_logs": analysis.get("total_logs"),
            "status": analysis.get("status")
        },
        "summary": summary,
        "predictions": cleaned_predictions,
        "exported_at": datetime.now().isoformat()
    }

    filename = f"{analysis_id}_report.json"

    response = jsonify(data)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"

    return response


@dashboard_bp.route("/analysis/<analysis_id>")
def analysis_detail(analysis_id):
    analysis = get_analysis_by_id(analysis_id)

    if analysis is None:
        abort(404)

    predictions = get_predictions_by_analysis_id(analysis_id)
    summary = get_analysis_summary(analysis_id)

    return render_template(
        "analysis_detail.html",
        analysis=analysis,
        predictions=predictions,
        summary=summary
    )