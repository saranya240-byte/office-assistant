def classify_intent(query: str) -> str:
    """
    Classify the employee query.

    Strong deterministic rules are checked first because they provide
    predictable behavior for well-known office-assistant queries.
    Ollama is used for queries that are not clearly identified by rules.
    """

    query = query.strip()

    if not query:
        return "UNKNOWN"

    # First use deterministic rules for clear cases.
    fallback_intent = classify_intent_fallback(query)

    if fallback_intent != "UNKNOWN":
        return fallback_intent

    # Use Ollama for queries that are not clearly classified.
    try:
        prompt = f"""
{INTENT_PROMPT}

Employee query:
{query}

Intent:
"""

        response = ollama.chat(
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
            intent = answer.strip().upper()
            intent = re.sub(r"[^A-Z_]", "", intent)

            if intent in INTENTS:
                return intent

    except Exception:
        pass

    return "UNKNOWN"

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
        "apply for casual leave",
        "apply for earned leave",
        "apply for sick leave",
        "request leave",
        "request for leave",
        "request casual leave",
        "request earned leave",
        "request sick leave",
        "take leave",
        "take casual leave",
        "take earned leave",
        "take sick leave",
        "take time off",
        "take a day off",
        "take days off",
        "need time off",
        "need leave",
        "need casual leave",
        "need earned leave",
        "need sick leave",
        "want time off",
        "want leave",
        "want casual leave",
        "want earned leave",
        "want sick leave",
        "want to apply for leave",
        "want to apply for casual leave",
        "want to apply for earned leave",
        "want to apply for sick leave",
        "book leave",
        "book casual leave",
        "book earned leave",
        "book sick leave",
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
    # Employee information
    if any(phrase in query for phrase in [
        "my profile",
        "my details",
        "my name",
        "what is my name",
        "what's my name",
        "tell me my name",
        "my department",
        "my designation",
        "my manager",
        "who is my manager",
    ]):
        return "EMPLOYEE_INFO"

    return "UNKNOWN"