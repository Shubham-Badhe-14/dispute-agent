# Resume State

When you resume tomorrow, you are in the middle of executing **Step 10 (Eval harness)**.

## What has been done so far (Step 10):
- **Model Fix:** Configured `get_llm()` in `src/config.py` to correctly use `gemini-2.0-flash`.
- **Dynamic Throttle:** Implemented parsing logic in `src/eval/judge_eval.py` to extract the exact `retry_after` delay from Gemini's `429 RESOURCE_EXHAUSTED` responses and sleep accordingly + 2 seconds to prevent rate limit crashing.
- **RAGAS:** Safely installed `ragas` and `datasets` to the virtual environment.
- **Eval Cases Mapping:** Attempted to map 15 handcrafted, nuanced edge-cases to real `transaction_id`s in the SQLite database via `scratch/match_cases.py`. 
- **Mapping Failure:** The synthetic `transactions.db` did not possess exactly matching rows for 8 of the nuanced edge cases (e.g., dropping `country_match` checks). The resulting mapped cases lost their intended logic completely.

## What is left to do:
1. **Inject Edge Cases into DB:** Write a quick script to generate and insert 8 perfectly matching synthetic rows into `data/transactions.db` for the dropped constraint cases (Cases 6, 7, 9, 10, 11, 12, 13, 15).
2. **Re-Run Mapping:** Once inserted, run `python scratch/match_cases.py` again to generate the flawless `data/eval/agent_eval_cases.jsonl`.
3. **Execute the Eval Harness:** Run the throttled harness across the new 15 cases.
   ```bash
   source venv/bin/activate
   python src/eval/judge_eval.py
   ```
4. **Move to Step 11:** Once the evaluation completes successfully, finalize Step 10 and move on to Step 11 (FastAPI wrapper).
