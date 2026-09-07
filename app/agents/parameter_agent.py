import json
import re
from datetime import datetime

from google import genai

from app.utils.config import GEMINI_API_KEY, GEMINI_MODEL


client = genai.Client(api_key=GEMINI_API_KEY)


PARAMETER_PROMPT = """
You are the leave parameter extraction component of TechNova Pvt. Ltd.'s
Office Assistant.

Extract leave request information from the employee's query.

Return ONLY valid JSON in exactly this format:

{
    "leave_type": "",
    "start_date": "",
    "end_date": "",
    "reason": ""
}

Allowed leave types:
- Casual Leave
- Earned Leave
- Sick Leave

Date format:
- Convert dates to YYYY-MM-DD whenever the exact date can be determined.

Rules:
1. Do not invent missing information.
2. If leave type is missing, return an empty string.
3. If start date is missing, return an empty string.
4. If end date is missing, return an empty string.
5. If reason is missing, return an empty string.
6. Extract only information actually provided by the employee.
7. Return only JSON. Do not add explanations.
"""


def extract_leave_parameters(query: str) -> dict:
    """
    Extract leave parameters using Gemini.

    If Gemini fails or returns invalid information,
    fall back to deterministic regex-based extraction.
    """

    query = query.strip()

    if not query:
        return empty_parameters()

    # -----------------------------------
    # Try Gemini first
    # -----------------------------------
    try:
        prompt = f"""
{PARAMETER_PROMPT}

Employee query:
{query}

JSON:
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        if response.text:
            text = response.text.strip()

            # Remove markdown code fences if Gemini adds them
            text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"```\s*", "", text)

            data = json.loads(text)

            if isinstance(data, dict):
                result = {
                    "leave_type": str(data.get("leave_type", "")).strip(),
                    "start_date": str(data.get("start_date", "")).strip(),
                    "end_date": str(data.get("end_date", "")).strip(),
                    "reason": str(data.get("reason", "")).strip(),
                }

                # Validate leave type
                valid_leave_types = {
                    "Casual Leave",
                    "Earned Leave",
                    "Sick Leave",
                }

                if result["leave_type"] not in valid_leave_types:
                    result["leave_type"] = ""

                # Validate dates
                if result["start_date"]:
                    result["start_date"] = normalize_date(
                        result["start_date"]
                    )

                if result["end_date"]:
                    result["end_date"] = normalize_date(
                        result["end_date"]
                    )

                return result

    except Exception:
        # Gemini failure → use deterministic fallback
        pass

    # -----------------------------------
    # Deterministic fallback
    # -----------------------------------
    return extract_leave_parameters_fallback(query)


def extract_leave_parameters_fallback(query: str) -> dict:
    """
    Original regex-based parameter extraction.
    """

    query_lower = query.lower()

    # -------------------------
    # Leave type
    # -------------------------
    leave_type = ""

    if "casual leave" in query_lower or "casual" in query_lower:
        leave_type = "Casual Leave"

    elif "earned leave" in query_lower or "earned" in query_lower:
        leave_type = "Earned Leave"

    elif "sick leave" in query_lower or "sick" in query_lower:
        leave_type = "Sick Leave"

    # -------------------------
    # Dates
    # -------------------------
    dates = re.findall(
        r"\b\d{4}-\d{2}-\d{2}\b"
        r"|\b\d{2}-\d{2}-\d{4}\b"
        r"|\b\d{2}/\d{2}/\d{4}\b",
        query,
    )

    start_date = ""
    end_date = ""

    if len(dates) >= 2:
        start_date = normalize_date(dates[0])
        end_date = normalize_date(dates[1])

    # -------------------------
    # Reason
    # -------------------------
    reason = ""

    reason_match = re.search(
        r"(?:because|reason is|for)\s+(.+)",
        query,
        re.IGNORECASE,
    )

    if reason_match:
        reason = reason_match.group(1).strip()

    return {
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
    }


def normalize_date(date_string: str) -> str:
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]

    for date_format in formats:
        try:
            date = datetime.strptime(date_string, date_format)
            return date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return ""


def empty_parameters() -> dict:
    return {
        "leave_type": "",
        "start_date": "",
        "end_date": "",
        "reason": "",
    }