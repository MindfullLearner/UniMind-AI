
from pathlib import Path
import pymupdf  # PyMuPDF


# Find the project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder containing PDF documents
DOCUMENTS_DIR = BASE_DIR / "documents"


def load_pdf_documents():
    """
    Load PDF documents and extract text page by page.

    Returns:
        A list containing extracted text and metadata.
    """

    extracted_documents = []

    # Find all PDF files
    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DOCUMENTS_DIR}"
        )

    for pdf_path in pdf_files:

        print(f"\nProcessing: {pdf_path.name}")

        # Open PDF document
        pdf = pymupdf.open(pdf_path)

        for page_number, page in enumerate(pdf, start=1):

            # Extract text from current page
            text = page.get_text("text").strip()

            # Skip pages without extractable text
            if not text:
                print(f"Warning: Page {page_number} is empty.")
                continue

            # Store text with metadata
            extracted_documents.append({
                "text": text,
                "metadata": {
                    "source": pdf_path.name,
                    "page": page_number
                }
            })

        pdf.close()

    return extracted_documents


if __name__ == "__main__":

    documents = load_pdf_documents()

    print("\n========== INGESTION SUMMARY ==========")
    print(f"Total pages extracted: {len(documents)}")

    for document in documents:
        print(
            f"Source: {document['metadata']['source']} | "
            f"Page: {document['metadata']['page']} | "
            f"Characters: {len(document['text'])}"
        )

    print("\nDocument ingestion completed!")

    print("\n========== TEXT PREVIEW ==========")

    seen_sources = set()

    for document in documents:
        source = document["metadata"]["source"]

        if source not in seen_sources:
            seen_sources.add(source)

            print(f"\nSource: {source}")
            print(f"Page: {document['metadata']['page']}")
            print(document["text"][:300])
            print("-" * 50)
