# Open Questions

Up: [[Home]]

Carried over from the README, still unresolved:

- Can [[Knowledge Graph]] construction be automated, or does it need a
  manual Obsidian pass first?
- What counts as "accuracy" precisely, for the [[Accuracy Judge]]'s
  held-out-20% eval — exact claim matching, semantic similarity, or
  LLM-judged faithfulness?
- [[Refutation Judge]] guidelines are explicitly TBD in the README; needs
  a system prompt / rubric before that judge can be built.
- [[PubMed]] currently uses topic-based search (shipped, 12 queries, 159
  abstracts) rather than extracting what Saladino actually cites — is
  topic search good enough long-term, or does citation extraction matter
  once accuracy eval needs source-of-truth precision?
- [[PubMed]]'s relevance-ranked search on broad query terms pulled in some
  off-topic results (e.g. veterinary studies under an "elimination diet"
  query) — worth a filtering or relevance-threshold pass before this
  corpus feeds [[Knowledge Graph]] construction?
