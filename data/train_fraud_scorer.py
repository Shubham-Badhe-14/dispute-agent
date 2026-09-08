import sqlite3
import pandas as pd
import json
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'transactions.db')
MODEL_PATH = os.path.join(BASE_DIR, 'src', 'tools', 'fraud_model.pkl')
EVAL_IDS_PATH = os.path.join(BASE_DIR, 'data', 'eval', 'labeled_cases_ids.json')

def train_and_save_model():
    print("Loading data from database...")
    conn = sqlite3.connect(DB_PATH)
    # Join with users to get account_age_days and user_country if needed, or just use basic transaction features.
    # We will use amount, mcc_code, card_present. (We'll one-hot encode mcc_code if possible or just treat it as simple).
    # Since MCC code has many categories, let's just use amount and card_present for a simple model.
    # To make it slightly better, we can include whether transaction_country == user_country.
    
    query = """
    SELECT 
        t.transaction_id, 
        t.amount, 
        t.card_present,
        (t.transaction_country = u.home_country) as country_match,
        t.is_fraudulent_ground_truth
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    WHERE t.is_fraudulent_ground_truth IS NOT NULL
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    if df.empty:
        print("No training data found.")
        return
        
    print(f"Loaded {len(df)} transactions.")
    
    # Simple feature engineering
    X = df[['amount', 'card_present', 'country_match']].fillna(0)
    y = df['is_fraudulent_ground_truth']
    
    # Split data to prevent data leakage in eval
    X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
        X, y, df['transaction_id'], test_size=0.2, random_state=42
    )
    
    # Save the held-out IDs for Step 10 Eval
    os.makedirs(os.path.dirname(EVAL_IDS_PATH), exist_ok=True)
    with open(EVAL_IDS_PATH, 'w') as f:
        json.dump(id_test.tolist(), f)
    print(f"Saved {len(id_test)} held-out transaction IDs to {EVAL_IDS_PATH}.")
    
    # Train model
    print("Training Logistic Regression model...")
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(class_weight='balanced', random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)
    score = pipeline.score(X_test, y_test)
    print(f"Model trained. Test Accuracy: {score:.2f}")
    
    # Save model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}.")

if __name__ == "__main__":
    train_and_save_model()
