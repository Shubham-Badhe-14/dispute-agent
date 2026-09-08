import os
import sys
import json
import time
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

load_dotenv()

from src.agents.graph import builder
from src.observability.tracing import get_langfuse_handler
from src.config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langgraph.checkpoint.memory import MemorySaver

# Define LLM-as-a-judge output
class JudgeDecision(BaseModel):
    is_correct: bool = Field(description="True if the agent's decision matches the expected decision.")
    explanation: str = Field(description="Explanation of why the agent's decision is correct or incorrect based on the expected reasoning.")

def run_eval():
    eval_file = os.path.join(BASE_DIR, 'data', 'eval', 'agent_eval_cases.jsonl')
    
    if not os.path.exists(eval_file):
        print(f"Eval file not found: {eval_file}")
        return
        
    with open(eval_file, 'r') as f:
        lines = f.readlines()
        
    if not lines:
        print("No cases found in agent_eval_cases.jsonl")
        return
        
    # We compile locally so it does not conflict with existing thread states
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory, interrupt_before=["human_review"])
    
    handler = get_langfuse_handler()
    judge_llm = get_llm().with_structured_output(JudgeDecision)
    
    judge_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert evaluator. Compare the Agent's Decision and Reasoning against the Expected Decision and Expected Reasoning. Evaluate if the agent arrived at the CORRECT final decision based on valid logic."),
        ("human", "Agent Decision: {agent_decision}\nAgent Reasoning: {agent_reasoning}\n\nExpected Decision: {expected_decision}\nExpected Reasoning: {expected_reasoning}")
    ])
    
    judge_chain = judge_prompt | judge_llm
    
    results = []
    
    print(f"Starting evaluation of {len(lines)} cases...")
    
    for idx, line in enumerate(lines):
        if not line.strip():
            continue
            
        case = json.loads(line)
        tx_id = case['transaction_id']
        expected_decision = case['expected_decision']
        reasoning_notes = case['reasoning_notes']
        
        print(f"\n[{idx+1}/{len(lines)}] Testing Transaction: {tx_id}")
        
        initial_state = {"transaction_id": tx_id}
        config = {
            "configurable": {"thread_id": f"eval_thread_{tx_id}"},
            "callbacks": [handler]
        }
        
        try:
            import re
            max_retries = 3
            final_state = None
            
            # Run graph with retry
            for attempt in range(max_retries):
                try:
                    for update in graph.stream(initial_state, config=config):
                        pass
                    final_state = graph.get_state(config).values
                    break
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        match = re.search(r'Please retry in ([\d\.]+)s', err_str)
                        sleep_time = float(match.group(1)) + 2.0 if match else 60.0
                        print(f"  [Graph] Rate limit hit. Sleeping {sleep_time:.1f}s (Attempt {attempt+1}/{max_retries})")
                        time.sleep(sleep_time)
                        if attempt == max_retries - 1: raise e
                    else:
                        raise e
            
            agent_decision = final_state.get('analyst_decision', 'unknown')
            agent_reasoning = final_state.get('analyst_reasoning', 'none')
            
            # Run Judge with retry
            judge_res = None
            for attempt in range(max_retries):
                try:
                    judge_res = judge_chain.invoke({
                        "agent_decision": agent_decision,
                        "agent_reasoning": agent_reasoning,
                        "expected_decision": expected_decision,
                        "expected_reasoning": reasoning_notes
                    })
                    break
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        match = re.search(r'Please retry in ([\d\.]+)s', err_str)
                        sleep_time = float(match.group(1)) + 2.0 if match else 60.0
                        print(f"  [Judge] Rate limit hit. Sleeping {sleep_time:.1f}s (Attempt {attempt+1}/{max_retries})")
                        time.sleep(sleep_time)
                        if attempt == max_retries - 1: raise e
                    else:
                        raise e
            
            print(f"  Agent Decision: {agent_decision}")
            print(f"  Expected Decision: {expected_decision}")
            print(f"  Judge Score: {'PASS' if judge_res.is_correct else 'FAIL'}")
            
            results.append({
                "transaction_id": tx_id,
                "agent_decision": agent_decision,
                "expected_decision": expected_decision,
                "judge_pass": judge_res.is_correct,
                "judge_explanation": judge_res.explanation
            })
            
        except Exception as e:
            print(f"  Error processing {tx_id}: {e}")
            
        # Optional small sleep between cases just to be safe
        time.sleep(2)
        
    # Print Summary
    total = len(results)
    passed = sum(1 for r in results if r["judge_pass"])
    print(f"\n--- EVALUATION COMPLETE ---")
    print(f"Total Cases: {total}")
    print(f"Passed: {passed}")
    print(f"Accuracy: {(passed/total)*100:.2f}%" if total > 0 else "Accuracy: 0.00%")

if __name__ == "__main__":
    run_eval()
