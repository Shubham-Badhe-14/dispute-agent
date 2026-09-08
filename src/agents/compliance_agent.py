import os
import sys
from pydantic import BaseModel, Field

# Add src to the path for standalone execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from langchain_core.prompts import ChatPromptTemplate
from src.agents.state import AgentState
from src.config import get_llm

class ComplianceDecision(BaseModel):
    is_compliant: bool = Field(description="True if the analyst's decision and reasoning strictly follow the retrieved policies, False otherwise.")
    feedback: str = Field(description="Detailed explanation of why it passed or failed. If it failed, specify exactly what policy was violated or ignored.")

def compliance_node(state: AgentState) -> dict:
    """
    Acts as a critic for the analyst. Verifies that the analyst's decision and reasoning 
    are sound and do not hallucinate policy logic.
    """
    llm = get_llm().with_structured_output(ComplianceDecision)
    
    analyst_decision = state.get("analyst_decision", "")
    analyst_reasoning = state.get("analyst_reasoning", "")
    policies = state.get("retrieved_policy_chunks", [])
    current_retry_count = state.get("retry_count", 0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strict Compliance Review Officer. Your job is to verify that the Analyst's decision strictly aligns with the provided Policies. If the analyst hallucinates a policy, makes a logical error, or violates the rules, you must fail them and provide constructive feedback."),
        ("human", "Analyst Decision: {decision}\n\nAnalyst Reasoning: {reasoning}\n\nRetrieved Policies:\n{policies}")
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "decision": analyst_decision,
        "reasoning": analyst_reasoning,
        "policies": "\n\n".join(policies)
    })
    
    if response.is_compliant:
        return {
            "compliance_verdict": "pass",
            "compliance_feedback": response.feedback
        }
    else:
        # If it fails, increment retry count
        new_retry_count = current_retry_count + 1
        needs_human = False
        
        # Max retries reached? (1 retry means current_retry_count was already 1)
        final_output = state.get("final_output", "")
        if current_retry_count >= 1:
            needs_human = True
            final_output = "Escalated for human review — automated resolution exceeded retry limit."
            
        return {
            "compliance_verdict": "fail",
            "compliance_feedback": response.feedback,
            "retry_count": new_retry_count,
            "needs_human_review": needs_human,
            "final_output": final_output
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("--- Running Compliance Agent Verification ---")
    
    # Simulate a bad analyst response that ignores a policy
    mock_state = {
        "analyst_decision": "approve",
        "analyst_reasoning": "I am approving this chargeback because the user is a nice person, even though it's a grocery store and the card was present.",
        "retrieved_policy_chunks": ["Card-present transactions at grocery stores (MCC 5411) must be denied absent evidence of physical theft."],
        "retry_count": 0
    }
    
    print("Mock Analyst Reasoning:", mock_state["analyst_reasoning"])
    result = compliance_node(mock_state)
    print("\nCompliance Verdict:", result.get("compliance_verdict"))
    print("Feedback:", result.get("compliance_feedback"))
    print("Retry Count:", result.get("retry_count"))
    print("Needs Human Review:", result.get("needs_human_review"))
    
    assert result["compliance_verdict"] == "fail", "Compliance failed to catch obvious violation"
