from app.rag.document_loader import load_all_pdfs


KNOWLEDGE_BASE_PATH = "app/knowledge_base"


def test_documents_are_loaded():
    """
    Verify that the knowledge base PDFs can be loaded
    and produce text with source/page metadata.
    """

    documents = load_all_pdfs(KNOWLEDGE_BASE_PATH)

    assert documents
    assert len(documents) > 0

    for document in documents:
        assert "text" in document
        assert "metadata" in document

        assert document["text"].strip() != ""

        assert "source" in document["metadata"]
        assert "page" in document["metadata"]


def test_expected_policy_documents_exist():
    """
    Verify that all required policy documents are present
    in the loaded knowledge base.
    """

    documents = load_all_pdfs(KNOWLEDGE_BASE_PATH)

    sources = {
        document["metadata"]["source"]
        for document in documents
    }

    expected_documents = {
        "Employee_Handbook.pdf",
        "Leave_Policy.pdf",
        "Travel_Policy.pdf",
        "IT_Policy.pdf",
        "WFH_Policy.pdf",
    }

    assert expected_documents.issubset(sources)


def test_wfh_policy_content_is_loaded():
    """
    Verify that important WFH policy content is actually
    extracted from the PDF.
    """

    documents = load_all_pdfs(KNOWLEDGE_BASE_PATH)

    wfh_documents = [
        document
        for document in documents
        if document["metadata"]["source"] == "WFH_Policy.pdf"
    ]

    assert wfh_documents

    combined_text = " ".join(
        document["text"].lower()
        for document in wfh_documents
    )

    assert "8" in combined_text
    assert "wfh" in combined_text or "work from home" in combined_text


def test_leave_policy_content_is_loaded():
    """
    Verify that the leave policy contains expected content.
    """

    documents = load_all_pdfs(KNOWLEDGE_BASE_PATH)

    leave_documents = [
        document
        for document in documents
        if document["metadata"]["source"] == "Leave_Policy.pdf"
    ]

    assert leave_documents

    combined_text = " ".join(
        document["text"].lower()
        for document in leave_documents
    )

    assert "casual leave" in combined_text
    assert "earned leave" in combined_text
    assert "sick leave" in combined_text