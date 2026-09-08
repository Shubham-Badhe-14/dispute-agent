import os
import joblib
import pandas as pd
from langchain_core.tools import tool

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, 'src', 'tools', 'fraud_model.pkl')

_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train_fraud_scorer.py first.")
        _model = joblib.load(MODEL_PATH)
    return _model

@tool
def score_fraud(amount: float, card_present: bool, transaction_country: str, home_country: str) -> float:
    """
    Score a transaction for fraud. 
    Requires amount, whether the card was present (True/False), and the transaction/home countries to check for geo-mismatch.
    Returns a probability score between 0.0 and 1.0.
    """
    model = get_model()
    country_match = int(transaction_country == home_country)
    
    # Model features: ['amount', 'card_present', 'country_match']
    df = pd.DataFrame([{
        'amount': float(amount) if amount is not None else 0.0,
        'card_present': int(card_present) if card_present is not None else 0,
        'country_match': country_match
    }])
    
    # Predict probability of class 1 (fraud)
    proba = model.predict_proba(df)[0][1]
    return float(proba)
