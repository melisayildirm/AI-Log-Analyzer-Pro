import re
import joblib
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ai" / "trained_models" / "linear_svc_model.pkl"
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


def _svc_confidence(vector):
    scores = model.decision_function(vector)

    if scores.ndim == 1:
        scores = np.array([scores])

    exp_scores = np.exp(scores - np.max(scores, axis=1, keepdims=True))
    pseudo_probs = exp_scores / exp_scores.sum(axis=1, keepdims=True)

    return float(round(pseudo_probs.max() * 100, 2))


def predict_log(log_text):
    clean_text = clean_log(log_text)
    vector = vectorizer.transform([clean_text])

    prediction = model.predict(vector)[0]
    confidence = _svc_confidence(vector)

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

    return [
        feature_names[i]
        for i in top_indices
        if contribution_scores[i] > 0
    ]