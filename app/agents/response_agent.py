from pathlib import Path
import json
import ollama

from app.utils.config import OLLAMA_MODEL


BASE_PATH = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_PATH / "prompts" / "response_prompt.txt"


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_response(result: dict, query: str = "") -> str:
    """
    Convert a structured tool/RAG result into a concise
    employee-facing response using Ollama.

    The original query is used for simple employee-information
    questions so that the response contains only the requested
    information.
    """

    # ---------------------------------------------------------
    # Handle failed results first
    # ---------------------------------------------------------

    if not result.get("success", True):
        return result.get(
            "message",
            "The request could not be processed.",
        )

    # ---------------------------------------------------------
    # Deterministic employee-information responses
    # ---------------------------------------------------------

    normalized_query = query.strip().lower()

    if "manager" in normalized_query and "manager" in result:
        return f"Your manager is {result['manager']}."

    if "name" in normalized_query and "name" in result:
        return f"Your name is {result['name']}."

    if "department" in normalized_query and "department" in result:
        return f"You work in the {result['department']} department."

    if "designation" in normalized_query and "designation" in result:
        return f"Your designation is {result['designation']}."

    if "location" in normalized_query and "location" in result:
        return f"Your office location is {result['location']}."

    # ---------------------------------------------------------
    # Leave balance
    # ---------------------------------------------------------

    if (
        "casual_leave" in result
        or "earned_leave" in result
        or "sick_leave" in result
    ):
        return format_leave_balance(result)

    # ---------------------------------------------------------
    # Leave request
    # ---------------------------------------------------------

    if "request_id" in result and "leave_type" in result:
        if "message" in result:
            return result["message"]

        return (
            f"Leave request {result['request_id']} is "
            f"{result.get('status', 'processed')}."
        )

    # ---------------------------------------------------------
    # Employee information
    # ---------------------------------------------------------

    if (
        "name" in result
        and "department" in result
        and "designation" in result
    ):
        return format_employee_information(result)

    # ---------------------------------------------------------
    # For policy/RAG and other complex results, use Ollama
    # ---------------------------------------------------------

    prompt_template = load_prompt()

    result_json = json.dumps(
        result,
        indent=2,
        default=str,
    )

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": prompt_template,
            },
            {
                "role": "user",
                "content": (
                    "Convert the following structured result "
                    "into the final employee-facing answer.\n\n"
                    "IMPORTANT:\n"
                    "- Return ONLY the natural-language answer.\n"
                    "- Do NOT return JSON.\n"
                    "- Use ONLY the information in the structured result.\n\n"
                    f"Structured result:\n{result_json}"
                ),
            },
        ],
    )

    answer = response["message"]["content"].strip()

    # ---------------------------------------------------------
    # Safety check:
    # If Ollama returns JSON, convert it to readable text.
    # ---------------------------------------------------------

    if answer.startswith("{") and answer.endswith("}"):
        try:
            parsed = json.loads(answer)

            if isinstance(parsed, dict):
                return format_structured_result(parsed)

        except json.JSONDecodeError:
            pass

    return answer


def format_leave_balance(result: dict) -> str:
    """
    Format leave balance information.
    """

    lines = ["Leave balance:"]

    if "casual_leave" in result:
        lines.append(
            f"- Casual Leave: {result['casual_leave']} days"
        )

    if "earned_leave" in result:
        lines.append(
            f"- Earned Leave: {result['earned_leave']} days"
        )

    if "sick_leave" in result:
        lines.append(
            f"- Sick Leave: {result['sick_leave']} days"
        )

    if "wfh_days_used" in result:
        lines.append(
            f"- WFH days used: {result['wfh_days_used']}"
        )

    return "\n".join(lines)


def format_employee_information(result: dict) -> str:
    """
    Format a complete employee profile.
    """

    return (
        f"Employee: {result['name']}\n"
        f"Department: {result['department']}\n"
        f"Designation: {result['designation']}\n"
        f"Manager: {result.get('manager', 'N/A')}\n"
        f"Location: {result.get('location', 'N/A')}"
    )


def format_structured_result(result: dict) -> str:
    """
    Fallback formatter for cases where the LLM returns
    structured JSON instead of natural language.
    """

    if not result.get("success", True):
        return result.get(
            "message",
            "The request could not be processed.",
        )

    # ---------------------------------------------------------
    # Leave balance
    # ---------------------------------------------------------

    if (
        "casual_leave" in result
        or "earned_leave" in result
        or "sick_leave" in result
    ):
        return format_leave_balance(result)

    # ---------------------------------------------------------
    # Leave request
    # ---------------------------------------------------------

    if "request_id" in result and "leave_type" in result:
        if "message" in result:
            return result["message"]

        return (
            f"Leave request {result['request_id']} is "
            f"{result.get('status', 'processed')}."
        )

    # ---------------------------------------------------------
    # Employee information
    # ---------------------------------------------------------

    if (
        "name" in result
        and "department" in result
        and "designation" in result
    ):
        return format_employee_information(result)

    # ---------------------------------------------------------
    # Generic result
    # ---------------------------------------------------------

    if "message" in result:
        return str(result["message"])

    return "The request was processed successfully."