from pathlib import Path
import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "IT_assets.csv"
)


def get_it_asset(employee_id: str) -> dict:
    """
    Retrieve IT assets assigned to an employee.
    """

    df = pd.read_csv(DATA_PATH)

    employee_id = employee_id.strip().upper()

    assets = df[df["employee_id"] == employee_id]

    if assets.empty:
        return {
            "success": False,
            "message": f"No IT assets found for {employee_id}."
        }

    records = assets.to_dict(orient="records")

    return {
        "success": True,
        "employee_id": employee_id,
        "assets": records
    }