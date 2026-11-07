# LangChain

LangChain is an open-source orchestration framework designed to simplify building applications powered by Large Language Models (LLMs), including chatbots, RAG pipelines, and autonomous agents.

---

## Core Components

### 1. Models (Model I/O)
- **What it is:** A standardized abstraction layer to interact with various LLMs, Chat Models, and Text Embedding models.
- **Why it matters:** Eliminates vendor lock-in. Instead of writing custom API integration code for each provider (OpenAI, Google Gemini, Anthropic, Ollama), you use a uniform interface (`ChatOpenAI`, `ChatGoogleGenerativeAI`). Swapping the underlying model requires changing only one line of configuration.
- **Main Categories:**
  - **Chat Models:** Take a list of structured messages (`SystemMessage`, `HumanMessage`, `AIMessage`) and return an `AIMessage`.
  - **LLMs (Legacy):** Take a raw string prompt and return a raw string response.
  - **Embeddings:** Convert text into numerical vector arrays for semantic similarity search.

---

### 2. Prompts (Prompt Templates)
- **What it is:** A structured API to create, parameterize, and format dynamic prompts for language models.
- **Why it matters:** Decouples static prompt instructions and few-shot examples from dynamic user runtime inputs.
- **Key Features:**
  - `PromptTemplate`: For single-string prompt formatting.
  - `ChatPromptTemplate`: For multi-role conversational messages (System, Human, AI).
  - **FewShotPromptTemplate:** Injects dynamic examples into the prompt to guide the model's behavior.
  - **Partial Formatting:** Pre-fills some variables early (e.g., current date, user role) while waiting for user input later.

---

### 3. Chains (LCEL - LangChain Expression Language)
- **What it is:** Sequences that connect models, prompt templates, output parsers, and custom functions into an end-to-end processing pipeline.
- **Why it matters:** Avoids messy manual glue code and callback spaghetti. Using the pipe operator (`|`), you can assemble clean, composable declarative pipelines:
  ```python
  chain = prompt | model | output_parser
  ```
- **Built-in Superpowers:**
  - First-class **streaming** (`stream()`, `astream()`).
  - Native **async** support (`ainvoke()`, `abatch()`).
  - **Parallel execution** (`RunnableParallel`) for fan-out tasks.
  - Automatic **fallbacks** and retries when an API fails.

---

### 4. Memory (Chat History & State)
- **What it is:** Utilities to persist and manage conversational context across multi-turn interactions.
- **Why it matters:** LLMs are inherently stateless; each API call knows nothing about previous exchanges. Memory injects relevant past conversational history into future prompt contexts.
- **Types of Memory:**
  - **Buffer Memory (`ChatMessageHistory`):** Stores all past messages raw in a list.
  - **Window Memory:** Retains only the last *K* exchanges to keep token counts low.
  - **Summary Memory:** Uses a background LLM call to summarize conversation history when the context gets too long.
  - **External Persistent Stores:** Persists chat history into production databases like Redis, MongoDB, or PostgreSQL.

---

### 5. Indexes / Retrieval (Data Connection & RAG)
- **What it is:** The complete toolkit for connecting external, private, and proprietary data to LLMs via Retrieval-Augmented Generation (RAG).
- **Core Building Blocks:**
  - **Document Loaders:** Ingest unstructured data from hundreds of sources (PDFs, Webpages, CSVs, Notion, Slack, SQL).
  - **Text Splitters:** Chunk large documents into smaller semantic pieces with configurable overlap (`RecursiveCharacterTextSplitter`).
  - **Vector Stores:** Store vector embeddings and provide fast similarity search (Qdrant, Chroma, Pinecone, FAISS).
  - **Retrievers:** High-level search interfaces that return relevant document chunks given a query (supports Vector similarity, BM25 keyword search, MMR for diversity, and Re-ranking).

---

### 6. Agents & Tools
- **What it is:** Systems where the LLM dynamically acts as a reasoning engine to decide *which* actions to take and in what order to solve a user goal.
- **Why it matters:** Chains follow a fixed, predetermined sequence. Agents evaluate progress dynamically and choose tools as needed.
- **Key Concepts:**
  - **Tools:** Standardized functions the agent can execute (e.g., Google Search, SQL database query, Python REPL, custom REST APIs).
  - **Agent Loop (ReAct / Tool-Calling):**
    ```text
    Input ──► LLM Reasons (Thought) ──► Calls Tool (Action) ──► Observes Tool Result ──► Decides Next Step / Returns Answer
    ```

---

### 7. Output Parsers
- **What it is:** Modules that parse and validate the raw text output of an LLM into structured data formats.
- **Why it matters:** LLMs output unstructured text by default. Output parsers enforce strict data structures (Pydantic models, JSON, CSV, lists) and trigger retries if the model generates invalid schemas.
