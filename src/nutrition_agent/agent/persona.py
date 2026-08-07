"""PersonaAgent: answers a question grounded in retrieved corpus context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nutrition_agent.agent.llm import LLMClient
from nutrition_agent.retrieval.index import BM25Index, CorpusChunk

# Lives outside the Python package (repo root, not src/) so a runtime other
# than this codebase -- e.g. a Claude Code agent session -- can read the same
# recipe without importing nutrition_agent. See
# docs/wiki/Agent Layer/Agent Runtimes.md.
DEFAULT_PROMPT_PATH = Path(__file__).resolve().parents[3] / "prompts" / "persona_system_prompt.md"


@dataclass
class PersonaResponse:
    answer: str
    sources: list[CorpusChunk]


class PersonaAgent:
    def __init__(
        self,
        llm: LLMClient,
        index: BM25Index,
        persona_name: str = "Paul Saladino",
        top_k: int = 6,
        prompt_path: Path = DEFAULT_PROMPT_PATH,
    ):
        self.llm = llm
        self.index = index
        self.persona_name = persona_name
        self.top_k = top_k
        self.prompt_template = prompt_path.read_text()

    def respond(self, question: str) -> PersonaResponse:
        hits = self.index.search(question, k=self.top_k)
        context = _format_context(hits)
        system = self.prompt_template.format(
            persona_name=self.persona_name, context=context or "(no matching context found)"
        )
        answer = self.llm.complete(system, question)
        return PersonaResponse(answer=answer, sources=[chunk for chunk, _ in hits])


def _format_context(hits: list[tuple[CorpusChunk, float]]) -> str:
    blocks = []
    for chunk, _score in hits:
        blocks.append(f"[{chunk.title} ({chunk.source_type})]\n{chunk.text}")
    return "\n\n".join(blocks)
