import json
import logging
from typing import AsyncIterator

import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str,
        max_tokens: int,
        timeout: int,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._max_tokens = max_tokens
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=httpx.Timeout(timeout, connect=10),
        )

    async def stream(self, messages: list[dict]) -> AsyncIterator[str]:
        payload = {
            "model": self._model,
            "stream": True,
            "max_tokens": self._max_tokens,
            "messages": messages,
        }
        async with self._client.stream("POST", "/chat/completions", json=payload) as resp:
            if resp.status_code >= 400:
                detail = await resp.aread()
                raise RuntimeError(f"upstream {resp.status_code}: {detail!r}")
            async for raw in resp.aiter_lines():
                if not raw:
                    continue
                if not raw.startswith("data:"):
                    continue
                data = raw[len("data:"):].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    logger.warning("bad upstream chunk: %s", data)
                    continue
                choices = obj.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                content = delta.get("content")
                if content:
                    yield content

    async def aclose(self) -> None:
        await self._client.aclose()
