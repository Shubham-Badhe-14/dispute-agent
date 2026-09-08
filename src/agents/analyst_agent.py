import sys
import os
from typing import Literal
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from langchain_core.prompts import ChatPromptTemplate
from src.agents.state import AgentState
from src.config import get_llm

class AnalystDecision(BaseModel):
    decision: Literal["approve", "deny", "escalate"] = Field(
        description="The final decision for the dispute: approve, deny, or escalate."
    )
    reasoning: str = Field(
        description="Detailed reasoning for the decision based on policy and transaction data."
    )
    confidence: float = Field(
        description="Confidence score for the decision from 0.0 to 1.0."
    )

def analyst_node(state: AgentState) -> dict:
    """
    Analyst node: Uses an LLM to reason over the transaction and retrieved policy.
    Returns a structured decision.
    """
    transaction_data = state.get("transaction_data", {})
    fraud_score = state.get("fraud_score", 0.0)
    policies = state.get("retrieved_policy_chunks", [])
    
    policy_text = "\n\n".join(policies)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a specialized fraud and dispute resolution analyst. Your job is to review transactions against policies and make a structured decision."),
        ("user", "Transaction Details: {tx_data}\nFraud Score (0.0 to 1.0): {score}\n\nRelevant Policies:\n{policy}\n\nPlease analyze and provide your decision.")
    ])
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(AnalystDecision)
    chain = prompt | structured_llm
    
    response = chain.invoke({
        "tx_data": str(transaction_data),
        "score": fraud_score,
        "policy": policy_text
    })
    
    return {
        "analyst_decision": response.decision,
        "analyst_reasoning": response.reasoning
    }

if __name__ == "__main__":
    print("--- Running Analyst Agent Standalone Test ---")
    test_state = {
        "transaction_data": {
            "dispute_reason": "10.4",
            "mcc_code": "5411",
            "amount": 20.0,
            "card_present": True
        },
        "fraud_score": 0.1,
        "retrieved_policy_chunks": [
            "## Reason Code 10.4: Fraud\nDefinition: Cardholder states they did not authorize...",
            "## MCC 5411: Grocery Stores, Supermarkets\nRisk Profile: Low. Rules: Disputes for fraud are generally rare unless the physical card was stolen. Card-present transactions at grocery stores should almost always be considered legitimate unless clear evidence of theft is presented."
        ]
    }
    
    try:
        result = analyst_node(test_state)
        print(f"Decision: {result['analyst_decision']}")
        print(f"Reasoning:\n{result['analyst_reasoning']}")
    except Exception as e:
        print(f"Error during verification: {e}")
        print("Note: Ensure GOOGLE_API_KEY is exported in your environment.")
