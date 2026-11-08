# ChatBot Features

- Built using LangGraph
- Persistence: Used LangGraph `SqliteSaver` for persistent disk checkpointing (`chatbot_checkpoint.db`)
- UI: Interactive chat frontend built with Streamlit
- Streaming: Real-time token generation via `chatbot.stream` rendered with `st.write_stream`
- Resume chat: Continue prior conversations anytime by providing the same `thread_id`
- SQLite: Persistent file-based checkpointing across app restarts using `SqliteSaver`
