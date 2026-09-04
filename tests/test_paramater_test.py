from app.agents.parameter_agent import extract_leave_parameters


def test_extract_leave_parameters():
    result = extract_leave_parameters(
        "I want casual leave from 2026-10-12 to 2026-10-13 for personal work"
    )

    assert result["leave_type"] == "Casual Leave"
    assert result["start_date"] == "2026-10-12"
    assert result["end_date"] == "2026-10-13"
    assert result["reason"] == "personal work"