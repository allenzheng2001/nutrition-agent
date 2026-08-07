# Chunker

Up: [[Home]] · Prev: [[Sources]] · Next: [[Corpus Store]]

**Job:** turn a `RawDocument`'s segments into `Chunk`s sized for
retrieval — long enough to carry standalone meaning, short enough to
embed/retrieve precisely, each still traceable back to its position in
the source.

## Interface

```python
@dataclass
class Chunk:
    chunk_id: int
    start_s: float | None    # None for non-timed sources like PubMed
    end_s: float | None
    text: str

class Chunker(Protocol):
    def chunk(self, doc: RawDocument, target_chars: int) -> list[Chunk]: ...
```

## Current implementation — done

Two free functions in `src/nutrition_agent/ingestion/chunk.py`, neither
yet a class implementing the `Chunker` protocol above — see
[[Known Gaps]]:

- `chunk_snippets()` — greedy merge of consecutive [[YouTube]] caption
  snippets up to `target_chars` (default 2500), preserving the timestamp
  span. Operates on `TranscriptSnippet`, the YouTube-specific type.
- `chunk_text()` — greedy merge of sentences up to `target_chars`, for
  untimed sources like [[PubMed]] abstracts. `start_s`/`end_s` are `None`
  since there's no timestamp span to preserve. Most abstracts are well
  under `target_chars` and come back as a single chunk.

Both share the same `Chunk` dataclass (`chunk_id`, `start_s`, `end_s`,
`text`), which is the one piece of the target `Chunker` interface that's
already common across sources.

Tested in `tests/test_chunk.py`: ordering/completeness of merged text,
correct start/end span, blank-snippet skipping, sentence-boundary
splitting.

## Swap candidates

Not believed to be final — chosen for speed on a deadline:

- **Semantic/topic-boundary chunking** — split where sentence-embedding
  similarity drops, rather than at a raw character count.
- **Speaker-turn-aware chunking** — once transcripts carry diarization
  (relevant for interview-format sources where multiple speakers talk),
  chunk on speaker turns rather than mid-sentence.
