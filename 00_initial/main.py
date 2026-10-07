import sys
from pathlib import Path
from dotenv import load_dotenv
import os
from importlib import import_module
import json

# Add workspace root to sys.path so const can be imported
workspace_root = Path(__file__).resolve().parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from const import GEMINI_3_6_FLASH

# from google import genai
from openai import OpenAI

# Prompt files are numbered for lesson order, so import them dynamically: a
# module name that begins with a digit cannot be used in a normal ``from`` import.
SYSTEM_PROMPT = import_module("prompts.03_cot").SYSTEM_PROMPT

load_dotenv()

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# interaction = client.interactions.create(
#     model="gemini-3.6-flash",
#     input="Explain how AI works in a few words"
# )
# print(interaction.output_text)


client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

print("\n\n\n")

message_history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    },
]

user_query = input("👉 ").strip()
if not user_query:
    print("No input provided. Exiting.")
    exit()

message_history.append({"role": "user", "content": user_query})

for _ in range(3):
    response = client.chat.completions.create(
        model=GEMINI_3_6_FLASH,
        response_format={"type": "json_object"},
        messages=message_history,
    )

    raw_result = response.choices[0].message.content
    try:
        parsed_result = json.loads(raw_result)
    except json.JSONDecodeError as error:
        raise RuntimeError("The model returned invalid JSON.") from error

    step = parsed_result.get("step")
    content = parsed_result.get("content")
    if step not in {"START", "PLAN", "OUTPUT"} or not isinstance(content, str):
        raise RuntimeError("The model returned an invalid response format.")

    # Preserve each result so the next request progresses to the next step.
    message_history.append({"role": "assistant", "content": raw_result})

    if step == "START":
        print("🔥 ", content)
        # Explicitly demand the PLAN step
        message_history.append({"role": "user", "content": "Now execute the PLAN step."})
        continue

    if step == "PLAN":
        print("🧠 ", content)
        # Explicitly demand the OUTPUT step
        message_history.append({"role": "user", "content": "Now execute the OUTPUT step."})
        continue

    if step == "OUTPUT":
        print("🤖 ", content)
        break
else:
    raise RuntimeError("The model did not return an OUTPUT step after three responses.")

print("\n\n\n")
