"""CLI: crawl official sources and ingest into Chroma."""
from __future__ import annotations

import argparse

from backend.rag.ingest_web import ingest_web
from backend.rag.ingest_youth import ingest_youth_qa


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl & ingest official Muungano sources")
    parser.add_argument("--youth", action="store_true", help="Ingest youth Q&A only")
    parser.add_argument("--crawl-all", action="store_true", help="Crawl full allowlist + follow links")
    parser.add_argument("--url", action="append", default=[], help="Specific URL(s) to fetch")
    args = parser.parse_args()

    if args.youth:
        print("Ingesting youth Q&A …")
        print(ingest_youth_qa())
        return

    print("Ingesting web sources …")
    result = ingest_web(urls=args.url or None, crawl_all=args.crawl_all or not args.url)
    print(result)


if __name__ == "__main__":
    main()
