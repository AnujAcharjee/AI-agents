# Conditional Edges and Smart routing
# Have an Evaluator who evaluates the response from an LLM
# if True (Good): END / if False (Not good): try with an advanced model

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from typing import Optional, Literal
from typing_extensions import TypedDict

from openai import OpenAI
from langgraph.graph import StateGraph, START, END

# Add workspace root to sys.path so const can be imported from anywhere
workspace_root = Path(__file__).resolve().parents[1]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from const import GEMINI_FLASH_LITE, GEMINI_3_5_FLASH_LITE

load_dotenv(workspace_root / ".env")
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=api_key,
)

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]


def chatbot_low(state: State):
    print("\n[Node: chatbot_low] Generating initial answer...")
    response = client.chat.completions.create(
        model=GEMINI_FLASH_LITE,
        messages=[
            {"role": "user", "content": state.get("user_query")}
        ]
    )

    state["llm_output"] = response.choices[0].message.content
    return state


def evalute_response(state: State) -> Literal["chatbot_advance", "endnode"]:
    print("\n[Router: evalute_response] Asking AI model to evaluate answer...")
    
    eval_prompt = f"""
    You are an evaluator. Determine if the answer is accurate and answers the question.
    
    Question: {state.get("user_query")}
    Answer: {state.get("llm_output")}

    Respond with ONLY 'YES' if the answer is good, or 'NO' if it needs improvement.
    """

    response = client.chat.completions.create(
        model=GEMINI_FLASH_LITE,
        messages=[
            {"role": "user", "content": eval_prompt}
        ]
    )

    decision = response.choices[0].message.content.strip().upper()
    print(f"[Router: evalute_response] AI Evaluator decision: {decision}")

    if "YES" in decision:
        return "endnode"

    return "chatbot_advance"


def chatbot_advance(state: State):
    print("\n[Node: chatbot_advance] Regenerating with advanced model...")
    response = client.chat.completions.create(
        model=GEMINI_3_5_FLASH_LITE,
        messages=[
            {"role": "user", "content": f"Provide an accurate and complete answer to: {state.get('user_query')}"}
        ]
    )

    state["llm_output"] = response.choices[0].message.content
    return state


def endnode(state: State):
    print("\n[Node: endnode] Finalizing output.")
    return state
    

# Build Graph
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot_low", chatbot_low)
graph_builder.add_node("chatbot_advance", chatbot_advance)
graph_builder.add_node("endnode", endnode)

# Flow: START -> chatbot_low -> (conditional edge: evalute_response) -> endnode OR chatbot_advance -> endnode -> END
graph_builder.add_edge(START, "chatbot_low")
graph_builder.add_conditional_edges("chatbot_low", evalute_response)

graph_builder.add_edge("chatbot_advance", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile()

# Run with a test query
updated_state = graph.invoke(State({"user_query": "Who is the GOAT of soccer, one person only?"}))

print("\n--- Result ---")
print(updated_state)
