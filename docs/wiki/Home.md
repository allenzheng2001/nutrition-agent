# Nutrition Agent — Design Wiki

Companion to the [root README](../../README.md), which states the
motivating question and open subquestions. This wiki breaks the system
into modules — each one a node you can dive into independently — so any
single piece can be swapped without rewriting its neighbors.

Guiding rule: every module talks to its neighbors through a small, boring
data contract (a dataclass or a `Protocol`), never through a specific
library's native types. If a module's job could plausibly be done a
different way next month, it gets an interface now, even if today there's
only one implementation behind it.

## The pipeline

```
 Sources        Ingestion            Corpus         Knowledge        Agent Layer      Evaluation
 ───────       ───────────          ────────        ─────────        ───────────      ──────────
 [[Sources]] → [[Chunker]] → [[Corpus Store]] → [[Knowledge Graph]] → [[Agent Layer]] → [[Evaluation]]
```

Each link is an interface boundary — click through for that module's
contract, current implementation, and swap candidates.

## Status

See [[Milestones]] for the full table. Short version: everything through
[[Agent Layer]] has a working minimal version — [[Sources]] (both
[[YouTube]] and [[PubMed]]), [[Chunker]], [[Corpus Store]], a BM25
[[Knowledge Graph]] stand-in, and a [[Persona Agent]] you can run via
`scripts/ask.py`. [[Evaluation]] is designed but not started, and the
agent hasn't been run end-to-end against a real model yet — that needs
`ANTHROPIC_API_KEY`.

## Cross-cutting notes

- [[Data Contracts]] — the structs every module above agrees on today
- [[Known Gaps]] — where the shipped code doesn't yet match the interfaces
  described here, and why that's currently OK
- [[Open Questions]] — unresolved questions carried over from the README
