
import re


def fixed_size_chunk(text, chunk_size=500, overlap=50):
    """Create approximately fixed-size chunks without splitting words."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk_size")

    text = re.sub(r"\s+", " ", text.strip())

    chunks = []
    start = 0

    while start < len(text):
        limit = min(start + chunk_size, len(text))
        end = limit

        # End the chunk at a word boundary.
        if limit < len(text):
            boundary = text.rfind(" ", start, limit)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        # Move backwards to preserve overlap, then align to a word.
        next_start = max(start + 1, end - overlap)
        next_space = text.find(" ", next_start, end)

        if next_space != -1:
            next_start = next_space + 1
        else:
            next_start = end

        start = next_start

    return chunks


def sentence_based_chunk(text, chunk_size=500):
    """Group complete sentences into chunks."""

    text = re.sub(r"\s+", " ", text.strip())

    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current_sentences = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        added_length = len(sentence)

        if current_sentences:
            added_length += 1  # Space between sentences

        if current_sentences and current_length + added_length > chunk_size:
            chunks.append(" ".join(s.strip() for s in current_sentences))
            current_sentences = [sentence]
            current_length = len(sentence)
        else:
            current_sentences.append(sentence)
            current_length += added_length

    if current_sentences:
        chunks.append(" ".join(s.strip() for s in current_sentences))

    return chunks

def chunk_documents(documents, strategy="fixed"):
    """
    Chunk extracted PDF pages and preserve their metadata.
    """

    chunked_documents = []

    for document in documents:
        text = document["text"]
        original_metadata = document["metadata"]

        if strategy == "fixed":
            chunks = fixed_size_chunk(
                text,
                chunk_size=500,
                overlap=50
            )

        elif strategy == "sentence":
            chunks = sentence_based_chunk(
                text,
                chunk_size=500
            )

        else:
            raise ValueError(
                "Strategy must be 'fixed' or 'sentence'"
            )

        for index, chunk in enumerate(chunks, start=1):
            chunked_documents.append({
                "text": chunk,
                "metadata": {
                    **original_metadata,
                    "strategy": strategy,
                    "chunk_index": index
                }
            })

    return chunked_documents



if __name__ == "__main__":

    from ingest import load_pdf_documents

    documents = load_pdf_documents()

    fixed_chunks = chunk_documents(
        documents,
        strategy="fixed"
    )

    sentence_chunks = chunk_documents(
        documents,
        strategy="sentence"
    )

    print("\n========== CHUNKING SUMMARY ==========")

    print(f"Original pages: {len(documents)}")
    print(f"Fixed-size chunks: {len(fixed_chunks)}")
    print(f"Sentence-based chunks: {len(sentence_chunks)}")

    print("\n========== FIXED-SIZE PREVIEW ==========")

    for chunk in fixed_chunks[:3]:
        print("\nMetadata:", chunk["metadata"])
        print("Text:", chunk["text"][:200])

    print("\n========== SENTENCE-BASED PREVIEW ==========")

    for chunk in sentence_chunks[:3]:
        print("\nMetadata:", chunk["metadata"])
        print("Text:", chunk["text"][:200])
