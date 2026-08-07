import json

from nutrition_agent.retrieval.index import BM25Index, load_corpus


def _write_doc(path, title, url, chunks):
    path.write_text(json.dumps({"title": title, "url": url, "chunks": chunks}))


def test_load_corpus_reads_chunks_across_sources(tmp_path):
    yt_dir = tmp_path / "youtube"
    pm_dir = tmp_path / "pubmed"
    yt_dir.mkdir()
    pm_dir.mkdir()

    _write_doc(
        yt_dir / "abc123.json",
        "Seed oils are terrible",
        "https://youtube.com/watch?v=abc123",
        [{"chunk_id": 0, "start_s": 0.0, "end_s": 10.0, "text": "Seed oils cause inflammation."}],
    )
    _write_doc(
        pm_dir / "999.json",
        "A review of linoleic acid",
        "https://pubmed.ncbi.nlm.nih.gov/999/",
        [{"chunk_id": 0, "start_s": None, "end_s": None, "text": "Linoleic acid intake and heart disease."}],
    )
    (pm_dir / "_manifest.json").write_text("{}")

    chunks = load_corpus(tmp_path)

    assert len(chunks) == 2
    by_source = {c.source_type for c in chunks}
    assert by_source == {"youtube", "pubmed"}
    yt_chunk = next(c for c in chunks if c.source_type == "youtube")
    assert yt_chunk.source_id == "abc123"
    assert yt_chunk.start_s == 0.0


def test_bm25_search_ranks_relevant_chunk_first(tmp_path):
    # BM25 idf goes degenerate on a two-document corpus (a term in every
    # document scores negative), so a handful of unrelated filler docs are
    # needed for "beef"/"grass" to read as the rare, discriminating terms
    # they'd actually be in a real corpus.
    src = tmp_path / "youtube"
    src.mkdir()
    _write_doc(
        src / "v1.json", "Video 1", "url1",
        [{"chunk_id": 0, "start_s": 0.0, "end_s": 1.0, "text": "Grass fed beef is nutrient dense and healthy."}],
    )
    for i, text in enumerate([
        "How to make sourdough bread at home.",
        "A guide to morning sunlight and circadian rhythm.",
        "Cold plunge therapy for recovery.",
        "The history of the sauna in Finland.",
    ]):
        _write_doc(src / f"filler{i}.json", f"Filler {i}", f"url-filler-{i}",
                    [{"chunk_id": 0, "start_s": 0.0, "end_s": 1.0, "text": text}])

    index = BM25Index(load_corpus(tmp_path))
    results = index.search("grass fed beef nutrients", k=5)

    assert results
    top_chunk, top_score = results[0]
    assert top_chunk.title == "Video 1"
    assert top_score > 0


def test_bm25_search_on_empty_corpus_returns_nothing():
    index = BM25Index([])
    assert index.search("anything") == []
