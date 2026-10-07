import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root (AI) and app directory (03_Async_RAG) to sys.path
queues_dir = Path(__file__).resolve().parent
app_dir = queues_dir.parent
workspace_root = app_dir.parent

for p in (workspace_root, app_dir):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from const import GEMINI_3_5_FLASH_LITE
from google.genai import types
from langchain_qdrant import QdrantVectorStore

from client.clients import gemini_client, openai_embedding_client

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=openai_embedding_client,
)

def process_query(user_query: str):
    print("Searching Chunks", user_query)
    search_results = vector_db.similarity_search(query=user_query, k=5)

    context_blocks = []
    for result in search_results:
        page_index = result.metadata.get("page", 0)
        source = result.metadata.get("source", "Unknown")
        context_blocks.append(
            f"Page Content: {result.page_content}\n"
            f"Page Number: {page_index + 1}\n"
            f"File Location: {source}"
        )
    
    context = "\n\n---\n\n".join(context_blocks)

    SYSTEM_PROMPT = f"""
    You are a helpful AI Assistant who answers user queries based solely on the available context retrieved from a PDF file.
    Always provide clear answers and cite the exact page number so the user can open the PDF and read further.
    Context:
    {context}
    """

    # Stream response using official Google GenAI Chat SDK
    chat = gemini_client.chats.create(
        model=GEMINI_3_5_FLASH_LITE,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
    )

    response_stream = chat.send_message_stream(user_query)

    print("\n🤖: ", end="", flush=True)

    full_response = []
    for chunk in response_stream:
        if chunk.text:
            print(chunk.text, end="", flush=True)
            full_response.append(chunk.text)
    print()
    return "".join(full_response)


if __name__ == "__main__":
    from rq import SimpleWorker
    from client.rq_client import redis_conn, queue

    print("🚀 Starting RQ Worker on queue 'default' (Windows SimpleWorker)...")
    worker = SimpleWorker([queue], connection=redis_conn)
    worker.work()
