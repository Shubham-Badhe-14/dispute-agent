# Agent Guidelines and Work Plan

Welcome, future Agent! This project follows a strict dependency-driven build order. This document outlines how you should operate.

## 1. Build Process
- Follow the sequence in `STEPS.md` and `MASTER_BUILD_PLAN.md`. DO NOT skip ahead.
- Build and test each numbered step standalone before wiring it into the broader LangGraph or system.
- Ensure that you don't add new dependencies without checking or flagging it first. Keep the stack constrained (LangGraph, FastAPI, Langfuse, RAGAS, SQLite, etc.).
- Update `STEPS.md` and `CHANGELOG.md` as you complete significant milestones.

## 2. Git and Version Control
- We commit and push code iteratively per step, rather than in giant dumps.
- **When a step is developed and tested properly**, create a commit. If you don't have push access, provide the user with the exact commands to review, commit, and push, e.g.:
  ```bash
  git add .
  git commit -m "feat(data): implement synthetic transaction generator"
  git push origin main
  ```
- Make sure to initialize the repo if it hasn't been already: `git init`, `git branch -M main`.

## 3. Testing and Verification
- **Standalone Testing**: For every new module (e.g., the SQL tool, the RAG tool), write a quick script or provide the terminal command to verify its functionality independently.
- If you cannot run the tests automatically, provide the user with clear instructions and commands to execute the tests.
- **Compatibility Check**: After completing a component, verify how it integrates with the rest of the application (e.g., checking data schemas against downstream agent expectations).

## 4. Continuity
- Before starting your task, read `MASTER_BUILD_PLAN.md`, `STEPS.md`, and `CHANGELOG.md` to get context on what has been done and what needs to be done next.
- Always document major decisions in `CHANGELOG.md`.
