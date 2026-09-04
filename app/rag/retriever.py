from pathlib import Path
import pickle

import faiss


TOP_K = 5

INDEX_FILE = "policy_index.faiss"
CHUNKS_FILE = "chunks.pkl"

MODEL_NAME = "all-MiniLM-L6-v2"


def load_vector_store(vector_store_path):
    """
    Load the FAISS index and chunk metadata from disk.
    """

    index_path = vector_store_path / INDEX_FILE
    chunks_path = vector_store_path / CHUNKS_FILE

    print(f"Loading FAISS index from: {index_path}")

    index = faiss.read_index(str(index_path))

    print(f"Loading chunk metadata from: {chunks_path}")

    with open(chunks_path, "rb") as file:
        chunks = pickle.load(file)

    print("Vector store loaded successfully.")
    print(f"Vectors: {index.ntotal}")
    print(f"Chunks : {len(chunks)}")

    return index, chunks


def retrieve(query, model, index, chunks, top_k=TOP_K):
    """
    Retrieve the most relevant policy chunks for a query.
    """

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_id in zip(scores[0], indices[0]):

        if index_id == -1:
            continue

        chunk = chunks[index_id]

        results.append({
            "text": chunk["text"],
            "source": chunk["metadata"]["source"],
            "page": chunk["metadata"]["page"],
            "chunk": chunk["metadata"]["chunk"],
            "score": float(score)
        })

    return results


def print_results(query, results):
    """
    Display retrieval results.
    """

    print()
    print("=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    print(f"Query: {query}")

    for i, result in enumerate(results, start=1):

        print()
        print("-" * 70)

        print(f"Result #{i}")
        print(f"Score : {result['score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Page  : {result['page']}")
        print(f"Chunk : {result['chunk']}")

        print()
        print("Text:")
        print(result["text"])

    print()
    print("-" * 70)


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[2]

    vector_store_path = (
        project_root
        / "app"
        / "vector_store"
    )

    print("=" * 70)
    print("TECHNOVA RAG - RETRIEVER")
    print("=" * 70)

    print()
    print(f"Project Root:")
    print(project_root)

    print()
    print(f"Vector Store:")
    print(vector_store_path)

    # -----------------------------------------------------
    # Load embedding model
    # -----------------------------------------------------

    print()
    print("Loading embedding model...")

    from embeddings import load_embedding_model

    model = load_embedding_model()

    # -----------------------------------------------------
    # Load persisted vector store
    # -----------------------------------------------------

    print()

    index, chunks = load_vector_store(
        vector_store_path
    )

    # -----------------------------------------------------
    # Test queries
    # -----------------------------------------------------

    test_queries = [
        "How many work from home days can I take in a month?",
        "How do I apply for leave?",
        "What are the rules for business travel?",
        "What should I do if my company laptop is lost?"
    ]

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    for query in test_queries:

        results = retrieve(
            query=query,
            model=model,
            index=index,
            chunks=chunks,
            top_k=TOP_K
        )

        print_results(
            query,
            results
        )