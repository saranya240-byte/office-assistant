import json
from pathlib import Path

from google import genai

from app.utils.config import GEMINI_API_KEY, GEMINI_MODEL


PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "response_prompt.txt"
)

with open(PROMPT_PATH, "r", encoding="utf-8") as file:
    RESPONSE_PROMPT = file.read()


client = genai.Client(api_key=GEMINI_API_KEY)


def generate_response(result: dict) -> str:
    """
    Convert structured tool/RAG output into a
    clear employee-facing response.
    """

    if not result:
        return "I could not find enough information to answer your request."

    prompt = f"""
{RESPONSE_PROMPT}

Here is the structured result produced by the Office Assistant:

{json.dumps(result, indent=2, default=str)}

Generate the final response for the employee.
Return only the employee-facing answer.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        if response.text:
            return response.text.strip()

        return "I could not generate a response from the available information."

    except Exception as exc:
        return f"Unable to generate the response: {exc}"