import os
import sys
from pathlib import Path
import warnings
from dotenv import load_dotenv
from openai import OpenAI
from mem0 import Memory

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["MEM0_TELEMETRY"] = "False"
warnings.filterwarnings("ignore")

# Add workspace root to sys.path so const can be imported
workspace_root = Path(__file__).resolve().parents[1]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from const import (
    GEMINI_3_5_FLASH_LITE,
    GEMINI_FLASH_LITE,
    EMBEDDING_GEMINI,
    EMBEDDING_NEMOTRON,
)

# Load environment variables (.env at repository root)
load_dotenv(workspace_root / ".env")
load_dotenv()

# =====================================================================
# Mem0 Configuration
# =====================================================================
# Embedder: OpenRouter (Nemotron, output dimension: 2048)
# LLM: Google Gemini
# Vector Store: Qdrant
# Graph Store: Neo4j
# =====================================================================
config = {
    "version": "v1.1",
    "llm": {
        "provider": "gemini",
        "config": {
            "model": GEMINI_3_5_FLASH_LITE,
            "temperature": 0.2,
            "api_key": os.getenv("GOOGLE_API_KEY"),
        },
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": EMBEDDING_NEMOTRON,
            "openai_base_url": "https://openrouter.ai/api/v1",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "embedding_dims": 2048,
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "agent_memory",
            "embedding_model_dims": 2048,
            # Tip: If you don't have a Qdrant server running, you can use local disk mode:
            # "path": str(Path(__file__).resolve().parent / "local_qdrant"),
        },
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": os.getenv("NEO4J_URI"),
            "username": os.getenv("NEO4J_USERNAME", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD"),
            "database": os.getenv("NEO4J_DATABASE", "neo4j"),
        },
    },
}

openai_client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


def get_memory(custom_config=None) -> Memory:
    """Initialize and return a Mem0 Memory instance."""
    return Memory.from_config(custom_config or config)


if __name__ == "__main__":
    try:
        memory = get_memory()

        user_id = "anuj"

        while True:
            user_query = input("\n> ").strip()
            if not user_query:
                continue
            if user_query.lower() in ("exit", "quit"):
                break

            # 1. Retrieve relevant memories for the user query
            search_results = memory.search(query=user_query, filters={"user_id": user_id})
            memories = [m["memory"] for m in search_results.get("results", []) if "memory" in m]

            print("Found Memories: ", memories)

            # 2. Build system prompt including retrieved memories as context
            system_prompt = "You are a helpful assistant."
            if memories:
                memory_context = "\n".join(f"- {m}" for m in memories)
                system_prompt += f"\n\nContext from past memories:\n{memory_context}"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ]

            # 3. Generate response using Gemini
            response = openai_client.chat.completions.create(
                model=GEMINI_3_5_FLASH_LITE,
                messages=messages,
            )

            ai_response = response.choices[0].message.content
            print(f"\n🤖: {ai_response}")

            # 4. Store conversation in memory
            memory.add(
                messages=[
                    {"role": "user", "content": user_query},
                    {"role": "assistant", "content": ai_response},
                ],
                user_id=user_id,
            )

    except Exception as e:
        print(f"\nError initializing Memory: {e}")
        print("\nNote: Ensure your Qdrant container is running:")
        print("  docker run -p 6333:6333 qdrant/qdrant")
        print("Or switch vector_store to local path mode: 'path': './local_qdrant'")