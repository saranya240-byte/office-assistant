import re


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


def classify_intent(query: str) -> str:
    """
    Classify a user query into one of the supported intents.

    This deterministic version is our MVP.
    Later, the LLM can replace this classifier without
    changing the rest of the agent architecture.
    """

    query = query.strip().lower()

    # -----------------------------
    # Leave action
    # -----------------------------
    if any(
        phrase in query
        for phrase in [
            "apply leave",
            "apply for leave",
            "request leave",
            "take leave",
            "book leave",
        ]
    ):
        return "APPLY_LEAVE"

    # -----------------------------
    # Leave balance
    # -----------------------------
    if any(
        phrase in query
        for phrase in [
            "leave balance",
            "how many leaves",
            "how much leave",
            "leaves do i have",
            "remaining leave",
            "wfh days have i used",
        ]
    ):
        return "LEAVE_BALANCE"

    # -----------------------------
    # Expense
    # -----------------------------
    if any(
        phrase in query
        for phrase in [
            "expense",
            "expenses",
            "spent",
            "spending",
            "reimbursement",
        ]
    ):
        return "EXPENSE"

    # -----------------------------
    # IT assets
    # -----------------------------
    if any(
        phrase in query
        for phrase in [
            "laptop",
            "computer",
            "it asset",
            "asset assigned",
            "device assigned",
            "monitor",
        ]
    ):
        return "IT_ASSET"

    # -----------------------------
    # Office
    # -----------------------------
    if any(
        phrase in query
        for phrase in [
            "office location",
            "office address",
            "where is the office",
            "working hours",
            "office timings",
        ]
    ):
        return "OFFICE"

    # -----------------------------
    # Employee information
    # -----------------------------
    if any(
        phrase in query
        for phrase in [
            "my profile",
            "my details",
            "my department",
            "my designation",
            "my manager",
            "who is my manager",
        ]
    ):
        return "EMPLOYEE_INFO"

    # -----------------------------
    # Policy
    # -----------------------------
    if any(
        phrase in query
        for phrase in [
            "policy",
            "policies",
            "allowed",
            "eligible",
            "how many wfh days can",
            "work from home",
            "travel policy",
            "leave policy",
            "it policy",
            "reimbursement policy",
        ]
    ):
        return "POLICY"

    return "UNKNOWN"