"""Thin wrapper around the Anthropic Messages API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import anthropic

DEFAULT_MODEL = "claude-opus-5"
DEFAULT_MAX_TOKENS = 4096


class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...


@dataclass
class AnthropicClient:
    model: str = DEFAULT_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS

    def __post_init__(self) -> None:
        self._client = anthropic.Anthropic()

    def complete(self, system: str, user: str) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return next(b.text for b in response.content if b.type == "text")
