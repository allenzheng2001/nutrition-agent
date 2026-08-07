"""Merge raw source content into larger, retrieval-sized text chunks."""

from __future__ import annotations

import re
from dataclasses import dataclass

from nutrition_agent.ingestion.youtube import TranscriptSnippet

TARGET_CHARS = 2500

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    chunk_id: int
    start_s: float | None
    end_s: float | None
    text: str


def chunk_snippets(
    snippets: list[TranscriptSnippet], target_chars: int = TARGET_CHARS
) -> list[Chunk]:
    """Greedily merge consecutive caption snippets into ~target_chars chunks.

    Captions arrive as short (few-second) fragments; grouping them keeps each
    chunk long enough to carry standalone meaning for retrieval while still
    tracking the timestamp range it came from.
    """
    chunks: list[Chunk] = []
    buf_text: list[str] = []
    buf_start: float | None = None
    buf_end: float = 0.0
    buf_len = 0

    def flush():
        nonlocal buf_text, buf_start, buf_end, buf_len
        if buf_text:
            chunks.append(
                Chunk(
                    chunk_id=len(chunks),
                    start_s=buf_start or 0.0,
                    end_s=buf_end,
                    text=" ".join(buf_text).strip(),
                )
            )
        buf_text = []
        buf_start = None
        buf_len = 0

    for snip in snippets:
        text = snip.text.strip()
        if not text:
            continue
        if buf_start is None:
            buf_start = snip.start
        buf_text.append(text)
        buf_end = snip.start + snip.duration
        buf_len += len(text) + 1
        if buf_len >= target_chars:
            flush()
    flush()

    return chunks


def chunk_text(text: str, target_chars: int = TARGET_CHARS) -> list[Chunk]:
    """Greedily merge sentences into ~target_chars chunks for untimed sources
    (e.g. PubMed abstracts), which have no timestamp span to preserve.

    Most abstracts are well under target_chars and come back as a single
    chunk; longer text (e.g. a future full-text source) still gets split.
    """
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]

    chunks: list[Chunk] = []
    buf: list[str] = []
    buf_len = 0

    def flush():
        nonlocal buf, buf_len
        if buf:
            chunks.append(
                Chunk(
                    chunk_id=len(chunks),
                    start_s=None,
                    end_s=None,
                    text=" ".join(buf).strip(),
                )
            )
        buf = []
        buf_len = 0

    for sentence in sentences:
        buf.append(sentence)
        buf_len += len(sentence) + 1
        if buf_len >= target_chars:
            flush()
    flush()

    return chunks
