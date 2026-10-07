import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import requests
from pydantic import BaseModel, Field
from typing import Optional

workspace_root = Path(__file__).resolve().parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from const import GEMINI_3_7_FLASH

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

SYSTEM_PROMPT = """
    You are an expert AI assistant in resolving user queries.

    You work on START, PLAN, TOOL, OBSERVE and OUTPUT steps.

    You need to first understand the user's request in START.

    Then use PLAN steps to determine what needs to be done.

    If a tool is required, use the TOOL step.

    After every TOOL step, wait for the OBSERVE step containing the tool output.

    Once enough planning is complete, provide the final answer using OUTPUT.

    Rules:

    - Strictly follow the given JSON output format.

    - Only run one step at a time.

    - The sequence is START → PLAN → TOOL → OBSERVE → PLAN → OUTPUT.

    - PLAN can occur multiple times.

    - TOOL is only used when a tool is required.

    - Never invent tool results.

    Output JSON Format:

    {"step": "START" | "PLAN" | "TOOL" | "OUTPUT", "content": "string", "tool": "string", "input": "string"}

    Available Tools:

    - get_weather(city: str): Takes a city name as input and returns weather information.

    - run_command(cmd: str): Executes a Windows PowerShell command on the user's system.

    Example 1:

    START: Hey, can you solve 2 + 3 * 5 / 10?

    PLAN: {"step": "PLAN", "content": "Identify the task as a math problem."}

    PLAN: {"step": "PLAN", "content": "Apply BODMAS to determine the order of operations."}

    PLAN: {"step": "PLAN", "content": "Calculate 3 * 5 = 15."}

    PLAN: {"step": "PLAN", "content": "Calculate 15 / 10 = 1.5."}

    PLAN: {"step": "PLAN", "content": "Calculate 2 + 1.5 = 3.5."}

    OUTPUT: {"step": "OUTPUT", "content": "3.5"}

    Example 2:

    START: What is the weather of Delhi?

    PLAN: {"step": "PLAN", "content": "Identify that the user is asking for the current weather in Delhi."}

    PLAN: {"step": "PLAN", "content": "Use the get_weather tool with Delhi as the city."}

    TOOL: {"step": "TOOL", "content": "Calling get_weather.", "tool": "get_weather", "input": "Delhi"}

    After the tool returns:

    PLAN: {"step": "PLAN", "content": "Use the weather information returned by the tool to prepare the final response."}

    OUTPUT: {"step": "OUTPUT", "content": "The weather in Delhi is currently sunny and 32°C."}

"""


# For structured output - using pydantic
class MyOutputFormat(BaseModel):

    step: str = Field(
        ...,
        description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc"
    )

    content: Optional[str] = Field(
        None,
        description="The optional string content for the step"
    )

    tool: Optional[str] = Field(
        None,
        description="The ID of the tool to call."
    )

    input: Optional[str] = Field(
        None,
        description="The input params for the tool"
    )


# My agent Tools
def get_weather(city: str):

    url = f"https://wttr.in/{city.lower()}?format=%C+%t"

    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"

    return "Weather API error"


def run_command(cmd: str):

    result = os.system(cmd)

    return result


available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}


def main():

    # Conversation history is created once
    # so the agent remembers previous conversations.
    message_history = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Infinite chat loop
    while True:

        try:
            user_query = input("👉 ").strip()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

        if not user_query:
            continue

        # Allow the user to exit the chat
        if user_query.lower() in {"exit", "quit", "bye"}:
            print("👋 Goodbye!")
            break

        # Add the new user message to the existing conversation
        message_history.append(
            {
                "role": "user",
                "content": user_query
            }
        )

        # Agent execution loop
        for _ in range(10):

            response = client.chat.completions.parse(
                model=GEMINI_3_7_FLASH,
                response_format=MyOutputFormat,
                messages=message_history,
            )

            raw_result = response.choices[0].message.content

            # try:
            #     parsed_result = json.loads(raw_result)
            # except json.JSONDecodeError as error:
            #     raise RuntimeError("The model returned invalid JSON.") from error

            parsed_result = response.choices[0].message.parsed

            if parsed_result is None:
                raise RuntimeError(
                    "The model did not return a structured response."
                )

            step = parsed_result.step
            content = parsed_result.content

            if step not in {"START", "PLAN", "TOOL", "OUTPUT"}:
                raise RuntimeError(
                    "The model returned an invalid step."
                )

            message_history.append(
                {
                    "role": "assistant",
                    "content": raw_result
                }
            )

            if step == "START":

                print("🔥", content)
                # Explicitly demand the PLAN step
                message_history.append(
                    {
                        "role": "user",
                        "content": "Now execute the PLAN step."
                    }
                )
                continue

            if step == "PLAN":

                print("🧠", content)
                # Explicitly allow the model to decide the next step
                message_history.append(
                    {
                        "role": "user",
                        "content": "Continue to the next required step."
                    }
                )
                continue

            if step == "TOOL":

                tool_to_call = parsed_result.tool
                tool_input = parsed_result.input

                print(f"🛠️ {tool_to_call} ({tool_input})")

                if not tool_to_call:
                    raise RuntimeError(
                        "No tool was specified."
                    )

                if not tool_input:
                    raise RuntimeError(
                        "No tool input was specified."
                    )

                if tool_to_call not in available_tools:
                    raise RuntimeError(
                        f"Unknown tool: {tool_to_call}"
                    )

                tool_response = available_tools[tool_to_call](
                    tool_input
                )

                print("👀", tool_response)
                message_history.append(
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "step": "OBSERVE",
                                "tool": tool_to_call,
                                "input": tool_input,
                                "output": tool_response,
                            }
                        ),
                    }
                )
                continue

            if step == "OUTPUT":
                print("🤖", content)
                break

        else:
            raise RuntimeError(
                "The model did not return an OUTPUT step after 10 responses."
            )


main()