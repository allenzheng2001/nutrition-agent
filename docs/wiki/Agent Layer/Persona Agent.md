# Persona Agent

Up: [[Agent Layer]]

**Status: done (minimal).**

Owns the final message "as Paul Saladino" — the core of the README's
motivating question (can an influencer's persona be imbued into an
agent?).

**Code:** `src/nutrition_agent/agent/persona.py`
**CLI:** `scripts/ask.py "<question>"`

`PersonaAgent.respond(question)` retrieves the top-k chunks via
[[Context Fetcher]] (currently `BM25Index.search`), formats them into a
`CONTEXT:` block labeled by source, and fills them into the system
prompt template at `prompts/persona_system_prompt.md` — instructing the
model to answer grounded in that context, citing sources, and to say so
explicitly when the context doesn't cover the question rather than
inventing a position. Returns a `PersonaResponse` with the answer text and
the `CorpusChunk`s it was grounded in, so a caller (or [[Evaluation]]
later) can check what evidence backed the answer.

The prompt template lives outside `src/`, as a standalone file, on
purpose — see [[Agent Runtimes]] for why.

## Interface

```python
class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...
```

`AnthropicClient` (`src/nutrition_agent/agent/llm.py`) implements this
against the Claude API, defaulting to `claude-opus-5`. Kept as a narrow
protocol rather than a hardcoded Anthropic call — swapping providers or
mocking for tests means implementing one method. `tests/test_persona.py`
exercises `PersonaAgent` entirely against a stub `LLMClient`, no network
or API key required.

Requires `ANTHROPIC_API_KEY` to actually generate; not yet run
end-to-end against a real model as of this milestone. Model choice is a
cost/quality tradeoff worth revisiting for a course-budget project —
`claude-sonnet-5` is a cheaper alternative if `claude-opus-5` proves too
expensive to iterate against.

## Why this is the most important swap point

Keeping `PersonaAgent` decoupled from any specific model API matters more
here than anywhere else in the system — this is the piece most likely to
change as the project evolves, and the piece [[Evaluation]] judges most
directly.
