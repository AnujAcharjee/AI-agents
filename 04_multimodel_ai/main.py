import os
import sys
import base64
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

import mimetypes

# Add workspace root to sys.path so const can be imported from anywhere
workspace_root = Path(__file__).resolve().parents[1]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from openai import OpenAI
from const import GEMINI_FLASH_LITE

# Set standard output encoding to UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# OpenAI client configured with Google Gemini OpenAI-compatible endpoint
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=api_key,
)


def image_to_data_url(source) -> str:
    """Converts a local file path or web URL into a base64 data URL for Gemini."""
    path_or_str = str(source)
    if path_or_str.startswith("data:"):
        return path_or_str

    if path_or_str.startswith("http://") or path_or_str.startswith("https://"):
        req = urllib.request.Request(path_or_str, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            mime_type = resp.headers.get_content_type() or "image/jpeg"
    else:
        file_path = Path(source)
        with open(file_path, "rb") as f:
            data = f.read()
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "image/jpeg"

    # Ensure clean MIME type without charset
    mime_type = mime_type.split(";")[0].strip()

    b64_str = base64.b64encode(data).decode("utf-8")
    return f"data:{mime_type};base64,{b64_str}"


def main():
    image_dir = Path(__file__).resolve().parent / "image"
    valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    image_files = [f for f in image_dir.iterdir() if f.suffix.lower() in valid_exts] if image_dir.exists() else []

    if not image_files:
        print(f"No images found in: {image_dir}")
        return

    print(f"Found {len(image_files)} image(s) in {image_dir.name}/ folder:")

    for img_path in image_files:
        print(f"\nProcessing: {img_path.name}")
        image_data_uri = image_to_data_url(img_path)

        response = client.chat.completions.create(
            model=GEMINI_FLASH_LITE,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Generate a caption for this image in about 50 words."},
                        {"type": "image_url", "image_url": {"url": image_data_uri}},
                    ],
                }
            ],
        )

        if response.choices:
            print("Response:\n", response.choices[0].message.content)
        else:
            print("Response: ", response)


if __name__ == "__main__":
    main()