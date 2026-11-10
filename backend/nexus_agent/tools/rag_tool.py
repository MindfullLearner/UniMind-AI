
from langchain_core.tools import tool




from backend.docusense.src.rag import answer_question


@tool
def rag_search(query: str) -> str:
    """Search the existing DocuSense document knowledge base.

    Use this tool when the user asks questions about information
    contained in the ingested documents, or asks to find document-based
    facts, explanations, or references.
    """

    try:
        result = answer_question(
            query=query,
            top_k=3,
            strategy="fixed"
        )

        answer = result.get("answer", "No answer was generated.")

        if result.get("refused"):
            return f"No sufficiently relevant document information found.\n{answer}"

        output = [f"Document-based answer:\n{answer}"]

        sources = result.get("sources", [])

        if sources:
            output.append("\nSources:")

            for index, source in enumerate(sources, start=1):
                metadata = source.get("metadata", {})
                source_name = (
                    metadata.get("source")
                    or metadata.get("file_name")
                    or metadata.get("filename")
                    or "Document source"
                )

                score = source.get("similarity_score", "N/A")

                output.append(
                    f"{index}. {source_name} "
                    f"(similarity: {score})"
                )

        return "\n".join(output)

    except Exception as error:
        return f"RAG search error: {type(error).__name__}: {error}"
