from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import httpx


class OllamaClient:
    def __init__(self, base_url: str, timeout_seconds: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout_seconds, connect=10.0)

    async def request(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str],
        body: bytes,
        query: str,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{query}"
        clean_headers = {
            k: v for k, v in headers.items()
            if k.lower() not in {"host", "content-length"}
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.request(method, url, headers=clean_headers, content=body)

    async def stream(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str],
        body: bytes,
        query: str,
    ) -> tuple[int, dict[str, str], AsyncIterator[bytes]]:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{query}"
        clean_headers = {
            k: v for k, v in headers.items()
            if k.lower() not in {"host", "content-length"}
        }
        client = httpx.AsyncClient(timeout=self.timeout)
        request = client.build_request(method, url, headers=clean_headers, content=body)
        response = await client.send(request, stream=True)

        async def iterator() -> AsyncIterator[bytes]:
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
            finally:
                await response.aclose()
                await client.aclose()

        return response.status_code, dict(response.headers), iterator()
