import sys
import uuid
from pathlib import Path

# Ensure backend directory is in sys.path regardless of execution folder
sys.path.append(str(Path(__file__).parent))

import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import (
    chatbot,
    get_response,
    stream_response,
    get_all_threads,
    get_thread_messages,
    delete_thread,
)

st.set_page_config(page_title="LangGraph ChatBot", page_icon="🤖", layout="centered")
st.title("🤖 LangGraph ChatBot")


def load_thread_chat(tid: str) -> list[dict]:
    """Load and format messages from SQLite checkpointer for a given thread_id."""
    raw_msgs = get_thread_messages(tid)
    formatted = []
    for m in raw_msgs:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        content = m.content
        if isinstance(content, list):
            text = "".join(
                p.get("text", "") if isinstance(p, dict) else str(p) for p in content
            )
        else:
            text = str(content)
        formatted.append({"role": role, "content": text})
    return formatted


# Initialize conversations from SQLite database
if "chats" not in st.session_state:
    st.session_state.chats = {}
    saved_threads = get_all_threads()
    if saved_threads:
        for tid in saved_threads:
            st.session_state.chats[tid] = load_thread_chat(tid)
        st.session_state.current_thread_id = saved_threads[0]
    else:
        initial_id = f"thread_{uuid.uuid4().hex[:6]}"
        st.session_state.chats[initial_id] = []
        st.session_state.current_thread_id = initial_id

if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = list(st.session_state.chats.keys())[0]

# Sidebar for session/chat management
with st.sidebar:
    st.header("Conversations (SQLite)")

    if st.button("➕ New Chat", use_container_width=True):
        new_id = f"thread_{uuid.uuid4().hex[:6]}"
        st.session_state.chats[new_id] = []
        st.session_state.current_thread_id = new_id
        st.rerun()

    st.divider()

    # List of all active thread IDs
    thread_ids = list(st.session_state.chats.keys())

    # Format thread label with preview of first user message
    def format_thread_label(tid: str) -> str:
        messages = st.session_state.chats.get(tid, [])
        if messages:
            first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
            snippet = first_user_msg[:20] + "..." if len(first_user_msg) > 20 else first_user_msg
            return f"💬 {snippet} ({tid})"
        return f"💬 New Chat ({tid})"

    selected_thread = st.radio(
        "Past Chats:",
        options=thread_ids,
        index=thread_ids.index(st.session_state.current_thread_id) if st.session_state.current_thread_id in thread_ids else 0,
        format_func=format_thread_label
    )

    if selected_thread != st.session_state.current_thread_id:
        st.session_state.current_thread_id = selected_thread
        st.rerun()

    st.divider()
    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        tid = st.session_state.current_thread_id
        delete_thread(tid)
        st.session_state.chats[tid] = []
        st.rerun()

# Get messages for active thread
current_messages = st.session_state.chats[st.session_state.current_thread_id]

# Display conversation history for the selected thread
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message here..."):
    # Append and render user message
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call LangGraph backend with streaming using SQLite persistence
    with st.chat_message("assistant"):
        ai_text = st.write_stream(
            stream_response(prompt, thread_id=st.session_state.current_thread_id)
        )

    # Append assistant response to current thread history
    current_messages.append({"role": "assistant", "content": ai_text})
