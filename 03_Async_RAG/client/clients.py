from dotenv import load_dotenv
from pathlib import Path
import os
from openai import OpenAI
from google import genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

# Load .env from project directory or repository root
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

# openai_client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=openrouter_api_key,
# )

openai_embedding_client = OpenAIEmbeddings(
    model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
    openai_api_base="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
    check_embedding_ctx_length=False,
    chunk_size=64,
)

gemini_client = genai.Client(
    api_key=google_api_key
)

# gemini_embedding_client = GoogleGenerativeAIEmbeddings(
#     model="gemini-embedding-001",
#     task_type="retrieval_document",
#     api_key=google_api_key,
# )
