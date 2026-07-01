"""CLI: ingest PDFs into vector database."""
from backend.rag.ingest import ingest_pdfs

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    result = ingest_pdfs(reset=args.reset)
    print(result)
