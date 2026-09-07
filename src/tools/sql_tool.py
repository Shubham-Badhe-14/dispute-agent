import sqlite3
import os
from typing import Dict, Any
from langchain_core.tools import tool

# Determine the absolute path to the database to ensure it works regardless of cwd
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    'data', 
    'transactions.db'
)

@tool
def get_transaction_details(transaction_id: str) -> Dict[str, Any]:
    """
    Fetch full transaction details and associated user data from the database 
    given a transaction_id.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()
    
    # Explicitly naming columns avoids shape-shifting downstream if schema changes
    query = '''
        SELECT 
            t.transaction_id,
            t.user_id,
            t.amount,
            t.currency,
            t.merchant_name,
            t.merchant_category,
            t.mcc_code,
            t.transaction_country,
            t.card_present,
            t.timestamp,
            t.status,
            t.dispute_reason,
            t.is_fraudulent_ground_truth,
            u.home_country,
            u.account_age_days
        FROM transactions t
        JOIN users u ON t.user_id = u.user_id
        WHERE t.transaction_id = ?
    '''
    
    cursor.execute(query, (transaction_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError(f"Transaction not found for ID: {transaction_id}")
        
    return dict(row)
