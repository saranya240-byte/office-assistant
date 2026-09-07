import json
from pathlib import Path

from ollama import Client

from app.utils.config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
)


PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "response_prompt.txt"
)


with open(PROMPT_PATH, "r", encoding="utf-8") as file:
    RESPONSE_PROMPT = file.read()


client = Client(host=OLLAMA_HOST)


def _format_citations(citations: list) -> str:
    """
    Deterministically format policy citations so the employee
    always sees a reference, regardless of what the LLM writes
    in the free-text answer.
    """

    lines = []
    seen = set()

    for citation in citations:

        source = citation.get("source", "Unknown")
        page = citation.get("page", "Unknown")
        key = (source, page)

        if key in seen:
            continue

        seen.add(key)
        lines.append(f"- {source} (Page {page})")

    return "\n".join(lines)


def generate_response(result: dict) -> str:

    if not result:
        return "I could not find enough information to answer your request."

    # ---------------------------------------------------------
    # Failed result
    # ---------------------------------------------------------

    if not result.get("success", False):
        return result.get(
            "message",
            "I could not complete your request.",
        )

    # ---------------------------------------------------------
    # Policy (RAG) results
    #
    # Previously this fell through to the generic "Other results"
    # branch below, which dumped the ENTIRE results list (raw
    # chunk text, scores, everything) into the prompt and relied
    # on the LLM to remember to cite its source. Now we build a
    # tighter context from the top chunks and always append a
    # deterministic citation block, so citations never depend on
    # the LLM behaving.
    # ---------------------------------------------------------

    if "citations" in result and "results" in result:

        top_results = result["results"][:4]

        context = "\n\n".join(
            f"[{item.get('source', 'Unknown')}, "
            f"Page {item.get('page', 'Unknown')}]\n"
            f"{item.get('text', '')}"
            for item in top_results
        )

        prompt = f"""
{RESPONSE_PROMPT}

Employee question:

{result.get('query', '')}

Relevant policy context:

{context}

IMPORTANT RULES:

1. Use ONLY the policy context above.
2. Do not invent information that is not present in the context.
3. Be concise and clear.
4. Do not mention Ollama, Python, or internal agents.
5. Do not add citations yourself — they are appended separately.
"""

        try:

            response = client.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            answer = response["message"]["content"].strip()

        except Exception as exc:

            answer = f"Unable to generate response: {exc}"

        citation_text = _format_citations(result.get("citations", []))

        if citation_text:
            return f"{answer}\n\nSource(s):\n{citation_text}"

        return answer

    # ---------------------------------------------------------
    # Office
    # ---------------------------------------------------------

    if "office_id" in result:

        return (
            f"Your office is located in {result['location']} "
            f"at {result['address']}. "
            f"Working hours are {result['working_hours']} "
            f"from {result['working_days']}."
        )

    # ---------------------------------------------------------
    # IT Assets
    # ---------------------------------------------------------

    if "assets" in result:

        assets = result.get("assets", [])

        if not assets:
            return "You currently do not have any IT assets assigned."

        responses = []

        for asset in assets:

            asset_type = asset.get("asset_type", "Asset")
            asset_name = asset.get("asset_name", "Unknown")
            asset_id = asset.get("asset_id", "Unknown")
            issue_date = asset.get("issue_date", "Unknown")
            warranty = asset.get("warranty_expiry", "Unknown")
            status = asset.get("status", "Unknown")

            responses.append(
                f"• Asset ID: {asset_id}\n"
                f"• Asset Type: {asset_type}\n"
                f"• Asset Name: {asset_name}\n"
                f"• Issue Date: {issue_date}\n"
                f"• Warranty Expiry: {warranty}\n"
                f"• Status: {status}"
            )

        header = (
            "Your assigned IT asset is:"
            if len(responses) == 1
            else "Your assigned IT assets are:"
        )

        return header + "\n\n" + "\n\n".join(responses)

    # ---------------------------------------------------------
    # Expenses
    #
    # This previously had no dedicated branch and fell through
    # to the generic LLM fallback. Now it's formatted directly,
    # which is faster and doesn't depend on Ollama being up.
    # ---------------------------------------------------------

    if "total_amount" in result:

        records = result.get("records", [])

        if not records:
            return "You have no recorded expenses."

        lines = []

        for record in records:

            category = record.get("category", "Expense")
            amount = record.get("amount", 0)
            date = record.get("date", "Unknown")

            lines.append(f"• {category}: ₹{amount} on {date}")

        return (
            f"Here are your expense records "
            f"(Total: ₹{result.get('total_amount', 0)}):\n\n"
            + "\n".join(lines)
        )

    # ---------------------------------------------------------
    # Employee Information
    # ---------------------------------------------------------

    if (
        "employee_id" in result
        and "designation" in result
        and "department" in result
    ):

        return (
            f"You are {result.get('name', 'the employee')}, "
            f"working as a {result.get('designation', '')} "
            f"in the {result.get('department', '')} department. "
            f"Your manager is {result.get('manager', '')} "
            f"and your office location is {result.get('location', '')}."
        )

    # ---------------------------------------------------------
    # Leave Balance
    # ---------------------------------------------------------

    if (
        "casual_leave" in result
        or "earned_leave" in result
        or "sick_leave" in result
    ):

        return (
            f"You have "
            f"{result.get('casual_leave', 0)} Casual Leave days, "
            f"{result.get('earned_leave', 0)} Earned Leave days, "
            f"{result.get('sick_leave', 0)} Sick Leave days remaining."
        )

    # ---------------------------------------------------------
    # Leave Application
    # ---------------------------------------------------------

    if "request_id" in result:

        return (
            f"Your {result.get('leave_type', '')} request "
            f"has been submitted successfully.\n\n"
            f"Request ID: {result.get('request_id')}\n"
            f"Start Date: {result.get('start_date')}\n"
            f"End Date: {result.get('end_date')}\n"
            f"Working Days: {result.get('working_days')}\n"
            f"Status: {result.get('status', 'Pending')}"
        )

    # ---------------------------------------------------------
    # Other results → Ollama (fallback for anything unhandled)
    # ---------------------------------------------------------

    prompt = f"""
{RESPONSE_PROMPT}

Structured result from the Office Assistant:

{json.dumps(result, indent=2, default=str)}

Generate the final employee-facing response.

IMPORTANT RULES:

1. Use ONLY information present in the structured result.
2. Never use information from previous conversations.
3. Never invent employee information.
4. Never add information that is not present in the structured result.
5. Do not mention Ollama.
6. Do not mention Python.
7. Do not mention internal agents.
8. Return only the employee-facing answer.
"""

    try:

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        answer = response["message"]["content"]

        if answer:
            return answer.strip()

        return "I could not generate a response."

    except Exception as exc:

        return f"Unable to generate response: {exc}"