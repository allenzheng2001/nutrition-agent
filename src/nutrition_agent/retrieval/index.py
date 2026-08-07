"""Load the ingested corpus and search it with BM25 keyword retrieval.

This stands in for the README's "retrieval graph" for the current milestone --
a flat keyword index over every chunk, source-agnostic. See
docs/wiki/Knowledge Graph/Knowledge Graph.md for how this relates to the
fuller graph-structured design.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from rank_bm25 import BM25Okapi

_TOKEN_RE = re.compile(r"[a-z0-9']+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


@dataclass
class CorpusChunk:
    source_type: str  # "youtube" | "pubmed"
    source_id: str
    chunk_id: int
    title: str
    url: str
    text: str
    start_s: float | None = None
    end_s: float | None = None


def load_corpus(corpus_dir: Path) -> list[CorpusChunk]:
    chunks: list[CorpusChunk] = []
    for source_dir in sorted(p for p in corpus_dir.iterdir() if p.is_dir()):
        source_type = source_dir.name
        for doc_path in sorted(source_dir.glob("*.json")):
            if doc_path.name == "_manifest.json":
                continue
            doc = json.loads(doc_path.read_text())
            for c in doc.get("chunks", []):
                chunks.append(
                    CorpusChunk(
                        source_type=source_type,
                        source_id=doc_path.stem,
                        chunk_id=c["chunk_id"],
                        title=doc.get("title", ""),
                        url=doc.get("url", ""),
                        text=c["text"],
                        start_s=c.get("start_s"),
                        end_s=c.get("end_s"),
                    )
                )
    return chunks


class BM25Index:
    def __init__(self, chunks: list[CorpusChunk]):
        self.chunks = chunks
        self._bm25 = BM25Okapi([_tokenize(c.text) for c in chunks]) if chunks else None

    def search(self, query: str, k: int = 6) -> list[tuple[CorpusChunk, float]]:
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(zip(self.chunks, scores), key=lambda pair: pair[1], reverse=True)
        return [(chunk, score) for chunk, score in ranked[:k] if score > 0]
