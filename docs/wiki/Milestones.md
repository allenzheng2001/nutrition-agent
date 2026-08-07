# Milestones

Up: [[Home]]

End-of-week deadline. Status per module:

| Module | Status | This week? |
|---|---|---|
| [[YouTube]] fetcher | done | — |
| [[PubMed]] fetcher | done | — |
| [[Chunker]] (`chunk_snippets`, `chunk_text`) | done | — |
| [[Corpus Store]] (JSON) | done | — |
| [[Knowledge Graph]] (BM25 interim) | done (interim) | — |
| [[Agent Layer]] (`PersonaAgent`, `BM25Index`) | done (minimal) | — |
| `CorpusStore` interface extraction | designed, recommended | if time allows (see [[Known Gaps]]) |
| Full [[Knowledge Graph]] (nodes/edges) | designed | no |
| [[Evaluation]] harness | designed | no |
| End-to-end run against a real model | blocked on `ANTHROPIC_API_KEY` | next |

Current corpus: 9 YouTube videos (396 chunks, ~16 hours of transcript) +
159 PubMed abstracts (across 12 topic queries) = 564 chunks total,
indexed and searchable via `scripts/ask.py`. 13 tests passing.
