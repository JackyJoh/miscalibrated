"""
app/services/llm_service.py — Abstracted LLM service layer.

This wraps both Anthropic (Claude) and OpenAI behind a single interface.
The active provider is set by the LLM_PROVIDER environment variable.
To switch providers, change one env var — no code changes needed.

Pattern: Program to an interface, not an implementation.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from app.config import settings


# ─── Abstract Interface ───────────────────────────────────────────────────────
# Any provider must implement this interface. This ensures that
# the agent logic is completely decoupled from the specific LLM API.
class BaseLLMProvider(ABC):

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Yield text chunks as they stream from the LLM."""
        ...

    @abstractmethod
    async def complete(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> str:
        """Return a full completion (non-streaming)."""
        ...


# ─── Anthropic (Claude) Provider ─────────────────────────────────────────────
class AnthropicProvider(BaseLLMProvider):

    def __init__(self):
        # Import here to avoid loading the SDK if we're using OpenAI
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-6"

    async def stream_chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a response from Claude."""
        # TODO: Implement streaming with tool use for agent actions
        kwargs = {"model": self.model, "max_tokens": 4096, "messages": messages}
        if system_prompt:
            kwargs["system"] = system_prompt

        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    async def complete(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> str:
        """Get a full response from Claude (non-streaming)."""
        # TODO: Implement with tool use
        kwargs = {"model": self.model, "max_tokens": 4096, "messages": messages}
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self.client.messages.create(**kwargs)
        return response.content[0].text


# ─── OpenAI Provider ─────────────────────────────────────────────────────────
class OpenAIProvider(BaseLLMProvider):

    def __init__(self):
        import openai
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"

    async def stream_chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a response from OpenAI."""
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(messages)

        stream = await self.client.chat.completions.create(
            model=self.model, messages=msgs, stream=True
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def complete(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> str:
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(messages)

        response = await self.client.chat.completions.create(
            model=self.model, messages=msgs
        )
        return response.choices[0].message.content


# ─── Service Factory ─────────────────────────────────────────────────────────
class LLMService:
    """
    Public interface used throughout the app.
    Instantiate this class wherever you need an LLM — it picks the
    right provider automatically based on settings.llm_provider.
    """

    def __init__(self):
        provider = settings.llm_provider.lower()
        if provider == "anthropic":
            self._provider = AnthropicProvider()
        elif provider == "openai":
            self._provider = OpenAIProvider()
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}. Use 'anthropic' or 'openai'.")

    async def stream_chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        return self._provider.stream_chat(messages, system_prompt)

    async def complete(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> str:
        return await self._provider.complete(messages, system_prompt)
