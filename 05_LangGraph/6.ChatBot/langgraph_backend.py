import sqlite3
from pathlib import Path
from typing import TypedDict, Optional, Annotated, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessageChunk
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

class ChatState(TypedDict):

    # This messages mentis a list of all the conversation with the LLM
    # we used a special reducer func `add_messages` from Langgraph to append messages, its  and optimized with BaseMessage 
    # ! Default behavior of State is to delete the prev msg, that why we need this reducer  function
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatGoogleGenerativeAI(model='gemini-flash-lite-latest')

def chat_node(state: ChatState):

    # take user query state
    messages = state['messages']

    # send to llm
    response = llm.invoke(messages)

    # response store in state
    return {'messages': [response]}

# SQLite persistence (stored on disk in chatbot_checkpoint.db)
db_path = Path(__file__).parent / "chatbot_checkpoint.db"
conn = sqlite3.connect(db_path, check_same_thread=False) 
# sqlitthread safe, but langgraph is not, so we use check_same_thread=Falsee is 
checkpointer = SqliteSaver(conn)
checkpointer.setup()

graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)

# add edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

# def get_response(user_message: str, thread_id: str = '1') -> str:
#     """Send user message to LangGraph chatbot and return AI text response."""
#     config = {'configurable': {'thread_id': thread_id}}
#     response = chatbot.invoke({'messages': [HumanMessage(content=user_message)]}, config=config)
#     raw_content = response['messages'][-1].content
#     if isinstance(raw_content, list):
#         return ''.join(
#             part.get('text', '') if isinstance(part, dict) else str(part)
#             for part in raw_content
#         )
#     return str(raw_content)

def stream_response(user_message: str, thread_id: str = '1'):
    """Stream token chunks from LangGraph chatbot (Generator)."""
    config = {'configurable': {'thread_id': thread_id}}

    for message_chunk, metadata in chatbot.stream(
        {'messages': [HumanMessage(content=user_message)]}, 
        config=config, 
        stream_mode='messages'
    ):
        if isinstance(message_chunk, AIMessageChunk) and message_chunk.content:
            if isinstance(message_chunk.content, str):
                yield message_chunk.content
            elif isinstance(message_chunk.content, list):
                for part in message_chunk.content:
                    if isinstance(part, dict) and 'text' in part:
                        yield part['text']
                    elif isinstance(part, str):
                        yield part

# Alias so both names work
get_response = stream_response

def get_all_threads() -> list[str]:
    """Retrieve all saved thread_ids from the SQLite database."""
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY checkpoint_id DESC")
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except Exception:
        return []

def get_thread_messages(thread_id: str):
    """Retrieve all messages stored in SQLite for a given thread_id."""
    config = {'configurable': {'thread_id': thread_id}}
    state = chatbot.get_state(config)
    if state and state.values and 'messages' in state.values:
        return state.values['messages']
    return []

def delete_thread(thread_id: str):
    """Delete a thread and its checkpoints from the SQLite database."""
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        cur.execute("DELETE FROM writes WHERE thread_id = ?", (thread_id,))
        conn.commit()
    except Exception:
        pass