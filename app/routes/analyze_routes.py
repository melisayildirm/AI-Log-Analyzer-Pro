from flask import Blueprint, render_template, request
from app.services.prediction_service import predict_log, get_top_keywords

analyze_bp = Blueprint("analyze", __name__)

@analyze_bp.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None

    if request.method == "POST":
        log_text = request.form.get("log_text")

        if log_text:
            result = predict_log(log_text)
            result["keywords"] = get_top_keywords(log_text)

    return render_template("analyze.html", result=result)