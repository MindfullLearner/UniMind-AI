import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.docusense.src.search import search


def main():
    query = "What are the risks and challenges of generative AI?"

    for strategy in ["fixed", "sentence"]:
        print(f"\n========== {strategy.upper()} SEARCH ==========")

        results = search(
            query=query,
            top_k=3,
            strategy=strategy
        )

        for index, result in enumerate(results, start=1):
            print(f"\nResult {index}")
            print("Similarity:", result["similarity_score"])
            print("Metadata:", result["metadata"])
            print("Text:", result["text"][:300])


if __name__ == "__main__":
    main()