# Knowledge Graph

Up: [[Home]] · Prev: [[Corpus Store]] · Next: [[Agent Layer]]

**Status: interim implementation shipped; the graph itself is still designed, not built.**

**Job:** organize chunks into the "wiki of him" the README asks for —
nodes for topics/claims/chunks, edges for relations (supports, cites,
contradicts, elaborates), so retrieval can pull a neighborhood of related
context instead of just top-k similar chunks.

## Interface (target design)

```python
class GraphBuilder(Protocol):
    def build(self, corpus: CorpusStore) -> KnowledgeGraph: ...

class KnowledgeGraph(Protocol):
    def neighbors(self, node_id: str, relation: str | None = None) -> list[Node]: ...
    def search(self, query: str, k: int) -> list[Node]: ...
```

## What's actually running today: `BM25Index`

`src/nutrition_agent/retrieval/index.py` — a flat BM25 keyword index over
every chunk from both [[YouTube]] and [[PubMed]], source-agnostic. No
nodes, no edges, no relations — `load_corpus()` reads every JSON file
under `data/corpus/*/`, `BM25Index.search(query, k)` ranks chunks by
`rank_bm25`'s Okapi BM25 score. This is what [[Agent Layer]]'s context
fetcher actually calls; it satisfies the `search()` half of the
`KnowledgeGraph` interface above and nothing else.

Chosen over an embedding-based vector index for the same reason
[[Chunker]]'s greedy strategy was chosen: no external API dependency, no
cost, works entirely offline, and was fast to stand up against a
deadline. Tested in `tests/test_retrieval.py`.

**Known quirk:** BM25's idf formula goes degenerate (negative scores) on
very small corpora — a term appearing in most/all documents scores
negatively. Irrelevant on the real corpus (564 chunks), but worth knowing
if this index is ever pointed at a tiny test fixture or an early,
sparsely-populated corpus.

## Open question (from the README, still open)

Can graph construction be automated — LLM-assisted node/edge extraction
over [[Chunker|chunks]] — or does it need a manual pass in Obsidian
first? The BM25 index is a deliberately simple placeholder for this;
revisit once retrieval quality (not availability) becomes the
bottleneck — e.g. once [[Evaluation]] shows BM25 keyword overlap missing
semantically related claims that don't share vocabulary.
