from nutrition_agent.agent.persona import PersonaAgent
from nutrition_agent.retrieval.index import BM25Index, CorpusChunk


class StubLLM:
    def __init__(self):
        self.last_system = None
        self.last_user = None

    def complete(self, system: str, user: str) -> str:
        self.last_system = system
        self.last_user = user
        return "stubbed answer"


def _index_with_one_chunk():
    # A handful of unrelated filler chunks keep BM25 idf well-behaved --
    # see the comment in test_retrieval.py's ranking test for why a corpus
    # of one or two documents produces degenerate (negative) scores.
    target = CorpusChunk(
        source_type="youtube",
        source_id="abc123",
        chunk_id=0,
        title="Everything about seed oils",
        url="https://youtube.com/watch?v=abc123",
        text="Seed oils are high in linoleic acid and drive inflammation.",
    )
    filler = [
        CorpusChunk(
            source_type="youtube", source_id=f"filler{i}", chunk_id=0,
            title=f"Filler {i}", url=f"url-filler-{i}", text=text,
        )
        for i, text in enumerate([
            "How to make sourdough bread at home.",
            "A guide to morning sunlight and circadian rhythm.",
            "Cold plunge therapy for recovery.",
        ])
    ]
    return BM25Index([target, *filler])


def test_respond_grounds_prompt_in_retrieved_context_and_returns_sources():
    llm = StubLLM()
    agent = PersonaAgent(llm=llm, index=_index_with_one_chunk(), persona_name="Paul Saladino")

    response = agent.respond("What do you think about seed oils?")

    assert response.answer == "stubbed answer"
    assert len(response.sources) == 1
    assert response.sources[0].title == "Everything about seed oils"
    assert "Paul Saladino" in llm.last_system
    assert "Seed oils are high in linoleic acid" in llm.last_system
    assert llm.last_user == "What do you think about seed oils?"


def test_respond_on_empty_index_still_calls_llm_with_no_context_note():
    llm = StubLLM()
    agent = PersonaAgent(llm=llm, index=BM25Index([]), persona_name="Paul Saladino")

    response = agent.respond("Unrelated question")

    assert response.sources == []
    assert "no matching context found" in llm.last_system
