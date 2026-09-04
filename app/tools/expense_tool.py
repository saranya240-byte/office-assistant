from pathlib import Path
import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "expense_records.csv"
)


def get_expenses(employee_id: str, category: str = None) -> dict:
    """
    Retrieve expense records for an employee.

    Optional category filter:
        Hotel
        Flight
        Train
        Cab
        Meals
        Internet
        Office Supplies
    """

    df = pd.read_csv(DATA_PATH)

    employee_id = employee_id.strip().upper()

    expenses = df[df["employee_id"] == employee_id]

    if expenses.empty:
        return {
            "success": False,
            "message": f"No expense records found for {employee_id}."
        }

    if category:
        expenses = expenses[
            expenses["category"].str.lower() == category.strip().lower()
        ]

    if expenses.empty:
        return {
            "success": True,
            "employee_id": employee_id,
            "total_amount": 0,
            "records": []
        }

    total = expenses["amount"].sum()

    records = expenses.to_dict(orient="records")

    return {
        "success": True,
        "employee_id": employee_id,
        "total_amount": round(float(total), 2),
        "records": records
    }