from typing import TypedDict, List

class AgentState(TypedDict, total=False):
    transaction_id: str
    transaction_data: dict
    retrieved_policy_chunks: List[str]
    fraud_score: float
    analyst_decision: str
    analyst_reasoning: str
    compliance_verdict: str
    needs_human_review: bool
    final_output: str
    error: str
