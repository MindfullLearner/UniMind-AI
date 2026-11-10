from pathlib import Path
import chromadb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_DIR = PROJECT_ROOT / "backend" / "docusense" / "chroma_db"

EXPECTED_COLLECTIONS = [
    "documents_fixed",
    "documents_sentence",
]

def main():
    print("Database path:", DB_DIR)

    if not DB_DIR.exists():
        print("ERROR: ChromaDB directory does not exist.")
        return

    client = chromadb.PersistentClient(path=str(DB_DIR))

    existing = client.list_collections()
    existing_names = {
        item if isinstance(item, str) else item.name
        for item in existing
    }

    print("\n========== CHROMADB SUMMARY ==========")

    for name in EXPECTED_COLLECTIONS:
        if name in existing_names:
            collection = client.get_collection(name)
            print(f"{name}: {collection.count()} records")
        else:
            print(f"{name}: NOT FOUND")

    print("\nDatabase verification completed.")

if __name__ == "__main__":
    main()
