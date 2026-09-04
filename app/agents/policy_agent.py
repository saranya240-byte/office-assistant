from pathlib import Path

from sentence_transformers import SentenceTransformer

from app.rag.retriever import load_vector_store, retrieve


BASE_PATH = Path(__file__).resolve().parent.parent
VECTOR_STORE_PATH = BASE_PATH / "vector_store"

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None
_index = None
_chunks = None


def _load_rag():
    """
    Load the embedding model and FAISS vector store once.
    """

    global _model, _index, _chunks

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    if _index is None or _chunks is None:
        _index, _chunks = load_vector_store(VECTOR_STORE_PATH)


def retrieve_policy(query: str, top_k: int = 5) -> list:
    """
    Retrieve relevant policy chunks for a user query.
    """

    _load_rag()

    return retrieve(
        query=query,
        model=_model,
        index=_index,
        chunks=_chunks,
        top_k=top_k,
    )


def handle_policy_query(query: str) -> dict:
    """
    Handle a company policy question using the RAG system.

    The actual answer generation can be connected to the LLM later.
    For now, this agent returns the retrieved evidence and citations.
    """

    if not query or not query.strip():
        return {
            "success": False,
            "message": "Policy query cannot be empty.",
        }

    try:
        results = retrieve_policy(query.strip())

        if not results:
            return {
                "success": False,
                "message": "I could not find relevant information in the company policies.",
                "citations": [],
            }

        citations = [
            {
                "source": result["source"],
                "page": result["page"],
                "chunk": result["chunk"],
                "score": result["score"],
            }
            for result in results
        ]

        return {
            "success": True,
            "query": query.strip(),
            "results": results,
            "citations": citations,
        }

    except Exception as exc:
        return {
            "success": False,
            "message": f"Policy search failed: {exc}",
            "citations": [],
        }
