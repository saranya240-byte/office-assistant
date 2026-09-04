from app.agents.intent_agent import classify_intent
from app.agents.employee_agent import handle_employee_query
from app.agents.action_agent import handle_action


def process_query(
    query: str,
    employee_id: str,
    leave_type: str = "",
    start_date: str = "",
    end_date: str = "",
    reason: str = "",
) -> dict:

    # ----------------------------------------
    # 1. Understand user intent
    # ----------------------------------------
    intent = classify_intent(query)

    # ----------------------------------------
    # 2. Policy → RAG
    # ----------------------------------------
    if intent == "POLICY":

        return {
            "intent": intent,
            "route": "RAG",
            "query": query,
            "message": "This query should be handled by the RAG agent."
        }

    # ----------------------------------------
    # 3. Employee data → Tools
    # ----------------------------------------
    if intent in {
        "EMPLOYEE_INFO",
        "LEAVE_BALANCE",
        "EXPENSE",
        "IT_ASSET",
        "OFFICE",
    }:

        result = handle_employee_query(
            intent=intent,
            employee_id=employee_id,
            query=query,
        )

        return {
            "intent": intent,
            "route": "EMPLOYEE_TOOL",
            "result": result,
        }

    # ----------------------------------------
    # 4. Actions
    # ----------------------------------------
    if intent == "APPLY_LEAVE":

        result = handle_action(
            intent=intent,
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )

        return {
            "intent": intent,
            "route": "ACTION_TOOL",
            "result": result,
        }

    # ----------------------------------------
    # 5. Unknown
    # ----------------------------------------
    return {
        "intent": "UNKNOWN",
        "route": "NONE",
        "message": (
            "I couldn't determine what you're asking. "
            "Please rephrase your request."
        ),
    }