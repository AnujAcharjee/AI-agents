# Checkpointing with MongoDB in LangGraph
# Stores conversation state in MongoDB so the agent remembers context across turns.

import os
import sys
import warnings
from pathlib import Path
from dotenv import load_dotenv

from typing import Annotated
from typing_extensions import TypedDict
from pymongo import MongoClient

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_google_genai import ChatGoogleGenerativeAI

warnings.filterwarnings("ignore")

# Add workspace root to sys.path so const can be imported
workspace_root = Path(__file__).resolve().parents[1]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from const import GEMINI_FLASH_LITE

load_dotenv(workspace_root / ".env")
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# 1. Setup Model
llm = ChatGoogleGenerativeAI(
    model=GEMINI_FLASH_LITE,
    google_api_key=api_key,
)

# 2. Define State
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 3. Define Node
def chatbot(state: State):
    response = llm.invoke(state.get("messages"))
    return {"messages": [response]}


# 4. Build Graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


# 5. Connect to MongoDB and create Checkpointer
mongodb_client = MongoClient("mongodb://admin:admin@localhost:27017/")
checkpointer = MongoDBSaver(mongodb_client)

# Compile graph with the MongoDB checkpointer
graph = graph_builder.compile(checkpointer)


def print_response(message):
    content = message.content
    if isinstance(content, list):
        content = "".join(p.get("text", str(p)) if isinstance(p, dict) else str(p) for p in content)
    print(f"Bot:  {str(content).strip()}\n")



# thread_id identifies a specific conversation/user session
config = {"configurable": {
    "thread_id": "session_1" # user_id
    }}

# query = "Hi, my name is Alex and I live in Tokyo."
query = "What is my name and where do I live?"

for chunk in graph.stream(
    State({"messages": [query]}),
    config,
    stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()