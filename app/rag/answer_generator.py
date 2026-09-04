import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

project_root = Path(__file__).resolve().parents[2]

env_path = project_root / ".env"

load_dotenv(env_path)


# ---------------------------------------------------------
# OpenAI configuration
# ---------------------------------------------------------

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError(
        "OPENAI_API_KEY was not found. "
        "Please add it to the .env file."
    )


client = OpenAI(api_key=API_KEY)

MODEL_NAME = "gpt-5.6-luna"


# ---------------------------------------------------------
# Build context
# ---------------------------------------------------------

def build_context(results):
    """
    Convert retrieved chunks into context for the LLM.
    """

    context_parts = []

    for i, result in enumerate(results, start=1):

        context_parts.append(
            f"""
Context {i}
Source: {result['source']}
Page: {result['page']}
Chunk: {result['chunk']}
Similarity Score: {result['score']:.4f}

{result['text']}
"""
        )

    return "\n".join(context_parts)


# ---------------------------------------------------------
# Generate answer
# ---------------------------------------------------------

def generate_answer(query, results):
    """
    Generate a grounded answer using retrieved policy context.
    """

    context = build_context(results)

    instructions = """
You are TechNova Pvt. Ltd.'s internal employee assistant.

Your job is to answer employee questions using ONLY the
provided policy context.

Rules:

1. Use only the supplied policy context.
2. Never invent or assume a company policy.
3. If the answer is not present in the context, say:
   "I could not find this information in the TechNova
   policy documents."
4. Give a concise, clear answer.
5. When the context contains the answer, cite the relevant
   document name and page number.
6. If multiple policy documents support the answer, cite
   all relevant documents.
7. Do not mention similarity scores.
8. Do not say that you are an AI model.
9. Do not provide information from outside the supplied
   TechNova policy documents.
"""

    user_prompt = f"""
Employee Question:

{query}


Retrieved TechNova Policy Context:

{context}
"""

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=instructions,
        input=user_prompt
    )

    return response.output_text


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    import sys

    sys.path.append(
        str(Path(__file__).resolve().parent)
    )

    from retriever import load_vector_store, retrieve
    from embeddings import load_embedding_model

    print("=" * 70)
    print("TECHNOVA RAG - OPENAI ANSWER GENERATOR")
    print("=" * 70)

    # -----------------------------------------------------
    # Paths
    # -----------------------------------------------------

    vector_store_path = (
        project_root
        / "app"
        / "vector_store"
    )

    # -----------------------------------------------------
    # Load embedding model
    # -----------------------------------------------------

    print()
    print("Loading embedding model...")

    embedding_model = load_embedding_model()

    # -----------------------------------------------------
    # Load vector store
    # -----------------------------------------------------

    print()
    print("Loading vector store...")

    index, chunks = load_vector_store(
        vector_store_path
    )

    # -----------------------------------------------------
    # Test question
    # -----------------------------------------------------

    query = (
        "How many work from home days "
        "can I take in a month?"
    )

    print()
    print("=" * 70)
    print("EMPLOYEE QUESTION")
    print("=" * 70)

    print(query)

    # -----------------------------------------------------
    # Retrieve context
    # -----------------------------------------------------

    print()
    print("Retrieving relevant policy information...")

    results = retrieve(
        query=query,
        model=embedding_model,
        index=index,
        chunks=chunks,
        top_k=5
    )

    # -----------------------------------------------------
    # Generate answer
    # -----------------------------------------------------

    print()
    print("Generating grounded answer...")

    answer = generate_answer(
        query=query,
        results=results
    )

    # -----------------------------------------------------
    # Display answer
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("TECHNOVA ASSISTANT")
    print("=" * 70)

    print(answer)

    print()
    print("=" * 70)