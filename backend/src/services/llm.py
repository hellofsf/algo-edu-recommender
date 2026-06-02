"""LLM service using DeepSeek API."""

import httpx
from typing import Any

from src.config import get_settings

settings = get_settings()

_deepseek_base_url = "https://api.deepseek.com/v1"


class LLMService:
    """Service for LLM interactions with DeepSeek API."""

    def __init__(self):
        self.base_url = _deepseek_base_url
        self.api_key = settings.deepseek_api_key if hasattr(settings, "deepseek_api_key") else None
        self.model = getattr(settings, "deepseek_model", "deepseek-chat")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(60.0, connect=10.0),
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send a chat completion request to DeepSeek.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            temperature: Sampling temperature (0.0-2.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            Generated text response.
        """
        if not self.api_key:
            raise RuntimeError("DeepSeek API key not configured")

        client = await self._get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = await client.post("/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def embedding(self, texts: list[str]) -> list[list[float]]:
        """
        Get text embeddings from DeepSeek.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors.
        """
        if not self.api_key:
            raise RuntimeError("DeepSeek API key not configured")

        embedding_model = getattr(settings, "deepseek_embedding_model", "deepseek-text-embedding")
        client = await self._get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": embedding_model,
            "input": texts,
        }

        response = await client.post(
            "/embeddings", json=payload, headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    async def health_check(self) -> bool:
        """Check if DeepSeek API is accessible."""
        if not self.api_key:
            return False
        try:
            client = await self._get_client()
            headers = {"Authorization": f"Bearer {self.api_key}"}
            # Lightweight models list check
            response = await client.get("/models", headers=headers)
            return response.status_code == 200
        except Exception:
            return False
