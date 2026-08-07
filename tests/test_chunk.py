from nutrition_agent.ingestion.chunk import chunk_snippets, chunk_text
from nutrition_agent.ingestion.youtube import TranscriptSnippet


def test_merges_short_snippets_into_target_sized_chunks():
    snippets = [
        TranscriptSnippet(text=f"word{i}", start=float(i), duration=1.0)
        for i in range(20)
    ]
    chunks = chunk_snippets(snippets, target_chars=30)

    assert len(chunks) > 1
    # every word from the source snippets shows up, in order, exactly once
    rebuilt = " ".join(c.text for c in chunks)
    assert rebuilt == " ".join(s.text for s in snippets)


def test_chunk_start_and_end_span_its_snippets():
    snippets = [
        TranscriptSnippet(text="a", start=0.0, duration=2.0),
        TranscriptSnippet(text="b", start=2.0, duration=3.0),
    ]
    [chunk] = chunk_snippets(snippets, target_chars=1000)

    assert chunk.start_s == 0.0
    assert chunk.end_s == 5.0


def test_blank_snippets_are_skipped():
    snippets = [
        TranscriptSnippet(text="  ", start=0.0, duration=1.0),
        TranscriptSnippet(text="real text", start=1.0, duration=1.0),
    ]
    chunks = chunk_snippets(snippets, target_chars=1000)

    assert len(chunks) == 1
    assert chunks[0].text == "real text"


def test_chunk_text_short_abstract_becomes_one_chunk():
    text = "Seed oil intake has risen. More research is needed."
    [chunk] = chunk_text(text, target_chars=2500)

    assert chunk.text == text
    assert chunk.start_s is None
    assert chunk.end_s is None


def test_chunk_text_splits_long_text_on_sentence_boundaries():
    sentences = [f"This is sentence number {i}." for i in range(30)]
    text = " ".join(sentences)

    chunks = chunk_text(text, target_chars=100)

    assert len(chunks) > 1
    rebuilt = " ".join(c.text for c in chunks)
    assert rebuilt == text
