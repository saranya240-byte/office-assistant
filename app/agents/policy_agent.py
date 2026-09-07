import os
from pathlib import Path
from functools import lru_cache

# ============================================================
# HUGGING FACE OFFLINE MODE
# ============================================================

# Prevent Hugging Face from making network requests at runtime.
os.environ.setdefault("HF_HUB_OFFLINE", "1")


# ============================================================
# IMPORTS
# ============================================================

from sentence_transformers import SentenceTransformer

from app.rag.retriever import (
    load_vector_store,
    retrieve,
)


# ============================================================
# PATHS
# ============================================================

BASE_PATH = Path(__file__).resolve().parent.parent

VECTOR_STORE_PATH = BASE_PATH / "vector_store"


# Local cached MiniLM model
LOCAL_MODEL_PATH = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--sentence-transformers--all-MiniLM-L6-v2"
    / "snapshots"
    / "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
)


# ============================================================
# LOAD RAG RESOURCES ONCE
# ============================================================

@lru_cache(maxsize=1)
def load_rag_resources():
    """
    Load the embedding model, FAISS index and chunks only once.

    These resources are cached for the lifetime of the
    Python process.
    """

    print("Loading RAG resources ONCE...")

    # --------------------------------------------------------
    # Check local model
    # --------------------------------------------------------

    if not LOCAL_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Local MiniLM model not found at:\n"
            f"{LOCAL_MODEL_PATH}"
        )

    # --------------------------------------------------------
    # Load local embedding model
    # --------------------------------------------------------

    print("Loading local MiniLM model...")

    model = SentenceTransformer(
        str(LOCAL_MODEL_PATH)
    )

    # --------------------------------------------------------
    # Load existing FAISS vector store
    # --------------------------------------------------------

    print("Loading existing FAISS index...")

    index, chunks = load_vector_store(
        VECTOR_STORE_PATH
    )

    print("RAG resources loaded successfully.")

    print(f"Vectors: {index.ntotal}")
    print(f"Chunks : {len(chunks)}")

    return model, index, chunks


# ============================================================
# POLICY DOCUMENT PRIORITY
# ============================================================

def get_policy_priority(query: str) -> list:
    """
    Identify which policy document is most likely relevant
    based on simple deterministic keywords.

    This does NOT use an LLM.
    """

    query_lower = query.lower()

    priorities = []

    # Work From Home
    if (
        "work from home" in query_lower
        or "work from office" in query_lower
        or "wfh" in query_lower
        or "remote work" in query_lower
        or "hybrid work" in query_lower
    ):
        priorities.append("WFH_Policy.pdf")

    # Leave
    if (
        "leave" in query_lower
        or "casual leave" in query_lower
        or "earned leave" in query_lower
        or "sick leave" in query_lower
        or "vacation" in query_lower
    ):
        priorities.append("Leave_Policy.pdf")

    # Reimbursement / Expense
    if (
        "reimbursement" in query_lower
        or "expense" in query_lower
        or "claim" in query_lower
        or "travel expense" in query_lower
    ):
        priorities.append("Reimbursement_Policy.pdf")

    # Security
    if (
        "security" in query_lower
        or "password" in query_lower
        or "vpn" in query_lower
        or "confidential" in query_lower
    ):
        priorities.append("Security_Policy.pdf")

    # Office
    if (
        "office" in query_lower
        or "working hours" in query_lower
        or "office hours" in query_lower
        or "holiday" in query_lower
    ):
        priorities.append("Office_Guidelines.pdf")

    # IT
    if (
        "laptop" in query_lower
        or "computer" in query_lower
        or "it asset" in query_lower
        or "device" in query_lower
        or "equipment" in query_lower
    ):
        priorities.append("IT_Policy.pdf")

    # Travel
    if (
        "travel" in query_lower
        or "business trip" in query_lower
        or "flight booking" in query_lower
    ):
        priorities.append("Travel_Policy.pdf")

    # Onboarding
    if (
        "onboarding" in query_lower
        or "induction" in query_lower
        or "new joinee" in query_lower
        or "new employee" in query_lower
    ):
        priorities.append("Onboarding_Guide.pdf")

    # Benefits
    if (
        "benefits" in query_lower
        or "insurance" in query_lower
        or "provident fund" in query_lower
        or "gratuity" in query_lower
    ):
        priorities.append("Benefits_Guide.pdf")

    # Employee Handbook (general catch-all — checked last so the
    # more specific documents above still take priority)
    if (
        "handbook" in query_lower
        or "code of conduct" in query_lower
    ):
        priorities.append("Employee_Handbook.pdf")

    return priorities


