# Agentic Transaction Dispute & Fraud Review Assistant — Master Build Plan

Working name: `dispute-agent` (rename once you pick something better — DisputeIQ, ClearCase, whatever)

---

## 1. Repo Structure

```
dispute-agent/
├── AGENTS.md                      # Cursor instructions — write this FIRST
├── README.md
├── requirements.txt
├── data/
│   ├── generate_transactions.py   # synthetic data generator
│   ├── transactions.db            # SQLite, generated
│   ├── policies/                  # 15-20 markdown docs, written by you
│   │   ├── chargeback_reason_codes.md
│   │   ├── merchant_category_rules.md
│   │   └── precedent_cases.md
│   └── eval/
│       └── labeled_cases.jsonl    # 30-50 hand-labeled disputes w/ ground truth
├── src/
│   ├── config.py
│   ├── agents/
│   │   ├── intake_agent.py
│   │   ├── retriever_agent.py
│   │   ├── analyst_agent.py
│   │   ├── compliance_agent.py
│   │   └── graph.py                # LangGraph wiring, state schema
│   ├── tools/
│   │   ├── sql_tool.py             # structured transaction query
│   │   ├── rag_tool.py             # hybrid retrieval (BM25 + embeddings)
│   │   └── fraud_scorer.py         # small sklearn classifier, exposed as tool
│   ├── eval/
│   │   ├── ragas_eval.py
│   │   └── judge_eval.py           # LLM-as-judge vs ground truth
│   ├── observability/
│   │   └── tracing.py              # Langfuse instrumentation wrapper
│   └── api/
│       └── main.py                 # FastAPI
├── tests/
├── docker/
│   └── Dockerfile
└── .github/workflows/ci.yml         # runs eval, blocks merge if score drops
```

---

## 2. Agent Graph (LangGraph)

**State object** carries: `transaction_id`, `transaction_data`, `retrieved_policy_chunks`, `fraud_score`, `analyst_decision`, `analyst_reasoning`, `compliance_verdict`, `needs_human_review`, `final_output`.

**Nodes:**
- `intake` → pulls transaction row via SQL tool, populates state
- `retrieve` → hybrid RAG over policy corpus based on transaction's dispute reason
- `analyze` → LLM reasons over transaction + retrieved policy + fraud_score, produces decision + reasoning
- `compliance_check` → LLM-as-judge checks analyst's reasoning against retrieved policy for hallucination/unsupported claims
- `human_review` → LangGraph `interrupt()`, triggered conditionally

**Edges:**
- `intake → retrieve → analyze → compliance_check`
- `compliance_check`: if flagged → loop back to `analyze` with critique injected (max 1 retry, then force human review)
- `compliance_check` → conditional: `fraud_score > threshold OR compliance flagged twice` → `human_review`, else → `final_output`

---

## 3. Build Order (dependency-driven)

1. **Data layer** — synthetic transaction generator + SQLite schema.
2. **SQL tool + intake agent** — test standalone.
3. **Policy corpus + RAG tool + retriever agent** — test retrieval quality manually.
4. **Analyst agent** — combine intake + retrieval, produce a decision.
5. **Fraud scorer tool** — train a small classical model, wire in as a callable tool.
6. **LangGraph wiring** — connect intake → retrieve → analyze.
7. **Compliance/critic agent** + loop-back edge.
8. **Human-in-the-loop interrupt** — test pause/resume.
9. **Observability instrumentation** — retrofit Langfuse tracing.
10. **Eval harness** — labeled cases, RAGAS, LLM-as-judge.
11. **FastAPI wrapper** — POST endpoint.
12. **Docker + CI gate** — GitHub Action runs eval.
13. **README** — architecture diagram, eval numbers, optimizations.
