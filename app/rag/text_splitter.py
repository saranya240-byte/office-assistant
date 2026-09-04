from pathlib import Path
from document_loader import load_all_pdfs


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> list[str]:
    """
    Split text into chunks without breaking words.

    Args:
        text: Text to split.
        chunk_size: Target maximum number of characters per chunk.
        chunk_overlap: Number of characters of overlap between chunks.

    Returns:
        List of text chunks.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if chunk_overlap < 0:
        raise ValueError(
            "chunk_overlap cannot be negative"
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    words = text.split()

    chunks = []

    current_words = []
    current_length = 0

    for word in words:

        word_length = len(word)

        proposed_length = (
            current_length + word_length + 1
            if current_words
            else word_length
        )

        if current_words and proposed_length > chunk_size:

            chunk = " ".join(current_words).strip()

            if chunk:
                chunks.append(chunk)

            # Create overlap from the end of current chunk
            overlap_words = []
            overlap_length = 0

            for previous_word in reversed(current_words):

                extra_length = (
                    len(previous_word) + 1
                    if overlap_words
                    else len(previous_word)
                )

                if overlap_length + extra_length > chunk_overlap:
                    break

                overlap_words.insert(0, previous_word)
                overlap_length += extra_length

            current_words = overlap_words
            current_length = len(
                " ".join(current_words)
            )

        current_words.append(word)

        current_length = len(
            " ".join(current_words)
        )

    # Add final chunk
    if current_words:

        chunk = " ".join(current_words).strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def create_chunks(
    documents: list[dict],
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> list[dict]:
    """
    Create chunks while preserving document metadata.

    Each chunk contains:

        text
        metadata
            - source
            - page
            - chunk
    """

    all_chunks = []

    for document in documents:

        text = document["text"]

        original_metadata = document["metadata"]

        chunks = split_text(
            text=text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        for chunk_number, chunk in enumerate(
            chunks,
            start=1
        ):

            chunk_metadata = {
                "source": original_metadata["source"],
                "page": original_metadata["page"],
                "chunk": chunk_number
            }

            all_chunks.append({
                "text": chunk,
                "metadata": chunk_metadata
            })

    return all_chunks


if __name__ == "__main__":

    # --------------------------------------------------
    # Find project root
    # --------------------------------------------------

    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    # --------------------------------------------------
    # Correct knowledge base location
    #
    # office-assistant/
    # └── app/
    #     └── knowledge_base/
    # --------------------------------------------------

    knowledge_base_path = (
        PROJECT_ROOT
        / "app"
        / "knowledge_base"
    )

    print(
        "Knowledge Base:",
        knowledge_base_path
    )

    # Check that the directory exists
    if not knowledge_base_path.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: "
            f"{knowledge_base_path}"
        )

    # --------------------------------------------------
    # 1. LOAD DOCUMENTS
    # --------------------------------------------------

    documents = load_all_pdfs(
        str(knowledge_base_path)
    )

    print(
        f"\nLoaded pages: {len(documents)}"
    )

    # --------------------------------------------------
    # 2. CREATE CHUNKS
    # --------------------------------------------------

    chunks = create_chunks(
        documents,
        chunk_size=500,
        chunk_overlap=100
    )

    print(
        f"Created chunks: {len(chunks)}"
    )

    # --------------------------------------------------
    # 3. DISPLAY SAMPLE CHUNKS
    # --------------------------------------------------

    print(
        "\n=============================="
    )

    for chunk in chunks[:5]:

        print(
            "\n------------------------------"
        )

        print(
            f"Source: "
            f"{chunk['metadata']['source']}"
        )

        print(
            f"Page: "
            f"{chunk['metadata']['page']}"
        )

        print(
            f"Chunk: "
            f"{chunk['metadata']['chunk']}"
        )

        print("\nText:")

        print(chunk["text"])