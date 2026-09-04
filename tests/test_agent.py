from app.agents.intent_agent import classify_intent
from app.agents.orchestrator import process_query


EMPLOYEE_ID = "TN0001"


def test_policy_intent():
    result = classify_intent(
        "How many WFH days can employees take?"
    )

    assert result == "POLICY"


def test_leave_intent():
    result = classify_intent(
        "How many leaves do I have?"
    )

    assert result == "LEAVE_BALANCE"


def test_expense_intent():
    result = classify_intent(
        "How much have I spent?"
    )

    assert result == "EXPENSE"


def test_asset_intent():
    result = classify_intent(
        "What laptop is assigned to me?"
    )

    assert result == "IT_ASSET"


def test_office_intent():
    result = classify_intent(
        "Where is my office?"
    )

    assert result == "OFFICE"


def test_leave_action_intent():
    result = classify_intent(
        "I want to apply leave"
    )

    assert result == "APPLY_LEAVE"


def test_employee_orchestrator():
    result = process_query(
        "How many leaves do I have?",
        EMPLOYEE_ID,
    )

    assert result["intent"] == "LEAVE_BALANCE"
    assert result["route"] == "EMPLOYEE_TOOL"
    assert result["result"]["success"] is True


def test_expense_orchestrator():
    result = process_query(
        "How much have I spent?",
        EMPLOYEE_ID,
    )

    assert result["intent"] == "EXPENSE"
    assert result["route"] == "EMPLOYEE_TOOL"
    assert result["result"]["success"] is True


def test_policy_orchestrator():
    result = process_query(
        "What is the WFH policy?",
        EMPLOYEE_ID,
    )

    assert result["intent"] == "POLICY"
    assert result["route"] == "RAG"