from flask import Blueprint, render_template, request
from app.services.prediction_service import predict_log, get_top_keywords
from app.services.mongo_service import (
    save_prediction,
    create_analysis_session,
    update_analysis_session
)

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None
    batch_results = []
    analysis_id = None

    if request.method == "POST":
        log_text = request.form.get("log_text")
        log_file = request.files.get("log_file")

        if log_file and log_file.filename:
            analysis_id = create_analysis_session(
                source_type="file_upload",
                file_name=log_file.filename
            )

            file_content = log_file.read().decode("utf-8", errors="ignore")
            log_lines = [line.strip() for line in file_content.splitlines() if line.strip()]

            for line in log_lines:
                prediction = predict_log(line)
                prediction["keywords"] = get_top_keywords(line)

                saved_id = save_prediction(prediction, analysis_id=analysis_id)
                prediction["saved_id"] = saved_id
                prediction["analysis_id"] = analysis_id

                batch_results.append(prediction)

            update_analysis_session(
                analysis_id=analysis_id,
                total_logs=len(batch_results),
                status="completed"
            )

        elif log_text:
            analysis_id = create_analysis_session(
                source_type="manual",
                file_name=None
            )

            result = predict_log(log_text)
            result["keywords"] = get_top_keywords(log_text)

            saved_id = save_prediction(result, analysis_id=analysis_id)
            result["saved_id"] = saved_id
            result["analysis_id"] = analysis_id

            update_analysis_session(
                analysis_id=analysis_id,
                total_logs=1,
                status="completed"
            )

    return render_template(
        "analyze.html",
        result=result,
        batch_results=batch_results,
        analysis_id=analysis_id
    )