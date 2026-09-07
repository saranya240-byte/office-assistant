import json
from datetime import datetime


def safe_strip(value):
    """
    Safely strip whitespace from a value.
    """

    if value is None:
        return ""

    return str(value).strip()


def format_date(date_value):
    """
    Format a date as YYYY-MM-DD.
    """

    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d")

    return str(date_value)


def format_currency(amount):
    """
    Format a numeric amount as Indian Rupees.
    """

    try:
        return f"₹{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def safe_json_dumps(data):
    """
    Convert Python data to readable JSON.
    """

    return json.dumps(
        data,
        indent=2,
        default=str,
    )