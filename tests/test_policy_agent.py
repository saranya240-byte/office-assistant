from app.agents.policy_agent import handle_policy_query


def test_policy_query():
    result = handle_policy_query(
        "What is the WFH policy?"
    )

    assert result["success"] is True
    assert "results" in result
    assert len(result["results"]) > 0
    assert "citations" in result