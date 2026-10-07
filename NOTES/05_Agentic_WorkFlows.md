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
- **Checkpointer:** Mechanism that saves state snapshots after each step.

---

## Checkpointing in LangGraph

### What is Checkpointing?
A **Checkpointer** in LangGraph captures and saves a complete snapshot of the graph's `State` at every single execution step (after every node finishes).

```text
User Input ──► [Node A] ──► (Save Snapshot) ──► [Node B] ──► (Save Snapshot) ──► Output
                                  │                                │
                                  ▼                                ▼
                          Checkpoint in DB                 Checkpoint in DB
```

### Why is Checkpointing Crucial?

1. **Multi-Turn Conversation Memory:**
   - Instead of manually passing message history back and forth, the checkpointer automatically loads prior conversation state using a `thread_id`.
2. **Fault Tolerance & Crash Recovery:**
   - If a server crashes or an API times out during step 4 of a 6-step agent task, execution can resume directly from the last checkpoint without restarting from step 1.
3. **Human-in-the-Loop (HITL):**
   - The graph can pause before executing sensitive actions (e.g., sending an email, processing a payment), save state to the database, wait hours or days for human approval, and resume immediately.
4. **Time Travel & Debugging:**
   - You can rewind to an earlier state snapshot, inspect what went wrong, fork the state, or replay the graph with modified inputs.

---

## Checkpointing with MongoDB

### Why MongoDB?
- **Document Model Fits State:** LangGraph state is typically a Python dictionary / JSON object. MongoDB natively stores BSON/JSON documents, making serialization seamless.
- **Persistent & Distributed:** Unlike in-memory checkpointers (`MemorySaver`) that vanish when the server restarts, MongoDB persists state across app reboots, multi-worker clusters, and scaling containers.
