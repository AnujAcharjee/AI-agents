import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project directory to sys.path so client can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

from google.genai import types
from langchain_qdrant import QdrantVectorStore

from client.clients import gemini_client, openai_embedding_client

# Connect to Qdrant collection using the same embedding model
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=openai_embedding_client,
)

# Take user input
user_query = input("Ask something: ")

# Retrieve top 5 relevant chunks
search_results = vector_db.similarity_search(query=user_query, k=5)

# Format context safely (PyPDFLoader uses 'page', not 'page_label')
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
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
    ),
)

response_stream = chat.send_message_stream(user_query)

print("\n🤖: ", end="", flush=True)

for chunk in response_stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
print()

