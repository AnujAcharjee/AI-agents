# Development Instructions

* **Only write code for the specific part you are asked to modify.**
* **Do not implement extra changes, refactor unrelated code, or add unnecessary improvements.**
* **Do not run the code or execute tests unless explicitly asked.**

## Project Context

* Before making any changes, **read `requirements.txt` first** to understand the project's dependencies and setup.
* **Do not read or inspect `.env`** under any circumstances.
* Use **`.env.example`** to understand the required environment variables and configuration.

## Models

* All models used by the project are defined in **`const.py`**.
* Always refer to `const.py` when you need to determine which models the project uses.
* Do not hardcode or introduce alternative model names unless explicitly requested.

## AI Stack

This project uses:

* **OpenAI API** as the API interface.
* **Gemini** as the LLM.
* **OpenRouter** for the embedding model.

When modifying AI-related code, follow the existing model configuration in `const.py` rather than introducing new model configurations.
