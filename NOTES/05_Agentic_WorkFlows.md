# Agentic Workflows with LangGraph

### What is an Agentic Workflow?
- A system where an LLM dynamically controls its execution flow (planning, taking actions, observing feedback, and looping) rather than following a fixed, hardcoded sequence.

---

### Real-World Example
**Scenario:** Customer refund request.
1. **Understand:** LLM reads customer message and extracts order ID.
2. **Action (Tool):** Checks order database (e.g., order is eligible for refund).
3. **Decision / Branching:** 
   - If eligible -> Trigger refund API.
   - If not eligible -> Draft explanation email.
4. **Loop / Reflect:** Checks if all steps succeeded before responding to the user.

---

### How LangGraph Helps

Standard LLM chains (like linear DAGs) struggle with loops and complex decisions. LangGraph solves this by treating workflows as **graphs**:

- **Cyclical Graphs (Loops):** Supports iterations, retries, and multi-step reasoning (e.g., generate -> evaluate -> revise).
- **Shared State:** Automatically passes and updates a centralized state object across all steps.
- **Conditional Branching:** Routes execution dynamically based on LLM outputs or tool results.
- **Human-in-the-Loop:** Can pause execution for human review/approval and resume seamlessly.
- **Persistence & Memory:** Built-in checkpointing to save and resume conversations or long-running tasks.

---

### Core Concepts in LangGraph
- **State:** The data structure (memory) shared across the entire workflow.
- **Nodes:** Python functions or agents that perform actions and update state.
- **Edges:** Rules that connect nodes (can be direct or conditional).
