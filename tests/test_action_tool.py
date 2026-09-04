from app.tools.action_tool import apply_leave


EMPLOYEE_ID = "TN0001"


def test_valid_leave_request():
    result = apply_leave(
        employee_id=EMPLOYEE_ID,
        leave_type="Casual Leave",
        start_date="2026-10-12",
        end_date="2026-10-13",
        reason="Personal work",
    )

    assert result["success"] is True
    assert result["employee_id"] == EMPLOYEE_ID
    assert result["leave_type"] == "Casual Leave"
    assert result["working_days"] == 2
    assert result["status"] == "Pending"
    assert "request_id" in result


def test_invalid_employee():
    result = apply_leave(
        employee_id="TN9999",
        leave_type="Casual Leave",
        start_date="2026-10-12",
        end_date="2026-10-13",
    )

    assert result["success"] is False
    assert "not found" in result["message"]


def test_invalid_leave_type():
    result = apply_leave(
        employee_id=EMPLOYEE_ID,
        leave_type="Vacation Leave",
        start_date="2026-10-12",
        end_date="2026-10-13",
    )

    assert result["success"] is False
    assert "Invalid leave type" in result["message"]


def test_invalid_dates():
    result = apply_leave(
        employee_id=EMPLOYEE_ID,
        leave_type="Casual Leave",
        start_date="2026-10-15",
        end_date="2026-10-12",
    )

    assert result["success"] is False
    assert "Start date cannot be after end date" in result["message"]


def test_invalid_date_format():
    result = apply_leave(
        employee_id=EMPLOYEE_ID,
        leave_type="Casual Leave",
        start_date="12-10-2026",
        end_date="13-10-2026",
    )

    assert result["success"] is False
    assert "YYYY-MM-DD" in result["message"]