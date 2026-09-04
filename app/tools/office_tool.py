from pathlib import Path
import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "office_locations.csv"
)


def get_office(location: str) -> dict:
    """
    Retrieve office information by city/location.
    """

    df = pd.read_csv(DATA_PATH)

    location = location.strip().lower()

    office = df[
        df["location"].str.lower() == location
    ]

    if office.empty:
        return {
            "success": False,
            "message": f"No office found for {location}."
        }

    row = office.iloc[0]

    return {
        "success": True,
        "office_id": row["office_id"],
        "location": row["location"],
        "address": row["address"],
        "working_hours": row["working_hours"],
        "working_days": row["working_days"]
    }