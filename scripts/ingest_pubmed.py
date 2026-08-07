#!/usr/bin/env python3
"""CLI: search PubMed for a list of queries, fetch abstracts, chunk them,
and write one normalized JSON file per PMID into data/corpus/pubmed/.

Usage:
    python scripts/ingest_pubmed.py --seeds data/seeds/pubmed_queries.txt
"""

from __future__ import annotations

import argparse
import dataclasses
import json
from datetime import datetime, timezone
from pathlib import Path

from nutrition_agent.ingestion.chunk import chunk_text
from nutrition_agent.ingestion.pubmed import fetch_abstracts, search_pubmed

REPO_ROOT = Path(__file__).resolve().parent.parent
EFETCH_BATCH_SIZE = 50


def read_seed_lines(seed_file: Path) -> list[str]:
    lines = []
    for line in seed_file.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def batched(items: list[str], size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seeds",
        type=Path,
        default=REPO_ROOT / "data" / "seeds" / "pubmed_queries.txt",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "data" / "corpus" / "pubmed",
    )
    parser.add_argument(
        "--retmax", type=int, default=15, help="Max results per query"
    )
    parser.add_argument(
        "--force", action="store_true", help="Re-fetch PMIDs that already have output"
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    queries = read_seed_lines(args.seeds)

    pmid_to_queries: dict[str, set[str]] = {}
    for query in queries:
        pmids = search_pubmed(query, retmax=args.retmax)
        print(f"search '{query}' -> {len(pmids)} ids")
        for pmid in pmids:
            pmid_to_queries.setdefault(pmid, set()).add(query)

    all_pmids = list(pmid_to_queries)
    to_fetch = [
        pmid
        for pmid in all_pmids
        if args.force or not (args.out / f"{pmid}.json").exists()
    ]
    skipped = [pmid for pmid in all_pmids if pmid not in to_fetch]
    for pmid in skipped:
        print(f"skip  {pmid} (already fetched)")

    records = []
    for batch in batched(to_fetch, EFETCH_BATCH_SIZE):
        records.extend(fetch_abstracts(batch))

    fetched_ids = set()
    for record in records:
        chunks = chunk_text(record.abstract)
        doc = {
            "pmid": record.pmid,
            "title": record.title,
            "journal": record.journal,
            "year": record.year,
            "authors": record.authors,
            "url": record.url,
            "source_queries": sorted(pmid_to_queries[record.pmid]),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "chunks": [dataclasses.asdict(c) for c in chunks],
        }
        (args.out / f"{record.pmid}.json").write_text(
            json.dumps(doc, indent=2, ensure_ascii=False)
        )
        print(f"ok    {record.pmid}  {len(chunks)} chunks  {record.title[:70]!r}")
        fetched_ids.add(record.pmid)

    failed = [pmid for pmid in to_fetch if pmid not in fetched_ids]
    for pmid in failed:
        print(f"FAIL  {pmid}  no usable abstract returned")

    manifest_path = args.out / "_manifest.json"
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queries": queries,
        "ok": sorted(fetched_ids),
        "skipped": skipped,
        "failed": failed,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))

    print(f"\n{len(fetched_ids)} ok, {len(skipped)} skipped, {len(failed)} failed")
    return 1 if failed and not fetched_ids else 0


if __name__ == "__main__":
    raise SystemExit(main())
