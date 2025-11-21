# backend/app/train_content_model.py
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
import joblib

ROOT = os.path.dirname(os.path.dirname(__file__))  # backend/app -> backend
DATA_CSV = os.path.join(ROOT, "data", "content_labeled.csv")
OUT_PATH = os.path.join(ROOT, "models", "content_model.joblib")

def load_data(path=DATA_CSV):
    df = pd.read_csv(path)
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(int)
    return df

def train_and_save():
    df = load_data()
    X = df["text"]
    y = df["label"]
    Xtrain, Xval, ytrain, yval = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    vec = TfidfVectorizer(max_features=20000, ngram_range=(1,2), stop_words='english')
    Xt = vec.fit_transform(Xtrain)
    clf = LogisticRegression(max_iter=1000, class_weight='balanced')
    clf.fit(Xt, ytrain)

    # evaluate
    Xval_t = vec.transform(Xval)
    preds = clf.predict(Xval_t)
    probs = clf.predict_proba(Xval_t)[:,1]
    print("Accuracy:", accuracy_score(yval, preds))
    print("ROC AUC:", roc_auc_score(yval, probs))
    print(classification_report(yval, preds, digits=4))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    joblib.dump({"tfidf": vec, "clf": clf}, OUT_PATH)
    print("Saved model to", OUT_PATH)

if __name__ == "__main__":
    train_and_save()
