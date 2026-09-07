# Project Build Steps Tracking

This document tracks our progress through the dependency-driven build order. Update the status of each step as we progress.

- [x] **Step 1: Data layer** — synthetic transaction generator + SQLite schema.
- [x] **Step 2: SQL tool + intake agent** — test standalone.
- [ ] **Step 3: Policy corpus + RAG tool + retriever agent** — write policy docs, test retrieval quality manually.
- [ ] **Step 4: Analyst agent** — combine intake + retrieval, produce a decision.
- [ ] **Step 5: Fraud scorer tool** — train a small classical model on synthetic features, wire in as a tool.
- [ ] **Step 6: LangGraph wiring** — connect intake → retrieve → analyze as a graph.
- [ ] **Step 7: Compliance/critic agent** + loop-back edge.
- [ ] **Step 8: Human-in-the-loop interrupt** — test the pause/resume flow explicitly.
- [ ] **Step 9: Observability instrumentation** — retrofit Langfuse tracing onto every node and tool.
- [ ] **Step 10: Eval harness** — labeled cases, RAGAS, LLM-as-judge agreement scoring.
- [ ] **Step 11: FastAPI wrapper** — `POST /investigate {transaction_id}` → decision + trace_id.
- [ ] **Step 12: Docker + CI gate** — GitHub Action runs the eval script on push.
- [ ] **Step 13: README** — architecture diagram, eval numbers, Langfuse trace, optimizations.
