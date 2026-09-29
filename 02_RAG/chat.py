import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore


load_dotenv()

gemini_client = genai.Client()

# Vector Embeddings
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", task_type="retrieval_document"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model,
)

# Take user input
user_query = input("Ask something: ")

# Retrieve top 4 relevant chunks
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


# Stream response using official Google GenAI SDK
response_stream = gemini_client.interactions.create(
    model="gemini-3.7-flash",
    input=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ],
    stream=True,
)

print("\n🤖: ", end="", flush=True)

for event in response_stream:
    print(event)
