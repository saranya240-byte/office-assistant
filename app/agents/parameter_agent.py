import re
from datetime import datetime


def extract_leave_parameters(query: str) -> dict:
    """
    Extract leave type, dates, and reason from an employee query.
    """

    if not query:
        return {
            "leave_type": "",
            "start_date": "",
            "end_date": "",
            "reason": "",
        }

    query_lower = query.lower()

    # --------------------------------
    # Leave type
    # --------------------------------

    leave_type = ""

    if (
        "casual leave" in query_lower
        or "casual" in query_lower
    ):
        leave_type = "Casual Leave"

    elif (
        "earned leave" in query_lower
        or "earned" in query_lower
    ):
        leave_type = "Earned Leave"

    elif (
        "sick leave" in query_lower
        or "sick" in query_lower
    ):
        leave_type = "Sick Leave"

    # --------------------------------
    # Dates
    # --------------------------------

    dates = re.findall(
        r"\b\d{4}-\d{2}-\d{2}\b"
        r"|\b\d{2}-\d{2}-\d{4}\b"
        r"|\b\d{2}/\d{2}/\d{4}\b",
        query,
    )

    start_date = ""
    end_date = ""

    # A single date means a one-day leave request — treat it as
    # both the start and end date. Previously a query like
    # "apply sick leave on 2026-09-10" extracted NO dates at all
    # because the code only handled the 2-dates case.
    if len(dates) == 1:
        single_date = normalize_date(dates[0])
        start_date = single_date
        end_date = single_date

    elif len(dates) >= 2:
        start_date = normalize_date(dates[0])
        end_date = normalize_date(dates[1])

    # --------------------------------
    # Reason
    # --------------------------------

    reason = ""

    # Kept "for" as a trigger (needed for phrasing like "... for
    # personal work"), but added a negative lookahead so it no
    # longer matches "for 2 days" / "for 3 days" — previously
    # "apply casual leave for 2 days because I am travelling"
    # incorrectly set the reason to "2 days because I am
    # travelling" instead of "I am travelling".
    reason_match = re.search(
        r"(?:because|due to|reason is|reason:|for)\s+"
        r"(?!\d+\s*days?\b)(.+)",
        query,
        re.IGNORECASE,
    )

    if reason_match:
        reason = reason_match.group(1).strip().rstrip(".?!")

    return {
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
    }


def normalize_date(date_string: str) -> str:
    """
    Convert supported date formats to YYYY-MM-DD.
    """

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]

    for date_format in formats:

        try:
            date = datetime.strptime(
                date_string,
                date_format,
            )

            return date.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            continue

    return ""