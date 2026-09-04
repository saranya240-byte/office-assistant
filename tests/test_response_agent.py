from app.agents.response_agent import generate_response


def test_response_agent():
    result = {
        "success": True,
        "employee_id": "TN0001",
        "department": "Engineering",
        "designation": "Software Engineer",
    }

    response = generate_response(result)

    assert isinstance(response, str)
    assert len(response) > 0