# ============================================================
# RERANK POLICY RESULTS
# ============================================================

def rerank_policy_results(
    query: str,
    results: list,
) -> list:
    """
    Reorder retrieved chunks so that the most relevant
    policy document appears first.

    FAISS similarity remains the primary retrieval mechanism.
    This is only a lightweight deterministic reranking step.
    """

    priorities = get_policy_priority(query)

    if not priorities:
        return results

    priority_results = []
    other_results = []

    for result in results:

        source = result.get("source", "")

        if source in priorities:
            priority_results.append(result)
        else:
            other_results.append(result)

    # Preserve FAISS ordering within each group.
    return priority_results + other_results


# ============================================================
# RETRIEVE POLICY
# ============================================================

def retrieve_policy(
    query: str,
    top_k: int = 8,
) -> list:
    """
    Retrieve relevant policy chunks.

    Important:
    - PDFs are NOT loaded here.
    - PDFs are NOT chunked here.
    - Document embeddings are NOT regenerated here.
    - FAISS is NOT rebuilt here.
    - Only the user query is embedded.
    """

    model, index, chunks = load_rag_resources()

    # --------------------------------------------------------
    # Search existing FAISS index
    # --------------------------------------------------------

    results = retrieve(
        query=query,
        model=model,
        index=index,
        chunks=chunks,
        top_k=top_k,
    )

    # --------------------------------------------------------
    # Remove weak results
    #
    # 0.50 is a reasonable bar, but with all-MiniLM-L6-v2 a
    # genuinely relevant chunk phrased differently from the
    # question often scores 0.35-0.48 — strictly enforcing 0.50
    # was silently discarding correct answers (e.g. "do I need
    # manager approval for WFH?" against a WFH policy chunk that
    # doesn't repeat the word "approval" verbatim). If the
    # strict cutoff finds nothing, retry with a lower bar before
    # giving up, so a moderately-confident match still surfaces
    # rather than returning "not found".
    # --------------------------------------------------------

    STRICT_THRESHOLD = 0.50
    FALLBACK_THRESHOLD = 0.30

    filtered_results = [
        result
        for result in results
        if result.get("score", 0) >= STRICT_THRESHOLD
    ]

    if not filtered_results:
        filtered_results = [
            result
            for result in results
            if result.get("score", 0) >= FALLBACK_THRESHOLD
        ]

    results = filtered_results

    # --------------------------------------------------------
    # Rerank relevant policy document
    # --------------------------------------------------------

    results = rerank_policy_results(
        query=query,
        results=results,
    )

    return results


# ============================================================
# POLICY QUERY HANDLER
# ============================================================

def handle_policy_query(
    query: str,
) -> dict:
    """
    Main policy/RAG handler.
    """

    # --------------------------------------------------------
    # Validate query
    # --------------------------------------------------------

    if not query or not query.strip():

        return {
            "success": False,
            "message": "Policy query cannot be empty.",
            "citations": [],
        }

    query = query.strip()

    try:

        # ----------------------------------------------------
        # Retrieve policy information
        # ----------------------------------------------------

        results = retrieve_policy(
            query=query,
            top_k=8,
        )

        # ----------------------------------------------------
        # No relevant results
        # ----------------------------------------------------

        if not results:

            return {
                "success": False,
                "message": (
                    "I could not find relevant information "
                    "in the company policies."
                ),
                "citations": [],
            }

        # ----------------------------------------------------
        # Citations
        # ----------------------------------------------------

        citations = [
            {
                "source": result.get(
                    "source",
                    "Unknown",
                ),
                "page": result.get(
                    "page",
                    "Unknown",
                ),
                "chunk": result.get(
                    "chunk",
                    "Unknown",
                ),
                "score": result.get(
                    "score",
                    0,
                ),
            }
            for result in results
        ]

        # ----------------------------------------------------
        # Return structured RAG result
        # ----------------------------------------------------

        return {
            "success": True,
            "query": query,
            "results": results,
            "citations": citations,
        }

    except Exception as exc:

        return {
            "success": False,
            "message": f"Policy search failed: {exc}",
            "citations": [],
        }