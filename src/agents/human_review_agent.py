from src.agents.state import AgentState

def human_review_node(state: AgentState) -> dict:
    """
    Node representing the manual human review stage.
    The graph pauses before reaching this node due to `interrupt_before=["human_review"]`.
    When a human resumes the graph, this node executes and finalizes the output.
    """
    # At this point, a human could have injected an updated analyst_decision or final_output 
    # directly into the state via graph.update_state().
    # If the final_output hasn't been explicitly resolved by the human, we set a default acknowledgment.
    current_output = state.get("final_output", "")
    
    return {
        "final_output": current_output + " (Processed by Human Reviewer)"
    }
