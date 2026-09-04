import os

# ---------------------------------------------------------
# SSL / CA certificate configuration
# Must be set BEFORE importing sentence-transformers
# ---------------------------------------------------------

SYSTEM_CA = "/etc/ssl/certs/ca-certificates.crt"

if not os.path.exists(SYSTEM_CA):
    raise FileNotFoundError(
        f"CA certificate bundle not found: {SYSTEM_CA}"
    )

os.environ["REQUESTS_CA_BUNDLE"] = SYSTEM_CA
os.environ["SSL_CERT_FILE"] = SYSTEM_CA
os.environ["CURL_CA_BUNDLE"] = SYSTEM_CA

print("Using certificate bundle:", SYSTEM_CA)


# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from text_splitter import create_chunks
from document_loader import load_all_pdfs


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"


# ---------------------------------------------------------
# Load embedding model
# ---------------------------------------------------------

def load_embedding_model():
    """
    Load the sentence-transformer embedding model.
    """

    print(f"Loading embedding model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    print("Embedding model loaded successfully.")

    return model


# ---------------------------------------------------------
# Generate embeddings
# ---------------------------------------------------------

def generate_embeddings(chunks, model):
    """
    Generate embeddings for all text chunks.

    Only the chunk text is embedded.
    Metadata such as source/page/chunk is preserved separately.
    """

    if not chunks:
        raise ValueError(
            "No chunks available for embedding."
        )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        f"Generating embeddings for {len(texts)} chunks..."
    )

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    embeddings = embeddings.astype("float32")

    print("Embeddings generated successfully.")

    return embeddings


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    # -----------------------------------------------------
    # Locate project root
    # -----------------------------------------------------

    project_root = Path(
        __file__
    ).resolve().parents[2]

    # -----------------------------------------------------
    # Locate knowledge base
    #
    # office-assistant/
    # └── app/
    #     ├── knowledge_base/
    #     │   ├── Employee_Handbook.pdf
    #     │   ├── Leave_Policy.pdf
    #     │   ├── Travel_Policy.pdf
    #     │   ├── IT_Policy.pdf
    #     │   └── WFH_Policy.pdf
    #     │
    #     └── rag/
    #         └── embeddings.py
    # -----------------------------------------------------

    knowledge_base_path = (
        project_root
        / "app"
        / "knowledge_base"
    )

    print()
    print("Knowledge Base:")
    print(knowledge_base_path)

    # -----------------------------------------------------
    # Check knowledge base
    # -----------------------------------------------------

    if not knowledge_base_path.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: "
            f"{knowledge_base_path}"
        )

    # -----------------------------------------------------
    # Load PDFs
    # -----------------------------------------------------

    print()
    print("Loading PDF documents...")

    documents = load_all_pdfs(
        str(knowledge_base_path)
    )

    print(
        f"Loaded pages: {len(documents)}"
    )

    # -----------------------------------------------------
    # Create chunks
    # -----------------------------------------------------

    print()
    print("Creating text chunks...")

    chunks = create_chunks(
        documents,
        chunk_size=500,
        chunk_overlap=100
    )

    print(
        f"Created chunks: {len(chunks)}"
    )

    # -----------------------------------------------------
    # Load embedding model
    # -----------------------------------------------------

    print()

    model = load_embedding_model()

    # -----------------------------------------------------
    # Generate embeddings
    # -----------------------------------------------------

    print()

    embeddings = generate_embeddings(
        chunks,
        model
    )

    # -----------------------------------------------------
    # Display results
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("EMBEDDING RESULTS")
    print("=" * 60)

    print(
        f"Number of chunks : {len(chunks)}"
    )

    print(
        f"Embedding shape  : {embeddings.shape}"
    )

    print(
        f"Embedding dtype  : {embeddings.dtype}"
    )

    print()

    print("First chunk:")
    print(
        chunks[0]["text"]
    )

    print()

    print("First embedding:")
    print(
        embeddings[0][:10]
    )

    print()

    print("Embedding vector length:")
    print(
        len(embeddings[0])
    )