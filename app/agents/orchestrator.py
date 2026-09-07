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

from app.utils.security import validate_employee_access


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
    """
    Main orchestrator for the TechNova Office Assistant.

    Flow:

    User Query
        ↓
    Security Validation
        ↓
    Intent Agent
        ↓
    ┌───────────────┬──────────────────┬────────────────────┐
    │               │                  │
    POLICY      EMPLOYEE QUERY      APPLY LEAVE
    │               │                  │
    RAG         Employee Tool    Parameter Extraction
    │               │                  │
    └───────────────┴──────────────────┴───────────────┐
                                                       ↓
                                                Action Tool
                                                       ↓
                                                Response Agent
                                                       ↓
                                                  Final Response

    Conversation memory is used for context and leave parameter extraction,
    but the CURRENT query alone is used to determine intent.
    """

    query = query.strip()

    conversation_history = conversation_history or []

    # ---------------------------------------------------------
    # SECURITY / ACCESS CONTROL
    # ---------------------------------------------------------

    access = validate_employee_access(employee_id)

    if not access["allowed"]:
        return {
            "intent": "SECURITY",
            "route": "NONE",
            "query": query,
            "conversation_context": "",
            "result": {
                "success": False,
                "message": access["message"],
            },
            "response": access["message"],
        }

    # Use the validated/normalized employee ID
    employee_id = access["employee_id"]

    # ---------------------------------------------------------
    # CONVERSATION MEMORY
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
    # INTENT CLASSIFICATION
    # ---------------------------------------------------------
    #
    # Only the CURRENT query is passed to the intent agent.
    # Conversation context is used later for leave parameters.
    # ---------------------------------------------------------

    intent = classify_intent(query)

    # ---------------------------------------------------------
    # POLICY → RAG → RESPONSE AGENT
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
    # EMPLOYEE QUERY → EMPLOYEE TOOL → RESPONSE AGENT
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # Pass the CURRENT query to generate_response().
    #
    # This allows questions such as:
    #
    # "What is my name?"
    # → "Your name is Ananya Sharma."
    #
    # "Who is my manager?"
    # → "Your manager is Kavya Iyer."
    #
    # instead of returning the complete employee profile.
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

        response = generate_response(
            result,
            query,
        )

        return {
            "intent": intent,
            "route": "EMPLOYEE_TOOL",
            "query": query,
            "conversation_context": context,
            "result": result,
            "response": response,
        }

    # ---------------------------------------------------------
    # APPLY LEAVE → PARAMETER EXTRACTION → ACTION TOOL
    # ---------------------------------------------------------

    if intent == "APPLY_LEAVE":

        # By default, extract parameters from the current query.
        parameter_query = query

        # If conversation context exists, use it to help extract
        # missing leave parameters.

        if context:

            parameter_query = f"""
Previous conversation context:

{context}

Current employee query:

{query}

Extract the leave parameters for the CURRENT request.
Do not use unrelated information from previous conversations.
"""

        parameters = extract_leave_parameters(parameter_query)

        # -----------------------------------------------------
        # Use extracted values first.
        #
        # If extraction did not find a value, use the value
        # explicitly supplied to process_query().
        # -----------------------------------------------------

        final_leave_type = (
            parameters["leave_type"] or leave_type
        )

        final_start_date = (
            parameters["start_date"] or start_date
        )

        final_end_date = (
            parameters["end_date"] or end_date
        )

        final_reason = (
            parameters["reason"] or reason
        )

        # -----------------------------------------------------
        # ACTION TOOL
        # -----------------------------------------------------

        result = handle_action(
            intent=intent,
            employee_id=employee_id,
            leave_type=final_leave_type,
            start_date=final_start_date,
            end_date=final_end_date,
            reason=final_reason,
        )

        # -----------------------------------------------------
        # RESPONSE AGENT
        # -----------------------------------------------------

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

