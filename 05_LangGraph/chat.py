import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.checkpoint.mongodb import MongoDBSaver

# Load environment variables
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
load_dotenv()

# Add workspace root to sys.path so const can be imported from anywhere
workspace_root = Path(__file__).resolve().parents[1]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from const import GEMINI_FLASH_LITE

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# Gemini chat model via LangChain
llm = ChatGoogleGenerativeAI(
    model=GEMINI_FLASH_LITE,
    google_api_key=api_key,
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    print("\n" + "-" * 50)
    print(" [Node: chatbot] Calling Gemini model...")
    response = llm.invoke(state.get("messages"))
    print(" [Node: chatbot] Response received.")
    return {"messages": [response]}


def samplenode(state: State):
    print("\n" + "-" * 50)
    print(" [Node: samplenode] Running post-processing node...")
    return {"messages": ["Sample Message Appended"]}


# Build Graph
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", samplenode)

# Edges: START -> chatbot -> samplenode -> END
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "samplenode")
graph_builder.add_edge("samplenode", END)

graph = graph_builder.compile()

# Execute Graph
input_message = "Who is the GOAT of football?"

print("\n" + "=" * 60)
print("             STARTING LANGGRAPH EXECUTION")
print("=" * 60)
print(f"User Prompt: {input_message}")

updated_state = graph.invoke(State({"messages": [input_message]}))



# Pretty Print Final Results
print("\n" + "=" * 60)
print("               UPDATED GRAPH STATE")
print("=" * 60)

for idx, msg in enumerate(updated_state.get("messages", []), 1):
    role = getattr(msg, "type", "message").upper()
    content = msg.content
    
    # Handle list-based content structures from Gemini
    if isinstance(content, list):
        content = "".join(
            part.get("text", str(part)) if isinstance(part, dict) else str(part)
            for part in content
        )

    print(f"\n[{idx}] {role}:")
    print(f"{content.strip()}\n")
    print("-" * 60)

print("\nExecution complete.\n")