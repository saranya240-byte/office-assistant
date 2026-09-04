from app.tools.employee_tool import get_employee
from app.tools.leave_tool import get_leave_balance
from app.tools.expense_tool import get_expenses
from app.tools.asset_tool import get_it_asset
from app.tools.office_tool import get_office


EMPLOYEE_ID = "TN0001"


def test_employee():
    result = get_employee(EMPLOYEE_ID)
    assert result["success"] is True
    assert result["employee_id"] == EMPLOYEE_ID


def test_leave_balance():
    result = get_leave_balance(EMPLOYEE_ID)
    assert result["success"] is True
    assert "casual_leave" in result
    assert "earned_leave" in result
    assert "sick_leave" in result


def test_expenses():
    result = get_expenses(EMPLOYEE_ID)
    assert result["success"] is True
    assert "total_amount" in result
    assert "records" in result


def test_it_asset():
    result = get_it_asset(EMPLOYEE_ID)
    assert result["success"] is True
    assert "assets" in result


def test_office():
    result = get_office("Hyderabad")
    assert result["success"] is True
    assert result["location"] == "Hyderabad"