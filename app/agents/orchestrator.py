from app.agents.intent_agent import classify_intent
from app.agents.employee_agent import handle_employee_query
from app.agents.action_agent import handle_action
from app.agents.parameter_agent import extract_leave_parameters
from app.agents.policy_agent import handle_policy_query


def process_query(
    query: str,
    employee_id: str,
    leave_type: str = "",
    start_date: str = "",
    end_date: str = "",
    reason: str = "",
) -> dict:

    # -----------------------------------------
    # Step 1: Classify user intent
    # -----------------------------------------
    intent = classify_intent(query)

    # -----------------------------------------
    # Step 2: Handle policy queries using RAG
    # -----------------------------------------
    if intent == "POLICY":

        result = handle_policy_query(query)

        return {
            "intent": intent,
            "route": "RAG",
            "query": query,
            "result": result,
        }

    # -----------------------------------------
    # Step 3: Handle employee-specific queries
    # -----------------------------------------
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

    # -----------------------------------------
    # Step 4: Handle action requests
    # -----------------------------------------
    if intent == "APPLY_LEAVE":

        # Extract parameters from natural language
        parameters = extract_leave_parameters(query)

        # If parameters were not found in the query,
        # use values passed directly to the orchestrator.
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

        return {
            "intent": intent,
            "route": "ACTION_TOOL",
            "parameters": {
                "leave_type": final_leave_type,
                "start_date": final_start_date,
                "end_date": final_end_date,
                "reason": final_reason,
            },
            "result": result,
        }

    # -----------------------------------------
    # Step 5: Unknown intent
    # -----------------------------------------
    return {
        "intent": "UNKNOWN",
        "route": "NONE",
        "message": (
            "I couldn't determine what you're asking. "
            "Please rephrase your request."
        ),
    }