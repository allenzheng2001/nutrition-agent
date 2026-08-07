# Agent Runtimes

Up: [[Agent Layer]] · See also: [[Evaluation]]

**Status: the recipe is now portable; a second runtime is still not
built.** Design decision made 2026-08-05.

## The insight

The actual IP of this project isn't the Python code that calls the
Anthropic API — it's the **recipe**: the persona system prompt (how to
answer grounded in Saladino's corpus, cite sources, admit gaps rather than
invent positions — see [[Persona Agent]]) plus the **retrieval access**
(the corpus under `data/corpus/*/`, queryable via [[Knowledge Graph]]'s
`BM25Index`, or just directly readable/greppable as files). That recipe
should be able to run on more than one execution engine — a "runtime" —
without changing what it's asking the model to do.

## Why this matters for evaluation

The README's evaluation plan (see [[Accuracy Judge]]) needs multiple
comparison arms:
- The recipe run as our own code (direct API call, BM25 retrieval)
- A base model with no retrieval, no persona instructions — pretrained
  knowledge only
- A "deep research"-style agent, not tailored to this corpus

**New addition to that list, from this design discussion:** run the same
recipe *as a Claude Code agent session* — given the repo (so it can read
`data/corpus/*/` directly with real file tools, `grep`/`read` rather than
going through `BM25Index`) and the persona instructions as its system
prompt / project context. This is cheap to set up precisely because
Claude Code is already the tool being used to build this project, and it
gives a second, architecturally-different implementation of the same
recipe to compare against the first — useful both as an evaluation arm
and as a sanity check that the recipe itself (not our specific retrieval
code) is what's carrying the persona.

## Candidate runtimes

| Runtime | What it is | Status |
|---|---|---|
| `PersonaAgent` (direct API) | Our code: `BM25Index.search()` + a system prompt + one `messages.create()` call | built, see [[Persona Agent]] |
| Claude Code agent session | Claude Code pointed at this repo, given the persona instructions as context, using real file tools against `data/corpus/*/` instead of `BM25Index` | not built |
| Base model, no context | Same persona instructions, no retrieval at all — pretrained knowledge of Saladino only | not built |
| Deep-research-style agent | Generic web-research agent, not tuned to this corpus | not built |

## Done: the recipe is extracted

`prompts/persona_system_prompt.md` — a standalone file at the repo root
(deliberately outside `src/`), not a Python string constant. Any runtime
can read it without importing `nutrition_agent`: [[Persona Agent]] loads
it via `Path.read_text()` and `.format()`s in `persona_name`/`context`;
a future Claude Code agent session pointed at this repo could read the
same file directly as part of its own instructions.

## Still not built: a second runtime

The table above is otherwise unchanged. Building the Claude Code
agent-session runtime itself — actually spinning up a session against
this repo's corpus and comparing its answers to `PersonaAgent`'s — is a
separate, larger piece of work than the prompt extraction, and hasn't
been started. Worth confirming it's worth the time before the deadline
vs. spending that time on [[Evaluation]] harness basics.
