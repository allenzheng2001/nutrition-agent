#!/usr/bin/env python3
"""CLI: ask the persona agent a question, grounded in the ingested corpus.

Usage:
    python scripts/ask.py "What do you think about seed oils?"

Requires ANTHROPIC_API_KEY to be set.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from nutrition_agent.agent.llm import DEFAULT_MODEL, AnthropicClient
from nutrition_agent.agent.persona import PersonaAgent
from nutrition_agent.retrieval.index import BM25Index, load_corpus

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question")
    parser.add_argument(
        "--corpus", type=Path, default=REPO_ROOT / "data" / "corpus"
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--top-k", type=int, default=6)
    args = parser.parse_args()

    chunks = load_corpus(args.corpus)
    if not chunks:
        print(f"No corpus found under {args.corpus} -- run the ingest scripts first.")
        return 1

    index = BM25Index(chunks)
    agent = PersonaAgent(
        llm=AnthropicClient(model=args.model), index=index, top_k=args.top_k
    )

    response = agent.respond(args.question)
    print(response.answer)
    print("\n--- sources ---")
    for chunk in response.sources:
        print(f"- {chunk.title} ({chunk.source_type}) {chunk.url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
