from app.tools.employee_tool import get_employee


def validate_employee_access(employee_id: str) -> dict:
    """
    Validate that the employee ID exists in the company system.
    """

    employee_id = employee_id.strip().upper()

    if not employee_id:
        return {
            "allowed": False,
            "message": "Employee ID is required."
        }

    employee = get_employee(employee_id)

    if not employee.get("success"):
        return {
            "allowed": False,
            "message": employee.get(
                "message",
                "Employee ID not found."
            )
        }

    return {
        "allowed": True,
        "employee_id": employee_id
    }