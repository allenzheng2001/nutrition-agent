# Corpus Store

Up: [[Home]] · Prev: [[Chunker]] · Next: [[Knowledge Graph]]

**Job:** persist normalized documents + chunks, keyed by
`(source_type, source_id)`, idempotently — re-running ingestion shouldn't
duplicate work or require re-fetching by default.

## Interface

```python
class CorpusStore(Protocol):
    def save(self, doc: RawDocument, chunks: list[Chunk]) -> None: ...
    def exists(self, source_type: str, source_id: str) -> bool: ...
    def load(self, source_type: str, source_id: str) -> tuple[RawDocument, list[Chunk]]: ...
    def list_all(self) -> Iterable[tuple[str, str]]: ...
```

## Current implementation — done

Flat JSON files, one per document, under `data/corpus/<source>/<id>.json`
(see [[Data Contracts]] for both shapes) — `data/corpus/youtube/` written
by `scripts/ingest_youtube.py`, `data/corpus/pubmed/` written by
`scripts/ingest_pubmed.py`. There's no `CorpusStore` class — each script
does its own file I/O inline, and idempotency is a path-exists check in
the CLI, not in a store abstraction. Both scripts independently
reimplement the same pattern (mkdir, exists-check, write JSON, write
`_manifest.json` summarizing ok/skipped/failed). See [[Known Gaps]] — this
is now the second real example the earlier "wait for a second example"
call was betting on, and it confirms the duplication is real and worth
factoring out.

## Swap candidates

- **SQLite** — queryable metadata (filter by channel, date range, etc.)
  without loading every JSON file.
- **Vector DB** — if chunk embeddings get stored alongside text for
  semantic retrieval, once [[Knowledge Graph]] or the agent's context
  fetcher needs similarity search.
- **Document store** (e.g. a simple key-value store) — if JSON-per-file
  starts to feel slow at corpus scale.

Any of these should be a drop-in behind `CorpusStore` without [[Sources]]
fetchers or the [[Chunker]] knowing the difference.
