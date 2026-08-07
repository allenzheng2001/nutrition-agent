# Data Contracts

Up: [[Home]]

The structs that are authoritative today — what [[Sources]] and
[[Chunker]] actually produce right now, as opposed to the generic
`RawDocument`/`Chunk` protocols each module page sketches for the
target state.

```python
TranscriptSnippet(text: str, start: float, duration: float)    # raw YouTube caption unit
PubMedRecord(pmid, title, abstract, journal, year, authors, url)  # raw PubMed record
Chunk(chunk_id: int, start_s: float | None, end_s: float | None, text: str)  # merged, retrieval-sized, shared by both sources
```

## Corpus JSON shapes

[[YouTube]] — `data/corpus/youtube/<video_id>.json`:

```json
{
  "video_id": "...", "title": "...", "channel": "...", "channel_id": "...",
  "url": "...", "upload_date": "...", "duration_s": 0,
  "transcript_language": "en", "transcript_is_generated": true,
  "fetched_at": "...", "chunks": [{"chunk_id": 0, "start_s": 0.0, "end_s": 0.0, "text": "..."}]
}
```

[[PubMed]] — `data/corpus/pubmed/<pmid>.json`:

```json
{
  "pmid": "...", "title": "...", "journal": "...", "year": "...",
  "authors": ["Last F", "..."], "url": "...", "source_queries": ["..."],
  "fetched_at": "...", "chunks": [{"chunk_id": 0, "start_s": null, "end_s": null, "text": "..."}]
}
```

Both share `chunks` (the `Chunk` shape) and roughly `title`/`url`/
`fetched_at`, but everything else is source-specific (video_id/channel vs.
pmid/journal/authors). That overlap-vs-difference is exactly what [[Known
Gaps]] uses to decide whether a generic `RawDocument` envelope is worth
building yet.

## Retrieval and agent structs

```python
CorpusChunk(source_type, source_id, chunk_id, title, url, text, start_s, end_s)  # a Chunk + its source metadata, flattened for retrieval
PersonaResponse(answer: str, sources: list[CorpusChunk])  # what PersonaAgent.respond() returns
```

`CorpusChunk` (`src/nutrition_agent/retrieval/index.py`) is what
`load_corpus()` produces by reading every JSON file under
`data/corpus/*/` and flattening each document's `chunks` back out with
the parent document's `title`/`url`/`source_type`/`source_id` attached —
this is the point where the two source-specific JSON shapes above
converge into one type. See [[Knowledge Graph]] and [[Persona Agent]].
