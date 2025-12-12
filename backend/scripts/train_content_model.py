import pandas as pd
import joblib
import os
import logging
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "phishing_email.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "content_model.joblib")

def train_model():
    logger.info("Loading dataset...")
    if not os.path.exists(DATA_PATH):
        logger.error(f"Dataset not found at {DATA_PATH}")
        return

    try:
        # Load Data
        df = pd.read_csv(DATA_PATH)
        
        # Drop missing values
        df.dropna(subset=['text_combined', 'label'], inplace=True)
        
        # Ensure text is string
        df['text_combined'] = df['text_combined'].astype(str)
        
        # Split features and target
        X = df['text_combined']
        y = df['label']
        
        # Train/Test Split
        logger.info("Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create Pipeline
        # TF-IDF: Convert text to numbers
        # LogisticRegression: Robust linear classifier for text
        logger.info("Building pipeline (TF-IDF + LogisticRegression)...")
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
            ('clf', LogisticRegression(max_iter=1000, solver='lbfgs'))
        ])
        
        # Train
        logger.info("Training model (this may take a minute)...")
        pipeline.fit(X_train, y_train)
        
        # Evaluate
        logger.info("Evaluating model...")
        y_pred = pipeline.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        logger.info(f"Test Accuracy: {acc:.2%}")
        logger.info("\n" + classification_report(y_test, y_pred))
        
        # Save
        if not os.path.exists(MODEL_DIR):
            os.makedirs(MODEL_DIR)
            
        logger.info(f"Saving model to {MODEL_PATH}...")
        joblib.dump(pipeline, MODEL_PATH)
        logger.info("Done!")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")

if __name__ == "__main__":
    train_model()
