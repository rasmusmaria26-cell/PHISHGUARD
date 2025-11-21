import pandas as pd
import joblib
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Point to your specific Kaggle file
KAGGLE_PATH = os.path.join(BASE_DIR, "../data/phishing_email.csv") 
SYNTHETIC_PATH = os.path.join(BASE_DIR, "../data/content_labeled.csv")
MODEL_PATH = os.path.join(BASE_DIR, "../models/content_model.joblib")

def load_and_merge_data():
    print("1. Loading Datasets...")
    
    # --- 1. Load Synthetic Data (The 'Base' logic) ---
    try:
        df_syn = pd.read_csv(SYNTHETIC_PATH)
        print(f"   [Synthetic] Loaded {len(df_syn)} rows.")
    except FileNotFoundError:
        print("   [Info] Synthetic data not found (that is okay).")
        df_syn = pd.DataFrame()

    # --- 2. Load Kaggle Data (The 'Real' logic) ---
    df_kaggle = pd.DataFrame()
    if os.path.exists(KAGGLE_PATH):
        try:
            print(f"   [Kaggle] Reading {KAGGLE_PATH}...")
            df_raw = pd.read_csv(KAGGLE_PATH)
            
            # This specific dataset usually has columns "text" and "label" 
            # OR "email_text" and "phishing_status"
            # We normalize them here:
            
            # Lowercase all columns to be safe
            df_raw.columns = [c.lower().strip() for c in df_raw.columns]
            
            # Auto-map known column names for this specific dataset
            # If the file has 'text' and 'label_phishing', rename them:
            if 'text_combined' in df_raw.columns: df_raw = df_raw.rename(columns={'text_combined': 'text'})
            if 'label' in df_raw.columns: pass # good
            
            # Check if we have what we need
            if 'text' in df_raw.columns and 'label' in df_raw.columns:
                # This dataset usually uses 1 for Phishing, 0 for Safe.
                # If it uses strings like "phishing"/"safe", map them:
                if df_raw['label'].dtype == 'O': 
                    df_raw['label'] = df_raw['label'].map({'phishing': 1, 'safe': 0, '1': 1, '0': 0})
                
                # Keep only valid rows
                df_kaggle = df_raw[['text', 'label']].dropna()
                
                # If dataset is HUGE, take a random sample of 5000 rows to speed up training
                if len(df_kaggle) > 10000:
                    print(f"   [Kaggle] Dataset is large ({len(df_kaggle)} rows). Sampling top 10,000 for speed.")
                    df_kaggle = df_kaggle.sample(n=10000, random_state=42)
                
                print(f"   [Kaggle] Loaded {len(df_kaggle)} valid rows.")
            else:
                print(f"   [Error] Columns not found. Found: {list(df_raw.columns)}")
                
        except Exception as e:
            print(f"   [Warning] Could not load Kaggle data: {e}")
    else:
        print(f"   [Info] File not found at {KAGGLE_PATH}")

    # --- 3. Merge ---
    if not df_kaggle.empty:
        df_final = pd.concat([df_syn, df_kaggle], ignore_index=True)
    else:
        df_final = df_syn

    # Shuffle
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"   [Total] Training on {len(df_final)} rows.")
    return df_final

def train():
    # 1. Get Data
    df = load_and_merge_data()
    if df is None or df.empty: 
        print("No data found!")
        return

    # Ensure string format
    X = df['text'].astype(str)
    y = df['label'].astype(int)

    # 2. Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Train
    print("2. Training Model...")
    # Use Unigrams + Bigrams (e.g., "verify" + "verify account")
    model = make_pipeline(
        TfidfVectorizer(stop_words='english', max_features=20000, ngram_range=(1, 2)),
        LogisticRegression(max_iter=1000)
    )

    model.fit(X_train, y_train)

    # 4. Evaluate
    print("3. Evaluation Results:")
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))
    
    # 5. Save
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\n[Success] New Brain saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()