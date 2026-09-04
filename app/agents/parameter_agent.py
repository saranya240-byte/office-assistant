import re
from datetime import datetime


def extract_leave_parameters(query: str) -> dict:
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
    # Expected formats:
    # 2026-10-12
    # 12-10-2026
    # 12/10/2026
    # -------------------------
    dates = re.findall(
        r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}-\d{2}-\d{4}\b|\b\d{2}/\d{2}/\d{4}\b",
        query
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
        re.IGNORECASE
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