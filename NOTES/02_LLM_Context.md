# [LLM WIKI](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

- An LLM Wiki is a structured Markdown-based memory system that stores project context, plans, and implementation details.
- It acts as a persistent, editable working memory for the LLM, complementing a vector database (which provides retrieval-based long-term memory).
- Instead of relying solely on retrieval, the system maintains a canonical, human-readable state that can be incrementally updated through an agent or orchestration layer.
- When needed, relevant information can be fetched from the vector DB and incorporated into the Markdown memory, improving consistency, traceability, and reducing hallucinations.

---

# RAG (Retrieval-Augmented Generation)

RAG is a technique where an LLM retrieves relevant external data and uses it to generate more accurate answers.

### How it works

- User asks a question
- System searches a vector database for related information
- Retrieved data is added to the prompt
- LLM generates the answer using that context

### Why RAG is used

- LLMs have limited context window
- Training data may be outdated
- Reduces hallucinations
- Allows use of private/custom data

### Key idea

- RAG does NOT store memory — it fetches context when needed.

### RAG vs Memory

- RAG: dynamic, query-time context (stateless)
- Memory (e.g., Markdown/wiki): persistent, structured context (stateful)

### Components

- Embedding model → converts text to vectors
- Vector database → stores searchable embeddings
- Retriever → finds relevant chunks
- LLM → generates final answer
