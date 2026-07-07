import re
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ai" / "trained_models" / "logistic_regression_model.pkl"
VECTORIZER_PATH = BASE_DIR / "ai" / "trained_models" / "tfidf_vectorizer.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def clean_log(text):
    text = str(text).lower()

    text = re.sub(r'\([^)]*\)', ' ', text)
    text = re.sub(r'0x[a-fA-F0-9]+', ' ', text)
    text = re.sub(r'[/\\][^\s]+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\b[a-zA-Z]\b', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def predict_log(log_text):
    clean_text = clean_log(log_text)
    vector = vectorizer.transform([clean_text])

    prediction = model.predict(vector)[0]
    probabilities = model.predict_proba(vector)[0]

    confidence = float(round(probabilities.max() * 100, 2))

    return {
        "original_log": log_text,
        "clean_log": clean_text,
        "predicted_incident": prediction,
        "confidence": confidence
    }


def get_top_keywords(log_text, top_n=5):
    clean_text = clean_log(log_text)
    vector = vectorizer.transform([clean_text])

    prediction = model.predict(vector)[0]
    class_index = list(model.classes_).index(prediction)

    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = vector.toarray()[0]
    class_weights = model.coef_[class_index]

    contribution_scores = tfidf_scores * class_weights
    top_indices = contribution_scores.argsort()[-top_n:][::-1]

    keywords = [
        feature_names[i]
        for i in top_indices
        if contribution_scores[i] > 0
    ]

    return keywords