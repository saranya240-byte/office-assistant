from pathlib import Path
import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "leave_balance.csv"
)


def get_leave_balance(employee_id: str) -> dict:
    """
    Retrieve the leave balance for an employee.
    """

    df = pd.read_csv(DATA_PATH)

    employee_id = employee_id.strip().upper()

    record = df[df["employee_id"] == employee_id]

    if record.empty:
        return {
            "success": False,
            "message": f"Leave balance not found for {employee_id}."
        }

    row = record.iloc[0]

    return {
        "success": True,
        "employee_id": employee_id,
        "casual_leave": int(row["casual_leave"]),
        "earned_leave": int(row["earned_leave"]),
        "sick_leave": int(row["sick_leave"]),
        "wfh_days_used": int(row["wfh_days_used"])
    }