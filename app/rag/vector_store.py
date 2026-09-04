
from pathlib import Path
import pickle

import faiss

from document_loader import load_all_pdfs
from text_splitter import create_chunks
from embeddings import load_embedding_model, generate_embeddings


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

INDEX_FILE = "policy_index.faiss"
CHUNKS_FILE = "chunks.pkl"


# ---------------------------------------------------------
# Create FAISS index
# ---------------------------------------------------------

def create_faiss_index(embeddings):
    """
    Create a FAISS index using cosine similarity.

    Since embeddings are normalized, inner product
    is equivalent to cosine similarity.
    """

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


# ---------------------------------------------------------
# Save FAISS index
# ---------------------------------------------------------

def save_faiss_index(index, path):
    """
    Save FAISS index to disk.
    """

    faiss.write_index(
        index,
        str(path)
    )

    print(f"FAISS index saved to: {path}")


# ---------------------------------------------------------
# Save chunks
# ---------------------------------------------------------

def save_chunks(chunks, path):
    """
    Save chunk metadata to disk using pickle.
    """

    with open(path, "wb") as file:
        pickle.dump(
            chunks,
            file
        )

    print(f"Chunks saved to: {path}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    # -----------------------------------------------------
    # Locate project directories
    # -----------------------------------------------------

    project_root = Path(__file__).resolve().parents[2]

    knowledge_base_path = (
        project_root
        / "app"
        / "knowledge_base"
    )

    vector_store_path = (
        project_root
        / "app"
        / "vector_store"
    )

    # Create vector_store directory
    vector_store_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # File paths
    index_path = (
        vector_store_path
        / INDEX_FILE
    )

    chunks_path = (
        vector_store_path
        / CHUNKS_FILE
    )

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    print("=" * 70)
    print("TECHNOVA RAG - VECTOR STORE CREATION")
    print("=" * 70)

    print()
    print("Project Root:")
    print(project_root)

    print()
    print("Knowledge Base:")
    print(knowledge_base_path)

    print()
    print("Vector Store:")
    print(vector_store_path)

    # -----------------------------------------------------
    # Validate knowledge base
    # -----------------------------------------------------

    if not knowledge_base_path.exists():

        raise FileNotFoundError(
            f"Knowledge base not found: "
            f"{knowledge_base_path}"
        )

    # -----------------------------------------------------
    # Load PDF documents
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
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    print(
        f"Created chunks: {len(chunks)}"
    )

    # -----------------------------------------------------
    # Validate chunks
    # -----------------------------------------------------

    if not chunks:

        raise ValueError(
            "No chunks were created from the documents."
        )

    # -----------------------------------------------------
    # Load embedding model
    # -----------------------------------------------------

    print()
    print("Loading embedding model...")

    model = load_embedding_model()

    print(
        "Embedding model loaded successfully."
    )

    # -----------------------------------------------------
    # Generate embeddings
    # -----------------------------------------------------

    print()
    print("Generating embeddings...")

    embeddings = generate_embeddings(
        chunks,
        model
    )

    print()
    print(
        f"Embedding matrix shape: "
        f"{embeddings.shape}"
    )

    # -----------------------------------------------------
    # Validate embedding count
    # -----------------------------------------------------

    if len(embeddings) != len(chunks):

        raise ValueError(
            f"Mismatch between embeddings "
            f"({len(embeddings)}) and chunks "
            f"({len(chunks)})."
        )

    # -----------------------------------------------------
    # Create FAISS index
    # -----------------------------------------------------

    print()
    print("Creating FAISS index...")

    index = create_faiss_index(
        embeddings
    )

    print(
        "FAISS index created successfully."
    )

    print(
        f"Number of vectors: {index.ntotal}"
    )

    # -----------------------------------------------------
    # Validate FAISS index
    # -----------------------------------------------------

    if index.ntotal != len(chunks):

        raise ValueError(
            f"FAISS/chunk mismatch: "
            f"{index.ntotal} vectors vs "
            f"{len(chunks)} chunks."
        )

    # -----------------------------------------------------
    # Save FAISS index
    # -----------------------------------------------------

    print()
    print("Saving vector store...")

    save_faiss_index(
        index,
        index_path
    )

    # -----------------------------------------------------
    # Save chunks
    # -----------------------------------------------------

    save_chunks(
        chunks,
        chunks_path
    )

    # -----------------------------------------------------
    # Final validation
    # -----------------------------------------------------

    print()
    print("Validating saved files...")

    if not index_path.exists():

        raise FileNotFoundError(
            f"FAISS index was not saved: "
            f"{index_path}"
        )

    if not chunks_path.exists():

        raise FileNotFoundError(
            f"Chunks file was not saved: "
            f"{chunks_path}"
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("VECTOR STORE CREATION COMPLETE")
    print("=" * 70)

    print()
    print(f"Documents/pages : {len(documents)}")
    print(f"Chunks          : {len(chunks)}")
    print(f"Vectors         : {index.ntotal}")
    print(f"Dimensions      : {embeddings.shape[1]}")

    print()
    print("Saved files:")

    print(
        f"FAISS index     : {index_path}"
    )

    print(
        f"Chunk metadata  : {chunks_path}"
    )

    print()
    print("FAISS vectors and chunks are synchronized.")
