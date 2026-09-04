from pathlib import Path
import pandas as pd


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "employees.csv"


def get_employee(employee_id: str) -> dict:
    """
    Retrieve employee information using employee ID.
    """

    df = pd.read_csv(DATA_PATH)

    employee_id = employee_id.strip().upper()

    employee = df[df["employee_id"] == employee_id]

    if employee.empty:
        return {
            "success": False,
            "message": f"Employee {employee_id} was not found."
        }

    record = employee.iloc[0]

    return {
        "success": True,
        "employee_id": record["employee_id"],
        "name": record["name"],
        "department": record["department"],
        "designation": record["designation"],
        "manager": record["manager"],
        "location": record["location"]
    }