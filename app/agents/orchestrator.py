from app.agents.intent_agent import classify_intent
from app.agents.employee_agent import handle_employee_query
from app.agents.action_agent import handle_action
from app.agents.parameter_agent import extract_leave_parameters
from app.agents.policy_agent import handle_policy_query
from app.agents.response_agent import generate_response


def process_query(
    query: str,
    employee_id: str,
    leave_type: str = "",
    start_date: str = "",
    end_date: str = "",
    reason: str = "",
) -> dict:

    intent = classify_intent(query)

    # Policy → RAG → Gemini Response
    if intent == "POLICY":
        result = handle_policy_query(query)
        response = generate_response(result)

        return {
            "intent": intent,
            "route": "RAG",
            "query": query,
            "result": result,
            "response": response,
        }

    # Employee query → Employee Tool → Gemini Response
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
            "result": result,
            "response": response,
        }

    # Action → Action Tool → Gemini Response
    if intent == "APPLY_LEAVE":
        parameters = extract_leave_parameters(query)

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
            "parameters": {
                "leave_type": final_leave_type,
                "start_date": final_start_date,
                "end_date": final_end_date,
                "reason": final_reason,
            },
            "result": result,
            "response": response,
        }

    # Unknown
    response = (
        "I couldn't determine what you're asking. "
        "Please rephrase your request."
    )

    return {
        "intent": "UNKNOWN",
        "route": "NONE",
        "message": response,
        "response": response,
    }
