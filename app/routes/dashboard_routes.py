from flask import Blueprint, render_template
from app.services.dashboard_service import (
    get_total_predictions,
    get_total_analyses,
    get_average_confidence,
    get_most_common_incident,
    get_recent_analyses
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    total_predictions = get_total_predictions()
    total_analyses = get_total_analyses()
    average_confidence = get_average_confidence()
    most_common_incident = get_most_common_incident()
    recent_analyses = get_recent_analyses(limit=10)

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        total_analyses=total_analyses,
        average_confidence=average_confidence,
        most_common_incident=most_common_incident,
        recent_analyses=recent_analyses
    )