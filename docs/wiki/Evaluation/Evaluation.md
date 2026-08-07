# Evaluation

Up: [[Home]] · Prev: [[Agent Layer]]

**Status: designed, not built.**

Two judge roles from the README, both structurally the same shape (a
judge scores a `(generated_text, reference_material)` pair) so they share
one interface:

```python
class EvalResult:
    score: float
    rationale: str

class Judge(Protocol):
    def score(self, generated: str, reference: list[Chunk]) -> EvalResult: ...
```

| Judge | Status |
|---|---|
| [[Accuracy Judge]] | designed |
| [[Refutation Judge]] | designed, guidelines TBD |

Both consume the [[Persona Agent]]'s output and score it against material
drawn from [[Corpus Store]] / [[Knowledge Graph]].
