
from .vector_store import embedding_model, get_collection


def search(query, top_k=5, strategy="fixed"):
    """
    Search relevant document chunks using semantic similarity.

    Args:
        query: User's search query.
        top_k: Number of results to return.
        strategy: 'fixed' or 'sentence'.

    Returns:
        List of relevant chunks with metadata and similarity scores.
    """

    if not query.strip():
        raise ValueError("Search query cannot be empty")

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    collection = get_collection(strategy)

    total_records = collection.count()

    if total_records == 0:
        return []

    # Convert user query into an embedding.
    query_embedding = embedding_model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Search ChromaDB for the nearest vectors.
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=min(top_k, total_records),
        include=["documents", "metadatas", "distances"]
    )

    search_results = []

    for i in range(len(results["ids"][0])):

        distance = results["distances"][0][i]

        # ChromaDB cosine distance = 1 - cosine similarity.
        similarity = 1 - distance

        search_results.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "similarity_score": round(similarity, 4)
        })

    return search_results


if __name__ == "__main__":

    query = "What are foundation models?"

    print(f"\nSearch query: {query}")

    results = search(
        query=query,
        top_k=3,
        strategy="fixed"
    )

    print("\n========== SEARCH RESULTS ==========")

    for index, result in enumerate(results, start=1):

        print(f"\nResult {index}")

        print("Source:", result["metadata"]["source"])
        print("Page:", result["metadata"]["page"])
        print("Strategy:", result["metadata"]["strategy"])

        print("Similarity score:", result["similarity_score"])

        print("Text:", result["text"][:300])
