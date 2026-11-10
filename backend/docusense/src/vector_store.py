
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "chroma_db"

# Initialize persistent ChromaDB
client = chromadb.PersistentClient(path=str(DB_DIR))

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# Separate collection for each chunking strategy
COLLECTION_NAMES = {
    "fixed": "documents_fixed",
    "sentence": "documents_sentence"
}


def get_collection(strategy):
    """Get or create a collection for the selected strategy."""

    if strategy not in COLLECTION_NAMES:
        raise ValueError("Invalid chunking strategy")

    collection_name = COLLECTION_NAMES[strategy]

    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


def store_chunks(chunks, strategy):
    """Generate embeddings and store chunks in ChromaDB."""

    collection = get_collection(strategy)

    # Clear previous records so ingestion can be repeated safely.
    collection.delete(where={"strategy": strategy})

    batch_size = 100

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]

        texts = [item["text"] for item in batch]

        metadatas = [
            item["metadata"] for item in batch
        ]

        ids = [
            (
                f"{item['metadata']['source']}"
                f"_page_{item['metadata']['page']}"
                f"_{strategy}_chunk_{item['metadata']['chunk_index']}"
            )
            for item in batch
        ]

        # Convert text into numerical vectors.
        embeddings = embedding_model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    print(f"\nStored {len(chunks)} chunks in {strategy} collection.")

    return collection


def get_collection_count(strategy):
    """Return the number of stored chunks."""

    collection = get_collection(strategy)

    return collection.count()



if __name__ == "__main__":

    from ingest import load_pdf_documents
    from chunking import chunk_documents

    print("Loading PDF documents...")

    documents = load_pdf_documents()

    print("\nGenerating fixed-size chunks...")
    fixed_chunks = chunk_documents(
        documents,
        strategy="fixed"
    )

    print("\nGenerating sentence-based chunks...")
    sentence_chunks = chunk_documents(
        documents,
        strategy="sentence"
    )

    print("\n========== STORING IN CHROMADB ==========")

    store_chunks(fixed_chunks, "fixed")
    store_chunks(sentence_chunks, "sentence")

    print("\n========== DATABASE SUMMARY ==========")

    print(
        "Fixed-size records:",
        get_collection_count("fixed")
    )

    print(
        "Sentence-based records:",
        get_collection_count("sentence")
    )

    print("\nVector database ingestion completed!")
