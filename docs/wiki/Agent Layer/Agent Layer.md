# Agent Layer

Up: [[Home]] · Prev: [[Knowledge Graph]] · Next: [[Evaluation]]

**Status: minimal version done.**

Per the README's system design sketch, splits into two roles:

| Component | Status |
|---|---|
| [[Persona Agent]] | done (minimal) |
| [[Context Fetcher]] | done — currently just [[Knowledge Graph|BM25Index.search]] |
| [[Agent Runtimes]] | designed |

The context fetcher pulls relevant material from the corpus (via
[[Knowledge Graph]]'s `BM25Index`) on demand rather than stuffing the
whole corpus into one context window; the [[Persona Agent]] owns the
final message "as Paul Saladino," consuming whatever context gets
fetched. `scripts/ask.py` wires both together into a runnable CLI.

**Design note:** the persona instructions + retrieval access are meant to
be portable across more than one execution engine — see
[[Agent Runtimes]] for why, and for how this feeds directly into
[[Evaluation]]'s baseline comparisons.
