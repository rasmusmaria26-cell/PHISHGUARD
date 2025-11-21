import os
import joblib

# path to: backend/models/content_model.joblib
ROOT = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(ROOT, "models", "content_model.joblib")

class ContentModel:
    def __init__(self, path: str = MODEL_PATH):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model not found at {path}")
        data = joblib.load(path)
        self.vectorizer = data["tfidf"]
        self.model = data["clf"]

    def score(self, text: str):
        """Return (score 0–100, note) based on ML probability."""
        if not text or len(text.strip()) < 10:
            return 0, "text too short for ML analysis"
        X = self.vectorizer.transform([text])
        prob = float(self.model.predict_proba(X)[0, 1])
        score = int(prob * 100)
        note = f"ML probability={prob:.3f}"
        return score, note
