# RAG System

## Problem

Suppose you need to build an **agent that is used by employees to retrieve information from a large collection of files**.

For example:

- Company documents
- PDFs
- Reports
- Internal documentation
- Policies
- Technical documents

The employee should be able to ask questions and get answers based on these files.

---

## Naive Approach

The simplest approach would be:

1. Extract the text from **all the files**.
2. Feed all of that text into the **LLM's context**.
3. Let the user ask questions based on that context.

### Problems with the Naive Approach

#### 1. High Token Usage

All the files may contain a **huge amount of text**.

Feeding all of this text to the LLM means:

- Large number of input tokens
- Higher API costs
- More unnecessary information sent to the model

#### 2. Context Window Limit

LLMs have a maximum **context window**—the maximum amount of information they can process in a single request.

If the collection of files becomes too large, the combined text will eventually **exceed the model's context window**.

> Even with very large context windows (for example, GPT-5.0's 1M-token context), a sufficiently large document collection can exceed the limit.

#### 3. Irrelevant Information

Most of the files are usually **not relevant to every question**.

For example, if an employee asks:

> "What is our company's vacation policy?"

There is no reason to send the LLM:

- Engineering documentation
- Sales reports
- Financial spreadsheets
- Old project documents
- Marketing material

Only the information relevant to the **vacation policy** is needed.

---

## Solution: RAG

This is where **RAG (Retrieval-Augmented Generation)** comes in.

Instead of sending **all documents** to the LLM:

> **Retrieve only the relevant information → Give it to the LLM → Generate the answer**

### Basic RAG Flow/Pipeline

```text
Large Collection of Files
          ↓
    Process / Chunk
          ↓
    Create Embeddings (Vector Embeddings)
          ↓
     Vector Database
          ↓
      User Question (vector similarity search)
          ↓
    Retrieve Relevant
        Chunks
          ↓
     LLM + Retrieved
       Information
          ↓
        Answer
```

The key idea is:

> **Don't give the LLM everything. Retrieve only what is relevant to the user's question.**
