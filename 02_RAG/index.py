import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from pydantic import SecretStr


# Load environment variables
load_dotenv()


# ============================================================
# Google API Key
# ============================================================

google_api_key: str | None = os.getenv("GOOGLE_API_KEY")

if google_api_key is None or not google_api_key.strip():
    raise EnvironmentError("GOOGLE_API_KEY not found")

google_api_key_secret = SecretStr(google_api_key)


# ============================================================
# PDF Path
# ============================================================

pdf_path: Path = Path(__file__).resolve().parent / "nodejs.pdf"

if not pdf_path.is_file():
    raise FileNotFoundError(f"PDF not found at: {pdf_path}")


# ============================================================
# Load PDF
# ============================================================

loader = PyPDFLoader(file_path=str(pdf_path))
docs = loader.load()


# ============================================================
# Split Documents
# ============================================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400,
)

chunks = text_splitter.split_documents(docs)

print(f"PDF pages: {len(docs)}")
print(f"Total chunks: {len(chunks)}")


# ============================================================
# Google Embedding Model
# ============================================================

embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    task_type="retrieval_document",
    api_key=google_api_key_secret,
)


# ============================================================
# Rate-Limited Embedding
# ============================================================

BATCH_SIZE = 20
DELAY_BETWEEN_BATCHES = 2
MAX_RETRIES = 5


def embed_chunks_with_rate_limit(chunks):
    """
    Embed documents in controlled batches.

    Includes:
    - Small batches
    - Delay between batches
    - Automatic retry for 429 quota errors
    - Exponential backoff
    """

    all_embeddings = []

    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_number, start in enumerate(
        range(0, len(chunks), BATCH_SIZE),
        start=1,
    ):
        batch = chunks[start:start + BATCH_SIZE]

        print(
            f"Embedding batch {batch_number}/{total_batches} "
            f"({len(batch)} chunks)..."
        )

        for attempt in range(MAX_RETRIES):
            try:
                embeddings = embedding_model.embed_documents(
                    [doc.page_content for doc in batch]
                )

                all_embeddings.extend(embeddings)

                print(
                    f"  ✓ Batch {batch_number}/{total_batches} completed"
                )

                break

            except Exception as error:
                error_text = str(error)

                if "429" not in error_text and "RESOURCE_EXHAUSTED" not in error_text:
                    raise

                if attempt == MAX_RETRIES - 1:
                    raise

                wait_time = min(60, 2 ** attempt * 5)

                print(
                    f"  ⚠ Rate limit reached. "
                    f"Retrying in {wait_time}s..."
                )

                time.sleep(wait_time)

        # Give Google's quota window some breathing room
        if batch_number < total_batches:
            print(
                f"  Waiting {DELAY_BETWEEN_BATCHES}s before next batch..."
            )
            time.sleep(DELAY_BETWEEN_BATCHES)

    return all_embeddings


# ============================================================
# Generate Embeddings
# ============================================================

print("\nStarting embedding process...\n")

embeddings = embed_chunks_with_rate_limit(chunks)

print(f"\nSuccessfully generated {len(embeddings)} embeddings.")


# ============================================================
# Store Embeddings in Qdrant
# ============================================================

print("\nConnecting to Qdrant...")

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning_rag",
    batch_size=BATCH_SIZE,
)


# ============================================================
# Success
# ============================================================

print(
    f"\nSuccessfully indexed {len(chunks)} "
    "chunks into Qdrant collection 'learning_rag'."
)
