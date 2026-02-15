"""
myAgentAI - OpenAI Service
============================
Shared async service for chat completions and embeddings.
Used by all utilities that need LLM or embedding capabilities.
"""

from typing import List, Dict, Optional
from openai import AsyncOpenAI
from app.core.config import get_settings

settings = get_settings()


class OpenAIService:
    """Async wrapper for OpenAI API operations."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = settings.OPENAI_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Send a chat completion request and return the assistant message."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def create_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text."""
        response = await self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
        return response.data[0].embedding
