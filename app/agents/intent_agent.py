import re

from google import genai

from app.utils.config import GEMINI_API_KEY, GEMINI_MODEL


INTENTS = [
    "POLICY",
    "EMPLOYEE_INFO",
    "LEAVE_BALANCE",
    "EXPENSE",
    "IT_ASSET",
    "OFFICE",
    "APPLY_LEAVE",
    "UNKNOWN",
]


client = genai.Client(api_key=GEMINI_API_KEY)


INTENT_PROMPT = """
You are the intent classification component of TechNova Pvt. Ltd.'s
Office Assistant.

Classify the employee's query into exactly ONE of these intents:

POLICY
EMPLOYEE_INFO
LEAVE_BALANCE
EXPENSE
IT_ASSET
OFFICE
APPLY_LEAVE
UNKNOWN

Intent definitions:

POLICY:
Questions about company policies, rules, eligibility, allowed limits,
work from home, leave rules, travel rules, IT rules, reimbursement rules,
or other company-wide policies.

EMPLOYEE_INFO:
Questions about the employee's own profile, department, designation,
manager, name, or employment details.

LEAVE_BALANCE:
Questions about how many leaves the employee has remaining or how many
WFH days they have used.

EXPENSE:
Questions about the employee's expenses, spending, or expense records.

IT_ASSET:
Questions about laptops, computers, monitors, headsets, devices,
or other IT assets assigned to the employee.

OFFICE:
Questions about office location, address, working hours, office timings,
or the employee's office.

APPLY_LEAVE:
Requests to apply for, request, book, or take leave.

UNKNOWN:
Anything that does not clearly belong to the categories above.

Important:
- Return ONLY the intent name.
- Do not return explanations.
- Do not return JSON.
- Do not return punctuation.
"""


def classify_intent(query: str) -> str:
    """
    Classify the query using Gemini.

    If Gemini fails or returns an invalid intent,
    fall back to deterministic keyword-based classification.
    """

    query = query.strip()

    if not query:
        return "UNKNOWN"

    # Try LLM classification first
    try:
        prompt = f"""
{INTENT_PROMPT}

Employee query:
{query}

Intent:
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        if response.text:
            intent = response.text.strip().upper()

            # Remove common formatting returned by an LLM
            intent = re.sub(r"[^A-Z_]", "", intent)

            if intent in INTENTS:
                return intent

    except Exception:
        # Gemini failure should not break the assistant.
        pass

    # Fall back to deterministic classification
    return classify_intent_fallback(query)


def classify_intent_fallback(query: str) -> str:
    """
    Deterministic fallback classifier.

    This preserves the original keyword-based behavior.
    """

    query = query.strip().lower()

    # Leave action
    if any(phrase in query for phrase in [
        "apply leave",
        "apply for leave",
        "request leave",
        "request for leave",
        "take leave",
        "take time off",
        "take a day off",
        "take days off",
        "need time off",
        "want time off",
        "days off",
        "book leave",
        "want casual leave",
        "want earned leave",
        "want sick leave",
        "need casual leave",
        "need earned leave",
        "need sick leave",
    ]):
        return "APPLY_LEAVE"

    # Leave balance
    if any(phrase in query for phrase in [
        "leave balance",
        "how many leaves",
        "how much leave",
        "leaves do i have",
        "remaining leave",
        "wfh days have i used",
    ]):
        return "LEAVE_BALANCE"

    # Company policies
    if any(phrase in query for phrase in [
        "policy",
        "policies",
        "allowed",
        "eligible",
        "how many wfh days can",
        "work from home",
        "working remotely",
        "rules around working remotely",
        "rules for working remotely",
        "remote work rules",
        "remote working rules",
        "can i work remotely",
        "can i work from home",
        "travel policy",
        "leave policy",
        "it policy",
        "reimbursement policy",
        "reimbursement rules",
    ]):
        return "POLICY"

    # Expenses
    if any(phrase in query for phrase in [
        "expense",
        "expenses",
        "spent",
        "spending",
    ]):
        return "EXPENSE"

    # IT assets
    if any(phrase in query for phrase in [
        "laptop",
        "computer",
        "it asset",
        "asset assigned",
        "device assigned",
        "monitor",
    ]):
        return "IT_ASSET"

    # Office
    if any(phrase in query for phrase in [
        "office location",
        "office address",
        "where is the office",
        "where is my office",
        "my office",
        "working hours",
        "office timings",
    ]):
        return "OFFICE"

    # Employee information
    if any(phrase in query for phrase in [
        "my profile",
        "my details",
        "my department",
        "my designation",
        "my manager",
        "who is my manager",
    ]):
        return "EMPLOYEE_INFO"

    return "UNKNOWN"