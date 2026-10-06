# Large Language Model (LLM)

- A Large Language Model (LLM) is an advanced deep learning / machine learning model trained on vast amounts of text data to comprehend, summarize, and generate human-like language.
- Primarily based on the **Transformer architecture** (utilizing self-attention mechanisms).

### Key Characteristics

- **Tokenization:** Breaks down text into smaller units (tokens) such as words, sub-words, or characters.
- **Context Window:** The maximum number of tokens the model can process and reason over in a single prompt/session.
- **Next-Token Prediction:** At its core, an LLM predicts the most statistically probable next token given the preceding sequence.

### Training Lifecycle

1. **Pre-training:** Unsupervised learning on massive web-scale corpora to learn grammar, syntax, facts, and general reasoning (resulting in a *Base Model*).
2. **Instruction Fine-Tuning (SFT):** Supervised fine-tuning on high-quality prompt-response pairs to teach the model how to follow instructions and act as an assistant.
3. **Alignment (RLHF / DPO):** Reinforcement Learning from Human Feedback or Direct Preference Optimization to make responses helpful, harmless, and honest.

### Strengths & Capabilities

- Text generation, summarization, translation, code generation, reasoning, and problem-solving.
- In-context learning (zero-shot and few-shot prompting without weight updates).

### Limitations & Challenges

- **Hallucinations:** Can generate plausible-sounding but factually incorrect assertions.
- **Knowledge Cutoff:** Fixed knowledge limited to the training dataset timestamp unless augmented with external tools or retrieval (e.g., RAG, Search).
- **Statelessness:** Does not retain persistent memory across independent requests.

---

# Multimodal AI (Multi-modal Models)

- Multimodal AI refers to machine learning models that can process, understand, and generate information across **multiple types of data modalities** (e.g., text, images, audio, video, code).
- Extends beyond text-only LLMs by bridging different sensory inputs into a unified representation space.

### How Multimodal AI Works

- **Modality Encoders:** Specialized encoders (e.g., Vision Transformers / CLIP for images, audio encoders for speech) convert raw non-text inputs into feature embeddings.
- **Projection / Cross-Attention:** Maps the modality embeddings into the shared latent space of the language model backbone.
- **Unified Reasoning Engine:** The core transformer processes both textual tokens and multimodal embeddings together to reason and generate responses.

### Supported Modalities

- **Text:** Prompts, documents, markdown, code.
- **Vision:** Images, diagrams, charts, UI screenshots, video frames.
- **Audio:** Spoken voice, acoustic signals, ambient sound.

### Common Use Cases

- **Visual Document Understanding (VDU):** Parsing invoices, receipts, PDFs with diagrams, and complex financial charts.
- **UI / Design to Code:** Converting wireframes, sketches, and screenshots directly into code.
- **Real-Time Interactive Agents:** Conversational assistants that listen, speak, and see user screens or camera feeds in real time.
- **Multimodal RAG:** Indexing and retrieving charts, screenshots, and diagrams alongside text chunks.