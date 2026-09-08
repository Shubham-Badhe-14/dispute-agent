import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.agents.state import AgentState
from src.tools.rag_tool import retrieve_policies

def retriever_node(state: AgentState) -> dict:
    """
    Retriever node: Extracts dispute_reason and mcc_code from the transaction_data,
    invokes the RAG tool, and appends the retrieved policy chunks to the state.
    """
    transaction_data = state.get("transaction_data", {})
    
    dispute_reason = transaction_data.get("dispute_reason")
    mcc_code = transaction_data.get("mcc_code")
    
    # If there's no reason or MCC, we might just return empty policies or do a semantic search
    # But usually, there's at least an MCC.
    if not dispute_reason and not mcc_code:
        return {"retrieved_policy_chunks": ["No relevant policy found."]}
        
    try:
        # retrieve_policies is a LangChain @tool
        # We can invoke it with the arguments directly
        result_text = retrieve_policies.invoke({
            "dispute_reason": str(dispute_reason) if dispute_reason else None, 
            "mcc_code": str(mcc_code) if mcc_code else None
        })
        
        # We'll just store the resulting combined text as a single chunk for simplicity
        # or we could parse it back into a list. For now, a list of 1 string is fine.
        return {"retrieved_policy_chunks": [result_text]}
        
    except Exception as e:
        return {
            "error": f"RAG error: {str(e)}",
            "retrieved_policy_chunks": [f"Error retrieving policies: {str(e)}"]
        }

if __name__ == "__main__":
    print("--- Running Retriever Agent Verification ---")
    
    # 1. Happy Path: Exact match for Reason 10.4 and MCC 5411
    print("\n[Test 1] Happy Path: Reason 10.4 and MCC 5411")
    happy_state = {
        "transaction_data": {
            "dispute_reason": "10.4",
            "mcc_code": "5411"
        }
    }
    result = retriever_node(happy_state)
    chunks = result.get("retrieved_policy_chunks", [])
    print(f"Retrieved {len(chunks)} chunk(s).")
    print("Content preview:")
    print(chunks[0][:200] + "..." if len(chunks[0]) > 200 else chunks[0])
    
    assert "10.4" in chunks[0] or "5411" in chunks[0], "Failed to retrieve exact match content"
    
    # 2. Negative Path: Nonsense codes
    print("\n[Test 2] Negative Path: Reason 99.9 and MCC 9999")
    negative_state = {
        "transaction_data": {
            "dispute_reason": "99.9",
            "mcc_code": "9999"
        }
    }
    result2 = retriever_node(negative_state)
    chunks2 = result2.get("retrieved_policy_chunks", [])
    print(f"Retrieved {len(chunks2)} chunk(s).")
    print("Content preview:")
    print(chunks2[0])
    
    assert "No relevant policy found." in chunks2[0], "Threshold cutoff failed, returned irrelevant chunks"
    
    print("\n--- Verification Complete! ---")
