from app.agents.intent_agent import classify_intent
from app.agents.employee_agent import handle_employee_query
from app.agents.action_agent import handle_action
from app.agents.parameter_agent import extract_leave_parameters
from app.agents.policy_agent import handle_policy_query
from app.agents.response_agent import generate_response

from app.utils.memory import (
    get_short_term_memory,
    get_long_term_memory,
    format_conversation,
)


def build_context(messages: list[dict]) -> str:
    """
    Convert previous conversation messages into a simple text context.
    Only the most recent 10 messages are included.
    """

    if not messages:
        return ""

    recent_messages = messages[-10:]

    context_lines = []

    for message in recent_messages:
        role = message.get("role", "").capitalize()
        content = message.get("content", "").strip()

        if content:
            context_lines.append(f"{role}: {content}")

    return "\n".join(context_lines)


def process_query(
    query: str,
    employee_id: str,
    leave_type: str = "",
    start_date: str = "",
    end_date: str = "",
    reason: str = "",
    conversation_history: list[dict] | None = None,
) -> dict:

    conversation_history = conversation_history or []

    # ---------------------------------------------------------
    # Get conversation memory
    # ---------------------------------------------------------

    short_term = get_short_term_memory(
        conversation_history,
        limit=10,
    )

    long_term = get_long_term_memory(
        employee_id,
        limit=10,
    )

    short_term_context = format_conversation(short_term)
    long_term_context = format_conversation(long_term)

    context = "\n".join(
        part
        for part in [
            short_term_context,
            long_term_context,
        ]
        if part
    )

    # ---------------------------------------------------------
    # Classify CURRENT query only
    # ---------------------------------------------------------

    intent = classify_intent(query)

    # ---------------------------------------------------------
    # POLICY → RAG → RESPONSE
    # ---------------------------------------------------------

    if intent == "POLICY":

        result = handle_policy_query(query)

        response = generate_response(result)

        return {
            "intent": intent,
            "route": "RAG",
            "query": query,
            "conversation_context": context,
            "result": result,
            "response": response,
        }

    # ---------------------------------------------------------
    # EMPLOYEE QUERY → EMPLOYEE TOOL → RESPONSE
    # ---------------------------------------------------------

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

        response = generate_response(result)

        return {
            "intent": intent,
            "route": "EMPLOYEE_TOOL",
            "query": query,
            "conversation_context": context,
            "result": result,
            "response": response,
        }

    # ---------------------------------------------------------
    # APPLY LEAVE
    # ---------------------------------------------------------

    if intent == "APPLY_LEAVE":

        # IMPORTANT:
        # Extract parameters ONLY from the current query.
        # Do not pass conversation history here.
        parameters = extract_leave_parameters(query)

        # Explicit parameters from the current query take priority.
        final_leave_type = parameters["leave_type"] or leave_type
        final_start_date = parameters["start_date"] or start_date
        final_end_date = parameters["end_date"] or end_date
        final_reason = parameters["reason"] or reason

        result = handle_action(
            intent=intent,
            employee_id=employee_id,
            leave_type=final_leave_type,
            start_date=final_start_date,
            end_date=final_end_date,
            reason=final_reason,
        )

        response = generate_response(result)

        return {
            "intent": intent,
            "route": "ACTION_TOOL",
            "query": query,
            "conversation_context": context,
            "parameters": {
                "leave_type": final_leave_type,
                "start_date": final_start_date,
                "end_date": final_end_date,
                "reason": final_reason,
            },
            "result": result,
            "response": response,
        }

    # ---------------------------------------------------------
    # UNKNOWN
    # ---------------------------------------------------------

    response = (
        "I couldn't determine what you're asking. "
        "Please rephrase your request."
    )

    return {
        "intent": "UNKNOWN",
        "route": "NONE",
        "query": query,
        "conversation_context": context,
        "message": response,
        "response": response,
    }