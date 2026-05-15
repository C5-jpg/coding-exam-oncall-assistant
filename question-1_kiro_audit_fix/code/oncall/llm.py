"""Zhipu GLM-4.6 chat client (GLM Coding Plan endpoint).

The Coding Plan REQUIRES `/api/coding/paas/v4` rather than the regular endpoint.
This client is OpenAI-compatible (chat.completions + tool calling).
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Iterable

import requests

from .config import SETTINGS

log = logging.getLogger("oncall.llm")


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(
        self,
        api_base: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
        max_retries: int = 2,
    ) -> None:
        self.api_base = (api_base or SETTINGS.llm_api_base).rstrip("/")
        self.api_key = api_key or SETTINGS.llm_api_key
        self.model = model or SETTINGS.llm_model
        self.timeout = timeout
        self.max_retries = max_retries

    def has_api(self) -> bool:
        return bool(self.api_key) and not self.api_key.startswith("your-")

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] = "auto",
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> dict[str, Any]:
        """Send a chat completion. Returns the raw choices[0].message dict."""
        if not self.has_api():
            raise LLMError("LLM_API_KEY is not configured. Set it in .env")
        url = f"{self.api_base}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=self.timeout,
                )
                if resp.status_code >= 500:
                    raise LLMError(f"upstream {resp.status_code}: {resp.text[:300]}")
                if resp.status_code == 429:
                    time.sleep(2 ** attempt)
                    raise LLMError("rate limited")
                if not resp.ok:
                    raise LLMError(f"HTTP {resp.status_code}: {resp.text[:300]}")
                data = resp.json()
                if "choices" not in data or not data["choices"]:
                    raise LLMError(f"empty response: {data}")
                return data["choices"][0]["message"]
            except (requests.RequestException, LLMError) as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise
        raise last_exc  # type: ignore[misc]
