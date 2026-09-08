import sys
import os

# Add src to the path for standalone execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.agents.state import AgentState
from src.tools.sql_tool import get_transaction_details

def intake_node(state: AgentState) -> dict:
    """
    Intake node: Pulls the transaction_id from state, invokes the SQL tool,
    and returns the updated state containing the full transaction data.
    Short-circuits by setting error/final_output if not found.
    """
    transaction_id = state.get("transaction_id")
    
    if not transaction_id:
        return {
            "error": "No transaction_id provided in state.",
            "final_output": "Failed at intake: No transaction_id provided."
        }
        
    try:
        # get_transaction_details is a LangChain @tool, so we invoke it
        data = get_transaction_details.invoke({"transaction_id": transaction_id})
        return {"transaction_data": data}
    except ValueError as e:
        # Not-found handling: short-circuit logic
        return {
            "error": str(e),
            "final_output": f"Failed at intake: {str(e)}"
        }
    except Exception as e:
        # Catch unexpected DB errors
        return {
            "error": f"Database error: {str(e)}",
            "final_output": f"Failed at intake: Database error {str(e)}"
        }

if __name__ == "__main__":
    import sqlite3
    
    # Standalone verification
    print("--- Running Intake Agent Verification ---")
    
    # 1. Happy Path: We need a valid transaction_id from the DB
    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        'data', 
        'transactions.db'
    )
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT transaction_id FROM transactions LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        valid_id = row[0]
        print(f"\n[Test 1] Happy Path with valid ID: {valid_id}")
        state = {"transaction_id": valid_id}
        result = intake_node(state)
        print("Result:", result)
        assert "transaction_data" in result, "transaction_data should be populated"
        assert "account_age_days" in result["transaction_data"], "JOIN failed to retrieve user fields"
    else:
        print("No transactions found in the database. Run Step 1 again.")
        
    # 2. Negative Path: Bogus transaction_id
    bogus_id = "this-id-does-not-exist"
    print(f"\n[Test 2] Negative Path with bogus ID: {bogus_id}")
    state = {"transaction_id": bogus_id}
    result = intake_node(state)
    print("Result:", result)
    assert "error" in result, "Error state should be populated on failure"
    assert "final_output" in result, "final_output should be populated to short-circuit the graph"
    
    print("\n--- Verification Complete! ---")
