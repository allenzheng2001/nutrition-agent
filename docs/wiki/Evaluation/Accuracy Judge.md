# Accuracy Judge

Up: [[Evaluation]]

**Status: designed, not built.**

Holds out ~20% of the corpus, generates answers with the [[Persona Agent]]
over the remaining 80%, and scores consistency with the original source
material — a "neutral evaluation agent whose sole goal is to determine
accuracy to the original source content set, not what the model is
actually tuned towards" (per the README).

## Baselines to compare against

Each baseline is a different [[Agent Runtimes|runtime]] running (or
deliberately not running) the same persona recipe:

- **Our `PersonaAgent`** — the recipe as direct API code + `BM25Index`.
- **A Claude Code agent session** — the same recipe, but with the model
  reading `data/corpus/*/` directly via real file tools instead of
  `BM25Index`. Cheap to stand up since it's the tool already in use to
  build this project; also a check that the persona survives a change of
  retrieval mechanism.
- **Base model with no retrieved context** — just pretrained knowledge of
  Saladino, no persona instructions, no corpus.
- **A generic "deep research"-style agent**, not tailored to this corpus.

This comparison is what answers "why is your structure of knowledge
storage any better than base ChatGPT?" — the core justification for
building [[Knowledge Graph]] and [[Corpus Store]] at all rather than
just prompting a base model.

## Open question

See [[Open Questions]] — what counts as "accuracy" precisely: exact claim
matching, semantic similarity, or LLM-judged faithfulness?
