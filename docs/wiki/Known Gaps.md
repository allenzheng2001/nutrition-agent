# Known Gaps

Up: [[Home]]

Written honestly, after the fact: where the shipped ingestion code
doesn't yet match the module interfaces described in this wiki.

1. Neither [[YouTube]] nor [[PubMed]]'s fetcher implements the generic
   `SourceFetcher`/`RawDocument` shape from [[Sources]] — they return
   their own `VideoRecord` and `PubMedRecord` dataclasses respectively.
2. [[Chunker]] has two free functions (`chunk_snippets`, `chunk_text`),
   not a class implementing the `Chunker` protocol. They do already share
   one thing in common: both return the same `Chunk` dataclass.
3. There's still no `CorpusStore` class — `scripts/ingest_youtube.py` and
   `scripts/ingest_pubmed.py` each write JSON files directly and each do
   their own exists-check for idempotency, rather than going through a
   shared [[Corpus Store]] interface.

## Status of the earlier decision point

The previous version of this page deferred retrofitting these interfaces
until there was "a second real example to generalize from" rather than
just one. That second example now exists — [[PubMed]] is built, and it
duplicated the same fetch → chunk → write-JSON-with-manifest loop that
[[YouTube]]'s CLI script already had, confirming the duplication
prediction rather than revealing a different shape than expected.

**Recommendation, updated:** worth factoring out `CorpusStore` now — both
scripts already agree on what it needs to do (mkdir, exists-check, save,
manifest), so there's no real design risk left in extracting it. The
`SourceFetcher`/`RawDocument` and `Chunker` interfaces are less urgent:
`VideoRecord` and `PubMedRecord` are different enough (timed vs. untimed,
different metadata) that forcing them into one shape now might be the
premature generalization the "wait for two examples" rule was trying to
avoid. Revisit once [[Knowledge Graph]] or the [[Agent Layer]] needs to
read from both corpora uniformly — that's the point a shared `RawDocument`
actually starts paying for itself.
