from app.tools.action_tool import apply_leave


def handle_action(
    intent: str,
    employee_id: str,
    leave_type: str = "",
    start_date: str = "",
    end_date: str = "",
    reason: str = "",
) -> dict:

    if intent == "APPLY_LEAVE":

        return apply_leave(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )

    return {
        "success": False,
        "message": f"Unsupported action: {intent}"
    }