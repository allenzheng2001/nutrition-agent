# PubMed Fetcher

Up: [[Sources]]

**Status: done.**

Uses NCBI's E-utilities REST API (`esearch` + `efetch`) — stable,
documented, no scraping fragility, unlike PDF-based full-text parsing.

**Code:** `src/nutrition_agent/ingestion/pubmed.py`
**CLI:** `scripts/ingest_pubmed.py`, driven by
`data/seeds/pubmed_queries.txt`

`search_pubmed(query, retmax)` runs one `esearch` call per seed query and
returns ranked PMIDs; `fetch_abstracts(pmids)` batches up to
`EFETCH_BATCH_SIZE` (50) IDs per `efetch` call and parses the returned XML
into `PubMedRecord` (pmid, title, abstract, journal, year, authors, url).
Requests are throttled to stay under NCBI's ~3 req/sec guidance for
unauthenticated use.

Scope, as planned: **abstracts only**. Full-text is often paywalled and
would need a PDF parser; abstracts are enough to ground the "related
studies" side of the corpus for now. Records with no abstract text
(editorials, letters) are skipped rather than stored empty.

Returns its own `PubMedRecord`, not yet the generic `RawDocument` — same
gap as [[YouTube]]'s `VideoRecord`. See [[Known Gaps]].

## Seed corpus (current)

12 topic queries in `data/seeds/pubmed_queries.txt`, chosen to cover both
supportive and contradicting literature around Saladino's
animal-based/carnivore claims (red meat & cardiovascular risk, saturated
fat, seed oils/omega-6, plant toxins, TMAO, dietary cholesterol, gut
microbiome & fiber, ketogenic diet, elimination diets) — useful for
grounding the agent *and* for the [[Refutation Judge]] use case in the
README.

159 abstracts ingested (top 15 results per query, deduped by PMID), 4
failed (no usable abstract returned — likely non-English or
abstract-less record types), 1 query ("plant toxins oxalates lectins
phytates digestion") returned 0 results — too narrow as a single
combined query, worth splitting later. Output: one JSON file per PMID in
`data/corpus/pubmed/<pmid>.json`, each chunked via
[[Chunker#chunk_text|chunk_text]] (nearly all abstracts fit in a single
chunk), plus a `_manifest.json`.

## Known noise

Relevance-ranked search on broad terms (e.g. "elimination diet
autoimmune disease") pulled in some off-topic veterinary-diet studies
(dogs/cats). Not fatal for MVP — flagging here so a future filtering or
relevance-threshold pass knows to look for it.

## Open question (unresolved)

How should PubMed IDs ultimately be selected — studies Saladino cites
directly (would need reference extraction from his content), or the
broader topic-based search used here? The topic-search approach shipped
first because it needed no discovery step beyond a static query list,
same reasoning [[YouTube]]'s static video-ID list used.
