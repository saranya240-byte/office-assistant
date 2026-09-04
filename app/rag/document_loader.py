from pathlib import Path
from pypdf import PdfReader


def load_pdf(file_path: str) -> list[dict]:
    """
    Load a single PDF and return one record per page.

    Each record contains:
        - text
        - metadata
            - source
            - page
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {file_path}"
        )

    reader = PdfReader(str(path))

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()

        if not text:
            continue

        documents.append({
            "text": text,
            "metadata": {
                "source": path.name,
                "page": page_number
            }
        })

    return documents


def load_all_pdfs(knowledge_base_path: str) -> list[dict]:
    """
    Load all PDF files from the knowledge base directory.
    """

    kb_path = Path(knowledge_base_path)

    if not kb_path.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: {knowledge_base_path}"
        )

    pdf_files = sorted(kb_path.glob("*.pdf"))

    if not pdf_files:
        raise ValueError(
            f"No PDF files found in {knowledge_base_path}"
        )

    all_documents = []

    for pdf_file in pdf_files:
        documents = load_pdf(str(pdf_file))
        all_documents.extend(documents)

    return all_documents


if __name__ == "__main__":

    # Find the project root automatically
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    # Correct knowledge base location:
    # office-assistant/app/knowledge_base/
    knowledge_base_path = PROJECT_ROOT / "app" / "knowledge_base"

    print("Knowledge base path:")
    print(knowledge_base_path)

    documents = load_all_pdfs(
        str(knowledge_base_path)
    )

    print(f"\nLoaded {len(documents)} pages")

    for document in documents[:3]:

        print("\n-----------------------------")

        print(
            "Source:",
            document["metadata"]["source"]
        )

        print(
            "Page:",
            document["metadata"]["page"]
        )

        print("Text:")

        print(document["text"][:500])