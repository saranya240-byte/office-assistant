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


# A small, explicit map of common typos actually seen in testing.
# Deliberately NOT a general fuzzy-matcher: a broad fuzzy corrector
# over the whole vocabulary risks silently "correcting" unrelated
# words and misrouting the query in ways that are hard to trace.
# This map only fires on an exact whole-word match, so it's safe
# and predictable — extend it as new typos turn up.
TYPO_CORRECTIONS = {
    "manger": "manager",
    "expresses": "expenses",
    "loose": "lose",
}


def _apply_typo_corrections(query: str) -> str:
    for typo, correction in TYPO_CORRECTIONS.items():
        query = re.sub(rf"\b{typo}\b", correction, query)
    return query


# --------------------------------------------------------------
# APPLY_LEAVE regexes
#
# The old version matched fixed phrases like "want sick leave" as
# an exact substring. That broke the moment a real user inserted
# a word — "i want 1 sick leave", "can i apply for a leave" — since
# "1" or "a" isn't in the literal phrase. These patterns instead
# allow a small gap (0-3 extra words) between the trigger word and
# "leave", so insertions like numbers or articles don't break the
# match. They intentionally look for singular "leave" (via \b),
# not "leaves", so they don't collide with LEAVE_BALANCE phrasing
# like "how many casual leaves do I have".
# --------------------------------------------------------------

_ACTION_LEAVE_PATTERN = re.compile(
    r"\b(?:apply|applying|request|requesting|book|booking|take|taking)\b"
    r"(?:\s+\w+){0,3}?\s+leave\b"
)

_TYPE_LEAVE_PATTERN = re.compile(
    r"\b(?:want|need|require|requesting)\b"
    r"(?:\s+\w+){0,3}?\s+(?:casual|earned|sick)\s+leave\b"
)


def classify_intent(query: str) -> str:
    query = query.strip().lower()

    # Normalize hyphens to spaces so phrases like "work-from-home"
    # match the same way "work from home" does. Without this,
    # the assignment's own example question ("How many
    # work-from-home days...") falls through to UNKNOWN.
    query = query.replace("-", " ")

    query = _apply_typo_corrections(query)

    # --------------------------------------------------------
    # 1. APPLY LEAVE (most specific — an action request)
    # --------------------------------------------------------
    if _ACTION_LEAVE_PATTERN.search(query) or _TYPE_LEAVE_PATTERN.search(query):
        return "APPLY_LEAVE"

    # --------------------------------------------------------
    # 2. LEAVE BALANCE (specific personal-data request)
    # --------------------------------------------------------
    if any(
        phrase in query
        for phrase in [
            "leave balance",
            "how many leaves",
            "how much leave",
            "leaves do i have",
            "remaining leave",
            "how many casual leaves",
            "how many sick leaves",
            "how many earned leaves",
        ]
    ):
        return "LEAVE_BALANCE"

    # --------------------------------------------------------
    # 3. POLICY (general company-document questions)
    #
    #    IMPORTANT: this is checked BEFORE OFFICE and IT_ASSET.
    #    Previously "what is the IT policy for laptops" or
    #    "reimbursement policy for a lost laptop" matched
    #    IT_ASSET first (because of "laptop") instead of POLICY,
    #    even though the employee was asking about the document,
    #    not their own assigned device.
    # --------------------------------------------------------
    if any(
        phrase in query
        for phrase in [
            "policy",
            "policies",
            "allowed",
            "eligible",
            "rules",
            "wfh",
            "work from home",
            "working from home",
            "how many wfh days",
            "travel policy",
            "leave policy",
            "it policy",
            "reimbursement policy",
            "reimbursement rules",
            "expense policy",
            "security policy",
            "employee handbook",
            "handbook",
            "onboarding",
            "induction process",
            "office guidelines",
            "guidelines",
            "benefits guide",
            "insurance",
            "provident fund",
            "gratuity",
            "holiday list",
            "public holidays",
            "leave without pay",
            "loss of pay",
            "approve",
            "approval",
            "requires approval",
            "sanction leave",
            "approving authority",
            "reimbursement",
            "receipt",
            "password",
            "weekend",
            "return equipment",
            "return my it equipment",
            "return laptop",
            "returning company property",
            "offboarding",
            "work from the office",
            "days in office",
            "office days",
            "wfo",
        ]
    ):
        return "POLICY"

    # --------------------------------------------------------
    # 4. OFFICE / LOCATION (employee-specific — their own office)
    #
    #    Removed the old standalone "location" keyword — it was
    #    too generic and could misfire on unrelated sentences
    #    that merely contained the word "location".
    # --------------------------------------------------------
    if any(
        phrase in query
        for phrase in [
            "office location",
            "office address",
            "where is the office",
            "where is my office",
            "where is my office location",
            "what is my office location",
            "my office location",
            "my office",
            "where is my location",
            "what is my location",
            "my location",
            "working hours",
            "office timings",
            "where am i based",
            "which city am i based",
            "my base location",
            "based in",
        ]
    ):
        return "OFFICE"

    # --------------------------------------------------------
    # 5. IT ASSET (employee-specific — what's assigned to them)
    # --------------------------------------------------------
    if any(
        phrase in query
        for phrase in [
            "laptop",
            "computer",
            "it asset",
            "asset assigned",
            "device assigned",
            "monitor",
            "keyboard",
            "mouse",
            "headset",
        ]
    ):
        return "IT_ASSET"

    # --------------------------------------------------------
    # 6. EXPENSE
    # --------------------------------------------------------
    if any(
        phrase in query
        for phrase in [
            "expense",
            "expenses",
            "spent",
            "spending",
        ]
    ):
        return "EXPENSE"

    # --------------------------------------------------------
    # 7. EMPLOYEE INFORMATION
    # --------------------------------------------------------
    if any(
        phrase in query
        for phrase in [
            "my profile",
            "my details",
            "my department",
            "my designation",
            "my manager",
            "who is my manager",
            "my name",
            "what is my name",
            "who am i",
            "tell me my details",
            "which department",
            "what department",
        ]
    ):
        return "EMPLOYEE_INFO"

    return "UNKNOWN"