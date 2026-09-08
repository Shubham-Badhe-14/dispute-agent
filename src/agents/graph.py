from typing import TypedDict, Any, List, Optional
from langgraph.graph import StateGraph, START, END
from src.agents.intake_agent import intake_node
from src.agents.retriever_agent import retriever_node
from src.agents.analyst_agent import analyst_node
from src.tools.fraud_scorer import score_fraud

from src.agents.state import AgentState

def fraud_scorer_node(state: AgentState) -> dict:
    """
    Computes the fraud score using the machine learning tool.
    """
    data = state.get("transaction_data", {})
    amount = data.get("amount", 0.0)
    card_present = data.get("card_present", 0)
    transaction_country = data.get("transaction_country", "")
    home_country = data.get("home_country", "") # Joined from users table
    
    try:
        score = score_fraud.invoke({
            "amount": amount,
            "card_present": bool(card_present),
            "transaction_country": transaction_country,
            "home_country": home_country
        })
        return {"fraud_score": score}
    except Exception as e:
        return {"error": f"Fraud Scorer failed: {str(e)}"}

def should_continue_after_intake(state: AgentState) -> str:
    """
    Conditional routing after intake: short-circuit to END if there's an error.
    """
    if state.get("error"):
        return END
    return "score_fraud"

def should_continue_after_score(state: AgentState) -> str:
    if state.get("error"):
        return END
    return "retrieve"

from src.agents.compliance_agent import compliance_node
from src.agents.human_review_agent import human_review_node
from langgraph.checkpoint.memory import MemorySaver

def should_continue_after_compliance(state: AgentState) -> str:
    """
    Conditional routing after compliance check.
    If pass -> END
    If fail & retry_count < 1 -> analyze
    If fail & retry_count >= 1 -> human_review
    """
    verdict = state.get("compliance_verdict")
    needs_human = state.get("needs_human_review", False)
    
    if verdict == "pass":
        return END
    
    if verdict == "fail" and not needs_human:
        return "analyze"
        
    return "human_review"

# Build the LangGraph
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("intake", intake_node)
builder.add_node("score_fraud", fraud_scorer_node)
builder.add_node("retrieve", retriever_node)
builder.add_node("analyze", analyst_node)
builder.add_node("compliance", compliance_node)
builder.add_node("human_review", human_review_node)

# Define edges
builder.add_edge(START, "intake")

# Conditional edge after intake handles short-circuiting on bad IDs
builder.add_conditional_edges("intake", should_continue_after_intake)

# score_fraud -> retrieve
builder.add_conditional_edges("score_fraud", should_continue_after_score)

# retrieve -> analyze
builder.add_edge("retrieve", "analyze")

# analyze -> compliance
builder.add_edge("analyze", "compliance")

# compliance -> conditional
builder.add_conditional_edges("compliance", should_continue_after_compliance)

# human_review -> END
builder.add_edge("human_review", END)

# Compile graph with a checkpointer and pause right before human_review
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["human_review"])

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Standalone Test
    print("--- Running Graph E2E Test ---")
    import sqlite3
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
        print(f"Testing with valid ID: {valid_id}")
        initial_state = {"transaction_id": valid_id}
        
        try:
            for s in graph.stream(initial_state):
                node_name = list(s.keys())[0]
                print(f"Completed Node: {node_name}")
            
            final_state = s[node_name]
            print("\nFinal Decision:", final_state.get("analyst_decision"))
            print("Fraud Score:", final_state.get("fraud_score"))
        except Exception as e:
            print(f"Graph execution failed: {e}")
    
    print("\n[Test] Negative Path (bad ID):")
    bad_state = {"transaction_id": "bad-id"}
    try:
        for s in graph.stream(bad_state):
            node_name = list(s.keys())[0]
            print(f"Completed Node: {node_name}")
        final_state = s[node_name]
        print("Final Output:", final_state.get("final_output"))
    except Exception as e:
        print(f"Graph execution failed: {e}")
