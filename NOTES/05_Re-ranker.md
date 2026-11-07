# Re-ranker

## What is a Re-ranker?

A **Re-ranker** is an intermediate model (typically a **Cross-Encoder**) that takes the user's query and candidate chunks retrieved from the vector database, evaluates them together, and **re-scores / re-orders them based on true semantic relevance**.

> **Vector Search (Fast Retrieval)** finds broadly relevant candidates → **Re-ranker (Deep Scoring)** sorts them so the chunks closest and most accurate to the user query end up at the very top.

---

## Why is a Re-ranker Needed?

Standard vector similarity search (bi-encoder retrieval) is very fast, but it has key limitations:

### 1. Vector Search Misses Nuance (Bi-Encoder vs. Cross-Encoder)
- **Vector Search (Bi-Encoder):** Encodes the query and chunks separately into vectors, then compares cosine distance. Because it calculates representations independently, it often misses specific nuances, keyword constraints, or subtle context.
- **Re-ranker (Cross-Encoder):** Feeds both the `[Query]` and `[Document Chunk]` together into the model attention layers simultaneously. This captures deep relationships between words in the question and words in the text.

### 2. Eliminates "False Positives" and Noise
Vector search can pull chunks that share similar words or general topic embedding, but do not actually answer the question. A re-ranker filters out this noise.

### 3. Solves the "Lost in the Middle" Problem
LLMs pay the most attention to information at the very beginning and very end of their prompt context. If a crucial chunk is buried in the middle of 10 retrieved chunks, the LLM may ignore or miss it. A re-ranker guarantees the highest-quality, most pertinent chunk is placed right at the top.

---

## How Many Relevant Chunks Should Be Picked?

A two-stage retrieval strategy balances speed, cost, and accuracy:

```text
               Vector DB Search (High Recall)
                      Retrieve Top-K (e.g., 20 - 50 Chunks)
                                   ↓
                       Re-ranker (High Precision)
                      Score & Re-order Chunks
                                   ↓
                         Select Top-N (e.g., 3 - 5 Chunks)
                                   ↓
                         LLM Final Context
```

### Stage 1: Initial Vector Retrieval (`Top-K`: 20 to 50 chunks)
- **Goal:** High **Recall** (ensure the correct answer is captured somewhere in the pool).
- Vector search is extremely cheap and fast, so you cast a wide net (e.g., 20, 30, or 50 chunks).

### Stage 2: Final Re-ranked Selection (`Top-N`: 3 to 5 chunks)
- **Goal:** High **Precision** (deliver only the most exact, concentrated context to the LLM).
- After re-ranking, only keep the top **3 to 5 chunks** (rarely more than 7–10).

### Key Factors Determining the Final Number (`Top-N`):
1. **Chunk Size:**
   - Small chunks (100–250 tokens): You can pass **5 to 10 chunks**.
   - Large chunks (500–1000+ tokens): Pass only **2 to 4 chunks** to avoid token bloat.
2. **Context Window & API Costs:**
   - Fewer, higher-quality chunks reduce latency and API token usage.
3. **Query Complexity:**
   - Factual single-hop questions (e.g., *"What is the leave policy limit?"*) usually need only **1 to 3 chunks**.
   - Multi-hop / comparative questions (e.g., *"Compare product A and product B features"*) may need **5 to 8 chunks**.

---

## RAG Pipeline with Re-ranker

```text
Large Collection of Files
          ↓
    Process / Chunk
          ↓
    Create Embeddings
          ↓
     Vector Database
          ↓
      User Question
          ↓
  Fast Vector Search (Top-K: 20-50 Chunks)
          ↓
   Re-ranker (Cross-Encoder Scoring)
          ↓
  Top-N Chunks (3-5 Most Relevant Chunks)
          ↓
   LLM + Highly Relevant Chunks
          ↓
        Answer
```
