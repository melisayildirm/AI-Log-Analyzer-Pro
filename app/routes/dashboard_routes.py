from flask import Blueprint, render_template
from app.services.dashboard_service import (
    get_total_predictions,
    get_average_confidence,
    get_most_common_incident,
    get_recent_predictions
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    total_predictions = get_total_predictions()
    average_confidence = get_average_confidence()
    most_common_incident = get_most_common_incident()
    recent_predictions = get_recent_predictions(limit=10)

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        average_confidence=average_confidence,
        most_common_incident=most_common_incident,
        recent_predictions=recent_predictions
    )