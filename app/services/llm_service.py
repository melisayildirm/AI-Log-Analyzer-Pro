import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_ai_summary(analysis, summary, predictions):
    if not GEMINI_API_KEY:
        return {
            "available": False,
            "text": "Gemini API key is not configured. Add GEMINI_API_KEY to your .env file."
        }

    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-2.5-flash")

    incident_distribution = summary.get("incident_distribution", {})
    average_confidence = summary.get("average_confidence", 0)
    top_keywords = summary.get("top_keywords", [])

    total_logs = analysis.get("total_logs", 0)

    sorted_incidents = sorted(
        incident_distribution.items(),
        key=lambda x: x[1],
        reverse=True
    )

    primary_incident = sorted_incidents[0][0] if sorted_incidents else "Unknown"
    primary_count = sorted_incidents[0][1] if sorted_incidents else 0
    primary_ratio = round((primary_count / total_logs) * 100, 2) if total_logs else 0

    sample_predictions = []

    for item in predictions[:15]:
        sample_predictions.append({
            "incident_type": item.get("incident_type"),
            "confidence": item.get("confidence"),
            "clean_log": item.get("clean_log"),
            "keywords": item.get("keywords", [])
        })

    prompt = f"""
You are an AI operations analyst for a log monitoring platform.

Your task:
Create a concise, professional operational report based ONLY on the structured data below.

STRICT RULES:
- Do NOT invent incident types.
- Do NOT mention any category that is not present in the provided incident distribution.
- Do NOT infer exact hardware components unless they appear in logs or keywords.
- Do NOT claim certainty about root causes.
- Use cautious language such as "may indicate", "suggests", "should be reviewed".
- If confidence is low or moderate, mention that results should be reviewed by an engineer.
- Keep the response practical and suitable for a technical dashboard.
- Do not use markdown tables.
- Do not use emojis.

Allowed incident types:
{list(incident_distribution.keys())}

Analysis metadata:
Analysis ID: {analysis.get("analysis_id")}
Source type: {analysis.get("source_type")}
File name: {analysis.get("file_name")}
Total logs: {total_logs}
Average confidence: {average_confidence}%

Incident distribution:
{incident_distribution}

Primary incident:
{primary_incident} ({primary_count} logs, {primary_ratio}%)

Top keywords:
{top_keywords}

Sample classified logs:
{sample_predictions}

Write the report exactly in this format:

Executive Summary:
2-3 sentences summarizing the analysis.

Primary Incident:
State the most common incident type, count, and percentage.

Confidence Assessment:
Evaluate the average model confidence. If it is below 70%, state that this is moderate and should be reviewed carefully.

Operational Interpretation:
Explain what the distribution may suggest without inventing new categories.

Risk Level:
Choose only one: Low, Medium, High, Critical.
Give one short reason.

Recommended Actions:
- Action 1
- Action 2
- Action 3
- Action 4

Review Notes:
Mention any uncertainty or limitations based on model confidence and synthetic/general log patterns.
"""

    try:
        response = model.generate_content(prompt)

        return {
            "available": True,
            "text": response.text
        }

    except Exception as e:
        return {
            "available": False,
            "text": f"AI summary could not be generated: {str(e)}"
        }