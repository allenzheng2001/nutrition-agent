# Context Fetcher

Up: [[Agent Layer]]

**Status: done — currently a thin wrapper over [[Knowledge Graph|BM25Index]].**

An assistant role that brings relevant context into the
[[Persona Agent]]'s prompt on demand, rather than requiring the whole
corpus to sit in context. There's no separate `ContextFetcher` class yet
— `PersonaAgent.respond()` calls `BM25Index.search(question, k)` directly.

## Interface (target shape, informally satisfied today)

```python
class ContextFetcher(Protocol):
    def fetch(self, query: str) -> list[Chunk]: ...
```

`BM25Index.search()` matches this shape closely enough (query in, ranked
chunks out) that formalizing it as its own class hasn't been necessary.
Worth doing once retrieval strategy actually needs to vary — e.g. if a
future `EmbeddingIndex` or graph-traversal fetcher gets added alongside
BM25 and [[Persona Agent]] needs to pick between them.
