import sqlite3
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'transactions.db')

# Standard MCC Codes
MCC_CATEGORIES = [
    ("Grocery", "5411"),
    ("Travel", "4511"),
    ("Retail", "5310"),
    ("Digital Goods", "5815"),
    ("Dining", "5812")
]

# Chargeback Reason Codes
REASON_FRAUD = "10.4"
REASON_NOT_RECEIVED = "13.1"
REASON_DUPLICATE = "12.6"

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        home_country TEXT,
        account_age_days INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT PRIMARY KEY,
        user_id TEXT,
        amount REAL,
        currency TEXT,
        merchant_name TEXT,
        merchant_category TEXT,
        mcc_code TEXT,
        transaction_country TEXT,
        card_present BOOLEAN,
        timestamp DATETIME,
        status TEXT,
        dispute_reason TEXT,
        is_fraudulent_ground_truth BOOLEAN,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    conn.commit()
    return conn

def generate_users(num_users=500):
    users = []
    for _ in range(num_users):
        users.append({
            "user_id": str(uuid.uuid4()),
            "home_country": fake.country_code(representation="alpha-2"),
            "account_age_days": random.randint(1, 3650)
        })
    return users

def generate_data():
    conn = setup_db()
    cursor = conn.cursor()
    
    # 1. Generate Users
    users = generate_users(500)
    cursor.executemany(
        "INSERT INTO users (user_id, home_country, account_age_days) VALUES (:user_id, :home_country, :account_age_days)", 
        users
    )
    
    # 2. Generate Transactions
    TOTAL_TXNS = 2000
    DISPUTE_RATE = 0.09 # ~9%
    num_disputed = int(TOTAL_TXNS * DISPUTE_RATE)
    num_clean = TOTAL_TXNS - num_disputed
    
    transactions = []
    
    # Generate Clean Transactions
    for _ in range(num_clean):
        user = random.choice(users)
        category, mcc = random.choice(MCC_CATEGORIES)
        
        tx = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "amount": round(random.uniform(5.0, 500.0), 2),
            "currency": "USD",
            "merchant_name": fake.company(),
            "merchant_category": category,
            "mcc_code": mcc,
            "transaction_country": user["home_country"] if random.random() > 0.1 else fake.country_code(representation="alpha-2"),
            "card_present": random.choice([True, False]),
            "timestamp": fake.date_time_between(start_date='-1y', end_date='now'),
            "status": "completed",
            "dispute_reason": None,
            "is_fraudulent_ground_truth": False
        }
        transactions.append(tx)
        
    # Generate Disputed Transactions (Edge Cases)
    # Evenly split among 4 types: true fraud, not received, duplicate, legitimate-but-flagged
    dispute_types = ["true_fraud", "not_received", "duplicate", "legit_flagged"]
    
    for i in range(num_disputed):
        user = random.choice(users)
        dtype = dispute_types[i % 4]
        category, mcc = random.choice(MCC_CATEGORIES)
        
        if dtype == "true_fraud":
            # High-value + international + card-not-present
            diff_country = fake.country_code(representation="alpha-2")
            while diff_country == user["home_country"]:
                diff_country = fake.country_code(representation="alpha-2")
                
            tx = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "amount": round(random.uniform(1000.0, 5000.0), 2),
                "currency": "USD",
                "merchant_name": fake.company(),
                "merchant_category": category,
                "mcc_code": mcc,
                "transaction_country": diff_country,
                "card_present": False,
                "timestamp": fake.date_time_between(start_date='-1m', end_date='now'),
                "status": "disputed",
                "dispute_reason": REASON_FRAUD,
                "is_fraudulent_ground_truth": True
            }
            transactions.append(tx)
            
        elif dtype == "not_received":
            tx = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "amount": round(random.uniform(20.0, 300.0), 2),
                "currency": "USD",
                "merchant_name": fake.company(),
                "merchant_category": category, # likely digital goods or retail
                "mcc_code": mcc,
                "transaction_country": user["home_country"],
                "card_present": False,
                "timestamp": fake.date_time_between(start_date='-3m', end_date='-1w'),
                "status": "disputed",
                "dispute_reason": REASON_NOT_RECEIVED,
                "is_fraudulent_ground_truth": False
            }
            transactions.append(tx)
            
        elif dtype == "duplicate":
            merchant_name = fake.company()
            timestamp1 = fake.date_time_between(start_date='-2m', end_date='now')
            timestamp2 = timestamp1 + timedelta(minutes=random.randint(1, 5))
            amount = round(random.uniform(10.0, 100.0), 2)
            
            # The first legitimate one
            tx1 = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "amount": amount,
                "currency": "USD",
                "merchant_name": merchant_name,
                "merchant_category": category,
                "mcc_code": mcc,
                "transaction_country": user["home_country"],
                "card_present": True,
                "timestamp": timestamp1,
                "status": "completed",
                "dispute_reason": None,
                "is_fraudulent_ground_truth": False
            }
            transactions.append(tx1)
            
            # The disputed duplicate one
            tx2 = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "amount": amount,
                "currency": "USD",
                "merchant_name": merchant_name,
                "merchant_category": category,
                "mcc_code": mcc,
                "transaction_country": user["home_country"],
                "card_present": True,
                "timestamp": timestamp2,
                "status": "disputed",
                "dispute_reason": REASON_DUPLICATE,
                "is_fraudulent_ground_truth": False # It's a duplicate, not malicious fraud
            }
            transactions.append(tx2)
            
        elif dtype == "legit_flagged":
            # Suspicious but Legitimate: Large purchase, matching home country, card present
            tx = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "amount": round(random.uniform(800.0, 3000.0), 2),
                "currency": "USD",
                "merchant_name": fake.company(),
                "merchant_category": category,
                "mcc_code": mcc,
                "transaction_country": user["home_country"],
                "card_present": True,
                "timestamp": fake.date_time_between(start_date='-1m', end_date='now'),
                "status": "disputed",
                "dispute_reason": REASON_FRAUD, # User or system flagged it as fraud
                "is_fraudulent_ground_truth": False # But it's actually legitimate
            }
            transactions.append(tx)

    cursor.executemany(
        """
        INSERT INTO transactions (
            transaction_id, user_id, amount, currency, merchant_name, 
            merchant_category, mcc_code, transaction_country, card_present, 
            timestamp, status, dispute_reason, is_fraudulent_ground_truth
        ) VALUES (
            :transaction_id, :user_id, :amount, :currency, :merchant_name,
            :merchant_category, :mcc_code, :transaction_country, :card_present,
            :timestamp, :status, :dispute_reason, :is_fraudulent_ground_truth
        )
        """, 
        transactions
    )
    
    conn.commit()
    conn.close()
    
    print(f"Generated {len(users)} users and {len(transactions)} transactions.")
    print("Edge cases and distributions applied successfully.")

if __name__ == "__main__":
    generate_data()
