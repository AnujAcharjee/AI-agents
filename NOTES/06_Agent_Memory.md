# Agent Memory

Memory allows AI agents to retain context, learn from past experiences, and personalize interactions across turns and sessions.

---

## 1. Short-Term vs. Long-Term Memory

```text
┌────────────────────────────────────────────────────────┐
│                      Agent Memory                      │
├──────────────────────────┬─────────────────────────────┤
│    Short-Term Memory     │      Long-Term Memory       │
│    (In-Session State)    │   (Cross-Session Storage)   │
├──────────────────────────┼─────────────────────────────┤
│ • Current chat history   │ • Episodic (Past events)    │
│ • Tool calls & results   │ • Semantic / Factual (Facts)│
│ • Scratchpad / State     │ • Procedural (Rules/Skills) │
└──────────────────────────┴─────────────────────────────┘
```

---

## 2. Short-Term Memory (Working Memory)

- **Scope:** Restricted to the active task, conversation, or session (`thread_id`).
- **Purpose:** Tracks ongoing context so the agent can reason step-by-step without losing track of current goals.
- **What it stores:**
  - Recent conversation turns (user & assistant messages).
  - Intermediate tool execution results and observations.
  - Scratchpad thoughts / plan progress.
- **Implementations:**
  - **In-Context Buffer:** Passing recent messages directly in the prompt.
  - **Sliding Window / Summary:** Keeping last $N$ turns or periodically summarizing earlier conversation.
  - **Graph State / Checkpointers:** E.g., LangGraph thread-level state saved per step.

---

## 3. Long-Term Memory (Persistent Memory)

Persists across separate sessions and time. It is stored externally (databases, vector stores, knowledge graphs) and retrieved dynamically when relevant.

### A. Factual Memory
- **What it is:** Objective facts and attributes about the user, entities, or domain.
- **Example:** *"User is allergic to peanuts"*, *"User prefers code in TypeScript"*, *"Project uses PostgreSQL"*.
- **Storage:** Key-value stores, JSON profiles, or entity knowledge graphs.

### B. Episodic Memory
- **What it is:** Specific past experiences, events, and sequential action traces ("what happened and when").
- **Example:** *"In yesterday's task, deployment failed because Docker port 8080 was busy; restarting the container fixed it."*
- **Purpose:** Enables the agent to reuse past solutions, avoid repeating mistakes, and recall prior user interactions.
- **Storage:** Vector databases (retrieved via semantic similarity / embedding search) or chronological event logs.

### C. Semantic Memory
- **What it is:** Generalized concepts, domain knowledge, and learned rules abstracted away from specific episodes.
- **Example:** *"Rate limits on API X reset every hour"*, *"Documentation on Company API v2"*.
- **Storage:** Vector stores (RAG), vector databases, or curated knowledge bases.

*(Note: In literature, **Factual** is often treated as a subset of **Semantic** memory).*

---

## Agent Memory Lifecycle

1. **Extract:** During/after a session, an LLM extracts key facts, user preferences, and learnings.
2. **Store & Consolidate:** Insights are embedded and saved into a database (updating or merging with existing memories).
3. **Retrieve:** On a new user query, the agent searches long-term memory for relevant context.
4. **Inject:** Retrieved memories are injected into the short-term prompt context before generation.

---

## 4. Graph Memory

Graph memory models an agent's knowledge as a network of nodes (entities, people, concepts) and directed edges (relationships, dependencies, actions). Unlike pure vector databases that rely solely on textual similarity, graph memory explicitly maps interconnected relationships (e.g., *"User works at Company"*, *"Company uses Tech Stack"*) and allows multi-hop reasoning. In AI, it is primarily used in **GraphRAG**, complex multi-entity tracking, fraud detection, recommendation engines, and long-term personalization where relationship context matters as much as text meaning. In our stack, **Neo4j** serves as the graph database engine to store, link, and traverse these entity relationships.