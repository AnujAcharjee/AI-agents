from dotenv import load_dotenv
from pathlib import Path
import os
from openai import OpenAI
from google import genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

# Add workspace root to sys.path so const can be imported
workspace_root = Path(__file__).resolve().parents[2]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from const import EMBEDDING_NEMOTRON, EMBEDDING_GEMINI

# Load .env from project directory or repository root
load_dotenv(workspace_root / ".env")
load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

# openai_client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=openrouter_api_key,
# )

openai_embedding_client = OpenAIEmbeddings(
    model=EMBEDDING_NEMOTRON,
    openai_api_base="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
    check_embedding_ctx_length=False,
    chunk_size=64,
)

gemini_client = genai.Client(
    api_key=google_api_key
)

# gemini_embedding_client = GoogleGenerativeAIEmbeddings(
#     model=EMBEDDING_GEMINI,
#     task_type="retrieval_document",
#     api_key=google_api_key,
# )
