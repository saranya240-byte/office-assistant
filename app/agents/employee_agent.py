from app.tools.employee_tool import get_employee
from app.tools.leave_tool import get_leave_balance
from app.tools.expense_tool import get_expenses
from app.tools.asset_tool import get_it_asset
from app.tools.office_tool import get_office


def handle_employee_query(
    intent: str,
    employee_id: str,
    query: str = ""
) -> dict:

    if intent == "EMPLOYEE_INFO":
        return get_employee(employee_id)

    if intent == "LEAVE_BALANCE":
        return get_leave_balance(employee_id)

    if intent == "EXPENSE":
        return get_expenses(employee_id)

    if intent == "IT_ASSET":
        return get_it_asset(employee_id)

    if intent == "OFFICE":
        employee = get_employee(employee_id)

        if not employee["success"]:
            return employee

        return get_office(employee["location"])

    return {
        "success": False,
        "message": f"Unsupported employee intent: {intent}"
    }