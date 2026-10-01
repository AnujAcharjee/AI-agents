import sys
from pathlib import Path

# Add project root to sys.path so utils can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from utils.clients import openai_embedding_client

# Get PDF path
pdf_path: Path = Path(__file__).resolve().parent / "nodejs.pdf"
if not pdf_path.is_file():
    raise FileNotFoundError(f"PDF not found at: {pdf_path}")

# Load PDF 
loader = PyPDFLoader(file_path=str(pdf_path))
docs = loader.load()

# Split Documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400,
)

chunks = text_splitter.split_documents(docs)

print(f"PDF pages: {len(docs)}")
print(f"Total chunks: {len(chunks)}")


# Store Embeddings in Qdrant

print("\nConnecting to Qdrant and generating embeddings...")

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=openai_embedding_client,
    url="http://localhost:6333",
    collection_name="learning_rag",
    # force_recreate=True,
)

print(
    f"\nSuccessfully indexed {len(chunks)} "
    "chunks into Qdrant collection 'learning_rag'."
)

