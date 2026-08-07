# Sources

Up: [[Home]] · Next: [[Chunker]]

**Job:** turn a reference to a piece of content (a video ID, a PubMed ID)
into a `RawDocument` — no chunking, no cleanup beyond removing
platform-specific junk.

## Interface

```python
class RawDocument(Protocol):
    source_type: str        # "youtube" | "pubmed" | ...
    source_id: str
    title: str
    url: str
    published: str | None
    metadata: dict           # source-specific extras (channel, authors, journal...)
    text_segments: list[TextSegment]   # ordered, each with optional timing/offset

class SourceFetcher(Protocol):
    def fetch(self, ref: str) -> RawDocument: ...
```

## Why this boundary

Adding a new source should never touch [[Chunker]], [[Corpus Store]], or
anything downstream — it should mean writing one new class that returns a
`RawDocument`.

## Fetchers

| Fetcher | Status |
|---|---|
| [[YouTube]] | done |
| [[PubMed]] | done |
| [[Podcast Audio]] | deferred |
| [[Short-Form Content]] | deferred |
