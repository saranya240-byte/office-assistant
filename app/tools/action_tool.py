from pathlib import Path
from datetime import datetime
import pandas as pd

BASE_PATH = Path(__file__).resolve().parent.parent
EMPLOYEE_PATH = BASE_PATH / "data" / "employees.csv"
LEAVE_BALANCE_PATH = BASE_PATH / "data" / "leave_balance.csv"
LEAVE_REQUEST_PATH = BASE_PATH / "data" / "leave_requests.csv"


VALID_LEAVE_TYPES = {
    "casual": "casual_leave",
    "casual leave": "casual_leave",
    "earned": "earned_leave",
    "earned leave": "earned_leave",
    "sick": "sick_leave",
    "sick leave": "sick_leave",
}


def apply_leave(
    employee_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str = ""
) -> dict:
    """
    Create a pending leave request for an employee.

    Leave balance is NOT deducted here because the request
    is only pending approval.
    """

    employee_id = employee_id.strip().upper()
    leave_type_key = leave_type.strip().lower()

    # --------------------------------------------------
    # 1. Validate employee
    # --------------------------------------------------
    employees = pd.read_csv(EMPLOYEE_PATH)

    if employee_id not in employees["employee_id"].values:
        return {
            "success": False,
            "message": f"Employee {employee_id} was not found."
        }

    # --------------------------------------------------
    # 2. Validate leave type
    # --------------------------------------------------
    if leave_type_key not in VALID_LEAVE_TYPES:
        return {
            "success": False,
            "message": (
                "Invalid leave type. Choose Casual Leave, "
                "Earned Leave, or Sick Leave."
            )
        }

    balance_column = VALID_LEAVE_TYPES[leave_type_key]

    # --------------------------------------------------
    # 3. Validate dates
    # --------------------------------------------------
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return {
            "success": False,
            "message": "Dates must be in YYYY-MM-DD format."
        }

    if start > end:
        return {
            "success": False,
            "message": "Start date cannot be after end date."
        }

    # --------------------------------------------------
    # 4. Calculate working days
    # --------------------------------------------------
    working_days = len(
        pd.bdate_range(start=start, end=end)
    )

    if working_days <= 0:
        return {
            "success": False,
            "message": "The selected dates contain no working days."
        }

    # --------------------------------------------------
    # 5. Check leave balance
    # --------------------------------------------------
    leave_balance = pd.read_csv(LEAVE_BALANCE_PATH)

    employee_balance = leave_balance[
        leave_balance["employee_id"] == employee_id
    ]

    if employee_balance.empty:
        return {
            "success": False,
            "message": f"Leave balance not found for {employee_id}."
        }

    available_balance = int(
        employee_balance.iloc[0][balance_column]
    )

    if working_days > available_balance:
        return {
            "success": False,
            "message": (
                f"Insufficient {leave_type.title()} balance. "
                f"Available: {available_balance} day(s), "
                f"requested: {working_days} day(s)."
            )
        }

    # --------------------------------------------------
    # 6. Load existing requests
    # --------------------------------------------------
    if LEAVE_REQUEST_PATH.exists():
        requests = pd.read_csv(LEAVE_REQUEST_PATH)
    else:
        requests = pd.DataFrame(
            columns=[
                "request_id",
                "employee_id",
                "leave_type",
                "start_date",
                "end_date",
                "status",
                "reason",
            ]
        )

    # --------------------------------------------------
    # 7. Generate request ID
    # --------------------------------------------------
    request_number = len(requests) + 1
    request_id = f"LR{request_number:05d}"

    normalized_leave_type = {
        "casual": "Casual Leave",
        "casual leave": "Casual Leave",
        "earned": "Earned Leave",
        "earned leave": "Earned Leave",
        "sick": "Sick Leave",
        "sick leave": "Sick Leave",
    }[leave_type_key]

    # --------------------------------------------------
    # 8. Create request
    # --------------------------------------------------
    new_request = pd.DataFrame([{
        "request_id": request_id,
        "employee_id": employee_id,
        "leave_type": normalized_leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "status": "Pending",
        "reason": reason.strip(),
    }])

    requests = pd.concat(
        [requests, new_request],
        ignore_index=True
    )

    requests.to_csv(LEAVE_REQUEST_PATH, index=False)

    # --------------------------------------------------
    # 9. Return structured result
    # --------------------------------------------------
    return {
        "success": True,
        "request_id": request_id,
        "employee_id": employee_id,
        "leave_type": normalized_leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "working_days": working_days,
        "status": "Pending",
        "message": (
            f"Leave request {request_id} created successfully "
            f"for {working_days} working day(s)."
        ),
    }