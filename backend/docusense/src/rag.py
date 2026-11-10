
import os
import re

from dotenv import load_dotenv
from google import genai

from .search import search


# Initial threshold; calibrated using the current evaluation set.
SIMILARITY_THRESHOLD = 0.50

# Project configuration
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=GEMINI_API_KEY)


def retrieve_context(query, top_k=5, strategy="fixed"):
    """Retrieve relevant document chunks."""
    return search(
        query=query,
        top_k=top_k,
        strategy=strategy
    )


def build_context(results):
    """Construct context with numbered source references."""

    if not results:
        return ""

    context_parts = []

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        context_part = (
            f"[{index}]\n"
            f"Source: {metadata['source']}\n"
            f"Page: {metadata['page']}\n"
            f"Chunk: {metadata['chunk_index']}\n"
            f"Content:\n{result['text']}\n"
        )

        context_parts.append(context_part)

    return "\n---\n".join(context_parts)


def generate_answer(query, context):
    """Generate an answer grounded only in supplied context."""

    if not context.strip():
        return "I cannot answer because no relevant context was retrieved."

    prompt = f"""
You are DocuSense, a document-based question-answering assistant.

STRICT INSTRUCTIONS:
1. Answer using ONLY the supplied context.
2. Do not use outside knowledge or assumptions.
3. Do not invent facts or citations.
4. If the context is insufficient, clearly say so.
5. Keep the answer clear and relevant.
6. Cite supporting information using only the provided
   reference labels, such as [1] or [2].
7. Do not cite a source unless it supports the statement.

SUPPLIED CONTEXT:
{context}

USER QUESTION:
{query}

GROUNDED ANSWER:
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    if not response.text:
        return "The model did not return an answer."

    return response.text.strip()


def validate_citations(answer, source_count):
    """Check whether generated citation labels exist."""

    cited_labels = re.findall(r"\[(\d+)\]", answer)

    invalid_labels = [
        label for label in cited_labels
        if int(label) < 1 or int(label) > source_count
    ]

    return {
        "valid": len(invalid_labels) == 0,
        "invalid_labels": invalid_labels
    }


def answer_question(query, top_k=3, strategy="fixed"):
    """Complete grounded RAG pipeline with citation validation."""

    results = retrieve_context(
        query=query,
        top_k=top_k,
        strategy=strategy
    )

    relevant_results = [
        result for result in results
        if result["similarity_score"] >= SIMILARITY_THRESHOLD
    ]

    if not relevant_results:
        return {
            "question": query,
            "answer": (
                "I cannot answer this question because "
                "the available documents do not contain "
                "sufficiently relevant information."
            ),
            "sources": [],
            "citation_validation": None,
            "refused": True
        }

    context = build_context(relevant_results)

    answer = generate_answer(
        query=query,
        context=context
    )

    citation_check = validate_citations(
        answer=answer,
        source_count=len(relevant_results)
    )

    if not citation_check["valid"]:
        answer = (
            "The generated answer contained invalid source "
            "references and was not accepted. Please try again."
        )

    return {
        "question": query,
        "answer": answer,
        "sources": relevant_results,
        "citation_validation": citation_check,
        "refused": False
    }


if __name__ == "__main__":

    question = "What are foundation models?"

    result = answer_question(
        query=question,
        top_k=3,
        strategy="fixed"
    )

    print("\n========== DOCUSENSE RAG ==========")
    print("Question:", result["question"])

    print("\n========== GENERATED ANSWER ==========")
    print(result["answer"])

    print("\n========== CITATION VALIDATION ==========")
    print(result["citation_validation"])

    print("\n========== RETRIEVED SOURCES ==========")

    for index, source in enumerate(result["sources"], start=1):
        metadata = source["metadata"]

        print(f"\n[{index}]")
        print("Source:", metadata["source"])
        print("Page:", metadata["page"])
        print("Similarity:", source["similarity_score"])
